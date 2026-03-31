"""Run management — start, list, inspect, cancel pipeline runs.

This module NEVER modifies existing orchestrator code. It:
- Starts pipeline_orchestrator.py as a subprocess
- Scans artifacts/runs/ for existing run directories
- Reads run_manifest.json (read-only)
- Sends SIGTERM to cancel a running subprocess
"""

from __future__ import annotations

import json
import re
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel

SERVER_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SERVER_DIR.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pipeline_contracts import section_artifact_stem

RUNS_DIR = PROJECT_ROOT / "artifacts" / "runs"
CONFIGS_DIR = PROJECT_ROOT / "configs"
UNIT_CONFIGS_DIR = CONFIGS_DIR / "units"
TEXTBOOKS_DIR = PROJECT_ROOT / "textbook"
CURRICULUMS_DIR = PROJECT_ROOT / "curriculum"
ORCHESTRATOR_SCRIPT = SCRIPTS_DIR / "pipeline_orchestrator.py"

router = APIRouter()

# In-memory tracking of active subprocess PIDs
_active_runs: dict[str, subprocess.Popen] = {}

ACCENTS = [
    ["#6366f1", "#818cf8"],
    ["#4f46e5", "#7c3aed"],
    ["#0f766e", "#14b8a6"],
    ["#1d4ed8", "#3b82f6"],
    ["#d97706", "#f59e0b"],
    ["#9333ea", "#c084fc"],
]


import unicodedata

# ---------------------------------------------------------------------------
# Textbooks endpoint — scan textbook/ folder
# ---------------------------------------------------------------------------
@router.get("/textbooks")
async def list_textbooks():
    """List textbook PDFs grouped by subject for manual page selection."""
    if not TEXTBOOKS_DIR.exists():
        return []
    subjects = []
    for subdir in sorted(TEXTBOOKS_DIR.iterdir()):
        if not subdir.is_dir() or subdir.name.startswith("."):
            continue
        pdfs = []
        for pdf in sorted(subdir.glob("*.pdf")):
            name_nfc = unicodedata.normalize('NFC', pdf.name)
            is_chart = "진도표" in name_nfc or "progress" in name_nfc.lower()
            if is_chart:
                continue
            pdfs.append({
                "filename": name_nfc,
                "path": str(pdf),
                "relative_path": f"textbook/{subdir.name}/{pdf.name}",
            })
        if pdfs:
            subjects.append({
                "subject": unicodedata.normalize('NFC', subdir.name),
                "pdfs": pdfs,
            })
    return subjects


@router.get("/curriculums")
async def list_curriculums():
    """List national curriculum PDFs found in curriculum/ or textbook/."""
    search_dirs = [CURRICULUMS_DIR, TEXTBOOKS_DIR]
    curriculums = []
    
    for sdir in search_dirs:
        if not sdir.exists():
            continue
        # Search recursively for PDFs
        for pdf in sorted(sdir.glob("**/*.pdf")):
            name_nfc = unicodedata.normalize('NFC', pdf.name)
            # Identify by name or parent directory or just if it's in CURRICULUMS_DIR
            is_curriculum = sdir == CURRICULUMS_DIR or "교육과정" in name_nfc or "curriculum" in str(pdf).lower()
            if is_curriculum:
                try:
                    rel_path = pdf.relative_to(PROJECT_ROOT)
                    curriculums.append({
                        "filename": name_nfc,
                        "path": str(pdf),
                        "relative_path": str(rel_path),
                    })
                except Exception:
                    continue
    return curriculums


def _subject_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value).strip().lower()
    normalized = re.sub(r"[^0-9A-Za-z가-힣]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "config"


class ManualLessonRequest(BaseModel):
    sheet_name: str
    title: str
    pdf_pages: list[int]


class CreateConfigFromPageMapRequest(BaseModel):
    subject: str
    pdf_path: str
    unit_title: str
    output_filename: str
    footer: str
    lessons: list[ManualLessonRequest]
    template_path: str = "빈 넘버스 파일.numbers"


class ValidatePageMapRequest(BaseModel):
    lessons: list[ManualLessonRequest]


@router.post("/validate-page-map")
async def validate_page_map(req: ValidatePageMapRequest):
    """Validate teacher-confirmed lesson/page mappings."""
    warnings: list[str] = []
    blocking_issues: list[str] = []
    page_owners: dict[int, str] = {}

    for lesson in req.lessons:
        if not lesson.pdf_pages:
            blocking_issues.append(f"{lesson.sheet_name}: at least one page must be selected")
            continue
        normalized_pages = sorted(set(lesson.pdf_pages))
        if len(normalized_pages) != len(lesson.pdf_pages):
            warnings.append(f"{lesson.sheet_name}: duplicate pages were normalized")
        for page_num in normalized_pages:
            if page_num < 1:
                blocking_issues.append(f"{lesson.sheet_name}: page number must be >= 1")
                continue
            previous_owner = page_owners.get(page_num)
            if previous_owner and previous_owner != lesson.sheet_name:
                blocking_issues.append(
                    f"{lesson.sheet_name}: page {page_num} overlaps with {previous_owner}"
                )
            page_owners[page_num] = lesson.sheet_name

    return {
        "ok": len(blocking_issues) == 0,
        "warnings": warnings,
        "blocking_issues": blocking_issues,
    }


class PdfMetadataRequest(BaseModel):
    pdf_path: str


@router.post("/pdf-metadata")
async def get_pdf_metadata(req: PdfMetadataRequest):
    """Return lightweight PDF metadata for manual page selection."""
    import fitz

    pdf_path = Path(req.pdf_path)
    if not pdf_path.is_absolute():
        pdf_path = (PROJECT_ROOT / pdf_path).resolve()
    else:
        pdf_path = pdf_path.resolve()

    if not pdf_path.exists():
        raise HTTPException(404, f"PDF not found: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        try:
            return {
                "pdf_path": str(pdf_path),
                "page_count": doc.page_count,
                "filename": pdf_path.name,
            }
        finally:
            doc.close()
    except Exception as exc:
        raise HTTPException(500, f"Failed to read PDF metadata: {exc}") from exc


@router.get("/pdf-page-image")
async def get_pdf_page_image(
    pdf_path: str = Query(...),
    page: int = Query(..., ge=1),
    width: int = Query(180, ge=60, le=600),
):
    """Render a single PDF page thumbnail as PNG."""
    import fitz

    resolved_path = Path(pdf_path)
    if not resolved_path.is_absolute():
        resolved_path = (PROJECT_ROOT / resolved_path).resolve()
    else:
        resolved_path = resolved_path.resolve()

    if not resolved_path.exists():
        raise HTTPException(404, f"PDF not found: {resolved_path}")

    try:
        doc = fitz.open(resolved_path)
        try:
            if page > doc.page_count:
                # Return empty page or 400 instead of 404 to avoid confusing generic 404s
                raise HTTPException(400, f"Page {page} out of range (max {doc.page_count})")
            pdf_page = doc.load_page(page - 1)
            rect = pdf_page.rect
            scale = max(width / max(rect.width, 1), 0.1)
            pix = pdf_page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            return Response(content=pix.tobytes("png"), media_type="image/png")
        finally:
            doc.close()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Failed to render page image: {exc}") from exc


@router.post("/create-config-from-page-map")
async def create_config_from_page_map(req: CreateConfigFromPageMapRequest):
    """Create a final config from teacher-confirmed lesson/page mappings."""
    if not req.lessons:
        raise HTTPException(400, "At least one lesson is required")

    sections = []
    slug = _subject_slug(req.subject)
    for i, lesson in enumerate(req.lessons):
        pdf_pages = sorted(set(lesson.pdf_pages))
        if not pdf_pages:
            raise HTTPException(400, f"{lesson.sheet_name}: at least one page must be selected")
        if any(page_num < 1 for page_num in pdf_pages):
            raise HTTPException(400, f"{lesson.sheet_name}: page number must be >= 1")
        card_file = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", f"{slug}_{lesson.sheet_name}")
        section = {
            "sheet_name": lesson.sheet_name,
            "card_file": card_file,
            "title": lesson.title,
            "badge": lesson.sheet_name,
            "accent": ACCENTS[i % len(ACCENTS)],
            "pdf_pages": pdf_pages,
        }
        section["lesson_id"] = section_artifact_stem(section)
        sections.append(section)

    config_name = _subject_slug(f"{slug}_{req.unit_title[:40]}")
    config_dir = UNIT_CONFIGS_DIR / slug
    config_path = config_dir / f"{config_name}.json"
    config_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "project_root": str(PROJECT_ROOT),
        "pdf_path": req.pdf_path,
        "template_path": req.template_path,
        "output_file": req.output_filename,
        "footer": req.footer,
        "sections": sections,
    }
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "config_path": str(config_path),
        "config_name": config_name,
        "sections_count": len(sections),
    }


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class StartRunRequest(BaseModel):
    config_path: str
    workflow_mode: str = "stable"
    gemini_model: str | None = None
    max_workers: int | None = None
    keep_run_artifacts: bool = True
    stop_after: str | None = None
    curriculum_pdf: str | None = None


class StartRunResponse(BaseModel):
    run_id: str
    run_root: str


class RunSummary(BaseModel):
    run_id: str
    started_at: str | None = None
    finished_at: str | None = None
    final_status: str = "pending"
    workflow_mode: str | None = None
    selected_unit: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _read_manifest(run_dir: Path) -> dict[str, Any] | None:
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.exists():
        return None
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _run_dirs() -> list[Path]:
    if not RUNS_DIR.exists():
        return []
    return sorted(
        [d for d in RUNS_DIR.iterdir() if d.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/runs", response_model=StartRunResponse)
async def start_run(req: StartRunRequest):
    """Start a new pipeline run as a subprocess."""
    config = Path(req.config_path).resolve()
    if not config.exists():
        raise HTTPException(404, f"Config not found: {config}")

    cmd = [
        sys.executable,
        str(ORCHESTRATOR_SCRIPT),
        "--config", str(config),
        "--workflow-mode", req.workflow_mode,
    ]
    if req.max_workers is not None and req.max_workers > 0:
        cmd.extend(["--max-workers", str(req.max_workers)])
    if req.gemini_model:
        cmd.extend(["--gemini-model", req.gemini_model])
    if req.keep_run_artifacts:
        cmd.append("--keep-run-artifacts")
    if req.stop_after:
        cmd.extend(["--stop-after", req.stop_after])
    if req.curriculum_pdf:
        cmd.extend(["--curriculum-pdf", req.curriculum_pdf])

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(PROJECT_ROOT),
    )

    # The orchestrator prints run_root as its first stdout line
    first_line = proc.stdout.readline().decode("utf-8").strip() if proc.stdout else ""
    if not first_line:
        raise HTTPException(500, "Orchestrator did not emit run_root")

    run_root = Path(first_line)
    run_id = run_root.name
    _active_runs[run_id] = proc

    return StartRunResponse(run_id=run_id, run_root=str(run_root))


@router.get("/runs")
async def list_runs() -> list[RunSummary]:
    """List all known runs (most recent first)."""
    results: list[RunSummary] = []
    for run_dir in _run_dirs():
        manifest = _read_manifest(run_dir)
        if manifest:
            results.append(
                RunSummary(
                    run_id=manifest.get("run_id", run_dir.name),
                    started_at=manifest.get("started_at"),
                    finished_at=manifest.get("finished_at"),
                    final_status=manifest.get("final_status", "pending"),
                    workflow_mode=manifest.get("workflow_mode"),
                    selected_unit=manifest.get("selected_unit"),
                )
            )
    return results


@router.get("/runs/{run_id}")
async def get_run(run_id: str) -> dict[str, Any]:
    """Get full run manifest."""
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        raise HTTPException(404, f"Run not found: {run_id}")
    manifest = _read_manifest(run_dir)
    if not manifest:
        raise HTTPException(404, f"Manifest not found for run: {run_id}")
    return manifest


@router.get("/runs/{run_id}/job-graph")
async def get_job_graph(run_id: str) -> dict[str, Any]:
    """Get the lesson-level job graph for a run."""
    run_dir = RUNS_DIR / run_id
    job_graph_path = run_dir / "job_graph.json"
    if not job_graph_path.exists():
        return {"jobs": [], "schema_version": "1.0.0", "run_id": run_id}
    try:
        return json.loads(job_graph_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"jobs": [], "schema_version": "1.0.0", "run_id": run_id}


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str):
    """Cancel a running pipeline subprocess."""
    proc = _active_runs.get(run_id)
    if proc is None:
        raise HTTPException(404, f"No active process for run: {run_id}")
    if proc.poll() is not None:
        return {"cancelled": False, "reason": "already_finished", "returncode": proc.returncode}
    proc.send_signal(signal.SIGTERM)
    return {"cancelled": True, "run_id": run_id}


async def _delete_run_impl(run_id: str):
    """Delete a run directory and forget any tracked subprocess."""
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        raise HTTPException(404, f"Run not found: {run_id}")

    proc = _active_runs.get(run_id)
    if proc is not None:
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        _active_runs.pop(run_id, None)

    shutil.rmtree(run_dir)
    return {"deleted": True, "run_id": run_id}


@router.delete("/runs/{run_id}")
async def delete_run(run_id: str):
    return await _delete_run_impl(run_id)


@router.post("/runs/{run_id}/delete")
async def delete_run_post(run_id: str):
    return await _delete_run_impl(run_id)
