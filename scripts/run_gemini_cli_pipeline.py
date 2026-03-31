import argparse
import asyncio
import concurrent.futures
import json
import os
import re
import selectors
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import fitz


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import draft_config_from_progress_chart as chart_draft  # noqa: E402
import agent_runtime  # noqa: E402
import generate_activity_plan as activity_plan_builder  # noqa: E402
import generate_lesson_analysis as lesson_analysis_builder  # noqa: E402
import generate_numbers_lesson as textbook  # noqa: E402
import generate_numbers_with_activities as numbers_with_activities  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402


PROMPTS_DIR = PROJECT_ROOT / "prompts" / "gemini"
WORKSPACE_PROMPT_DIR = PROJECT_ROOT / "artifacts" / "_gemini_prompts"
PROMPT_CACHE: dict[str, str] = {}
TEXT_CACHE: dict[Path, str] = {}
SCHEMA_CACHE: dict[Path, dict] = {}
LAST_ARTIFACT_ROOT: Path | None = None
LESSON_CONTEXT_TEXT_LIMIT = 3000
EARLY_ABORT_PATTERNS = (
    "exhausted your capacity on this model",
    "quota will reset after",
    "rate limit exceeded",
)
ACTIVITY_PLAN_EXAMPLE = {
    "schema_version": "1.0.0",
    "generated_at": "2026-01-01T00:00:00+00:00",
    "lesson_id": "2차시",
    "activities": [
        {
            "activity_id": "act-2-1",
            "lesson_id": "2차시",
            "object_role": "activity_area",
            "lesson_flow_stage": "during",
            "activity_type": "freeform_html",
            "level": "core",
            "learning_goal": "핵심 개념을 새로운 상황에 적용해 설명할 수 있다.",
            "prompt_text": "새로운 사례를 보고 핵심 개념이 왜 필요한지 설명해 봅시다.",
            "layout_template": "freeform_html",
            "html_content": "<!DOCTYPE html><html lang='ko'><head><meta charset='UTF-8'><style>body{width:1600px;background:transparent;font-family:\"Noto Sans KR\",sans-serif;}.card{background:#fff;padding:32px;border-radius:24px;}.writing{background:#fff;border:2px solid #333;min-height:520px;border-radius:16px;}</style></head><body><div class='card'><h1>활동 제목</h1><div class='writing'></div></div></body></html>",
            "source_refs": [56, 57],
            "teacher_notes": "",
            "student_writing_zones": [
                {
                    "zone_id": "main_response",
                    "label": "핵심 생각 쓰기",
                    "input_area_type": "free-writing",
                    "min_height": 520,
                }
            ],
            "estimated_minutes": 12,
            "review_status": "draft",
        }
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to textbook config JSON")
    parser.add_argument("--pdf", help="Optional override for textbook PDF path")
    parser.add_argument("--chart", help="Optional progress chart image path")
    parser.add_argument("--gemini-bin", default="gemini", help="Gemini CLI binary path")
    parser.add_argument("--gemini-model", help="Gemini model name")
    parser.add_argument(
        "--gemini-extensions",
        nargs="*",
        default=["stitch-skills"],
        help="Gemini extensions to enable for headless runs",
    )
    parser.add_argument("--output-root", help="Artifact root directory")
    parser.add_argument("--approval-mode", default="yolo", help="Gemini CLI approval mode")
    parser.add_argument("--max-workers", type=int, default=2, help="Max concurrent lesson workers for Gemini stages")
    parser.add_argument("--keep-artifacts", action="store_true", help="Keep generated assets from downstream renderer")
    parser.add_argument("--debug-artifacts", action="store_true", help="Keep Gemini prompt/raw/wrapper debug artifacts")
    parser.add_argument("--gemini-timeout-sec", type=int, default=120, help="Timeout for each Gemini CLI call")
    parser.add_argument("--dry-run", action="store_true", help="Stop after AI JSON generation")
    parser.add_argument(
        "--include-status",
        nargs="*",
        default=["draft", "reviewed", "approved"],
        help="review_status values to render when building Numbers output",
    )
    parser.add_argument(
        "--textbook-only-fallback",
        action="store_true",
        help="If Gemini stages fail completely, produce textbook-only output",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def sanitize_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in "-_." else "_" for char in value)


def read_text(path: Path) -> str:
    cached = TEXT_CACHE.get(path)
    if cached is None:
        cached = path.read_text(encoding="utf-8")
        TEXT_CACHE[path] = cached
    return cached


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_prompt(name: str) -> str:
    cached = PROMPT_CACHE.get(name)
    if cached is None:
        cached = read_text(PROMPTS_DIR / name)
        PROMPT_CACHE[name] = cached
    return cached


def extract_last_json_object(text: str) -> dict:
    lines = text.splitlines()
    candidates = []
    for index, line in enumerate(lines):
        if line.strip().startswith("{"):
            candidates.append(index)
    for index in reversed(candidates):
        chunk = "\n".join(lines[index:]).strip()
        try:
            parsed = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("Could not find trailing JSON object in Gemini CLI output")


def extract_json_code_fence(text: str) -> dict | None:
    patterns = [
        r"```json\s*(\{.*?\})\s*```",
        r"```\s*(\{.*?\})\s*```",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.DOTALL | re.IGNORECASE)
        for candidate in reversed(matches):
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return None


def extract_any_json_object(text: str) -> dict:
    fenced = extract_json_code_fence(text)
    if fenced is not None:
        return fenced

    starts = [index for index, char in enumerate(text) if char == "{"]  # nosec B105
    decoder = json.JSONDecoder()
    for start in starts:
        try:
            parsed, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("Could not find any JSON object in Gemini CLI output")


def extract_json_from_response_text(text: str) -> dict:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        try:
            parsed = extract_last_json_object(text)
        except ValueError:
            parsed = extract_any_json_object(text)
    if isinstance(parsed, dict) and isinstance(parsed.get("response"), str):
        response_text = parsed.get("response", "").strip()
        if response_text:
            try:
                nested = json.loads(response_text)
            except json.JSONDecodeError:
                try:
                    nested = extract_last_json_object(response_text)
                except ValueError:
                    nested = extract_any_json_object(response_text)
            if isinstance(nested, dict):
                parsed = nested
    if not isinstance(parsed, dict):
        raise ValueError("Gemini response did not contain a JSON object")
    return parsed


def classify_gemini_failure(exc: Exception) -> tuple[str, str]:
    message = str(exc).strip()
    lowered = message.lower()
    if "aborterror" in lowered or "the user aborted a request" in lowered:
        return "aborted", message
    if "timed out" in lowered:
        return "timeout", message
    if "capacity/rate-limit condition" in lowered:
        return "capacity_or_rate_limit", message
    if "exhausted your capacity" in lowered or "quota will reset after" in lowered or "rate limit exceeded" in lowered:
        return "capacity_or_rate_limit", message
    if "did not contain a json object" in lowered or "could not find any json object" in lowered:
        return "invalid_json", message
    if "json" in lowered:
        return "invalid_json", message
    if "field" in lowered or "schema" in lowered or "validation" in lowered:
        return "validation_error", message
    return "unknown", message


def invoke_gemini_json(
    prompt: str,
    artifact_dir: Path,
    stem: str,
    gemini_bin: str,
    gemini_model: str | None,
    gemini_extensions: list[str],
    approval_mode: str,
    debug_artifacts: bool,
    timeout_sec: int | None,
    idle_timeout_sec: int | None = None,
) -> tuple[dict, str]:
    if timeout_sec is not None and timeout_sec <= 0:
        timeout_sec = None
    if idle_timeout_sec is not None and idle_timeout_sec <= 0:
        idle_timeout_sec = None
    command = [gemini_bin, "-o", "json", "--approval-mode", approval_mode]
    if gemini_model:
        command.extend(["-m", gemini_model])
    for extension_name in gemini_extensions:
        command.extend(["-e", extension_name])
    if debug_artifacts:
        WORKSPACE_PROMPT_DIR.mkdir(parents=True, exist_ok=True)
        prompt_path = WORKSPACE_PROMPT_DIR / f"{sanitize_name(artifact_dir.name)}-{stem}.md"
        prompt_path.write_text(prompt, encoding="utf-8")
    command.extend(["-p", prompt])

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        stdout_chunks: list[bytes] = []
        stderr_chunks: list[bytes] = []
        selector = selectors.DefaultSelector()
        if process.stdout is not None:
            selector.register(process.stdout, selectors.EVENT_READ)
        if process.stderr is not None:
            selector.register(process.stderr, selectors.EVENT_READ)
        deadline = None if timeout_sec is None else time.monotonic() + timeout_sec
        last_activity_at = time.monotonic()
        try:
            while selector.get_map():
                if deadline is None:
                    events = selector.select(timeout=0.5)
                else:
                    remaining = max(0.0, deadline - time.monotonic())
                    if remaining == 0:
                        raise subprocess.TimeoutExpired(command, timeout_sec)
                    events = selector.select(timeout=min(0.5, remaining))
                if idle_timeout_sec is not None and (time.monotonic() - last_activity_at) >= idle_timeout_sec:
                    raise RuntimeError(f"Gemini CLI idle timeout after {idle_timeout_sec} seconds for {stem}")
                if not events and process.poll() is not None:
                    break
                for key, _ in events:
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    last_activity_at = time.monotonic()
                    if key.fileobj is process.stdout:
                        stdout_chunks.append(chunk)
                    else:
                        stderr_chunks.append(chunk)
                        stderr_text = b"".join(stderr_chunks).decode("utf-8", errors="replace").lower()
                        if any(pattern in stderr_text for pattern in EARLY_ABORT_PATTERNS):
                            raise RuntimeError("Gemini CLI capacity/rate-limit condition detected")
            process.wait(timeout=1)
            stdout = b"".join(stdout_chunks).decode("utf-8", errors="replace")
            stderr = b"".join(stderr_chunks).decode("utf-8", errors="replace")
        except subprocess.TimeoutExpired as exc:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            stdout = b"".join(stdout_chunks).decode("utf-8", errors="replace")
            stderr = b"".join(stderr_chunks).decode("utf-8", errors="replace")
            if debug_artifacts and stdout:
                (artifact_dir / f"{stem}.stdout.txt").write_text(stdout, encoding="utf-8")
            (artifact_dir / f"{stem}.stderr.txt").write_text(
                ((stderr or "") + f"\n\nTimed out after {timeout_sec} seconds.").strip() + "\n",
                encoding="utf-8",
            )
            raise TimeoutError(f"Gemini CLI timed out after {timeout_sec} seconds for {stem}") from exc
        except RuntimeError as exc:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            stdout = b"".join(stdout_chunks).decode("utf-8", errors="replace")
            stderr = b"".join(stderr_chunks).decode("utf-8", errors="replace")
            if debug_artifacts and stdout:
                (artifact_dir / f"{stem}.stdout.txt").write_text(stdout, encoding="utf-8")
            (artifact_dir / f"{stem}.stderr.txt").write_text(stderr or "", encoding="utf-8")
            message = str(exc)
            if "idle timeout" in message.lower():
                raise RuntimeError(message) from exc
            raise RuntimeError(f"Gemini CLI aborted early for {stem}: capacity/rate-limit condition") from exc
        finally:
            selector.close()

        if process.returncode != 0:
            if debug_artifacts and stdout:
                (artifact_dir / f"{stem}.stdout.txt").write_text(stdout, encoding="utf-8")
            (artifact_dir / f"{stem}.stderr.txt").write_text(stderr or "", encoding="utf-8")
            raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)
    except subprocess.CalledProcessError as exc:
        if debug_artifacts:
            (artifact_dir / f"{stem}.stdout.txt").write_text(exc.stdout or "", encoding="utf-8")
        (artifact_dir / f"{stem}.stderr.txt").write_text(exc.stderr or "", encoding="utf-8")
        raise

    raw_output = stdout
    stderr_path = artifact_dir / f"{stem}.stderr.txt"
    stderr_path.write_text(stderr or "", encoding="utf-8")

    try:
        wrapper = extract_last_json_object(raw_output)
    except ValueError:
        wrapper = extract_any_json_object(raw_output)
    response_text = wrapper.get("response", "")
    parsed = extract_json_from_response_text(response_text)
    if debug_artifacts:
        raw_path = artifact_dir / f"{stem}.raw.txt"
        raw_path.write_text(raw_output, encoding="utf-8")
        wrapper_path = artifact_dir / f"{stem}.wrapper.json"
        write_json(wrapper_path, wrapper)
        parsed_path = artifact_dir / f"{stem}.response.json"
        write_json(parsed_path, parsed)
    return parsed, raw_output


def load_schema(path: Path) -> dict:
    cached = SCHEMA_CACHE.get(path)
    if cached is None:
        cached = json.loads(read_text(path))
        SCHEMA_CACHE[path] = cached
    return cached


def ensure_required_fields(payload: dict, required_fields: list[str], label: str) -> None:
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise ValueError(f"{label} missing required fields: {', '.join(missing)}")


def validate_lesson_analysis(payload: dict) -> None:
    schema = load_schema(PROJECT_ROOT / "schemas" / "lesson_analysis.schema.json")
    ensure_required_fields(payload, schema["required"], "lesson_analysis")
    if not isinstance(payload.get("content_chunks"), list) or not payload["content_chunks"]:
        raise ValueError("lesson_analysis.content_chunks must be a non-empty list")


def validate_activity_plan(payload: dict) -> None:
    schema = load_schema(PROJECT_ROOT / "schemas" / "activity_plan.schema.json")
    ensure_required_fields(payload, schema["required"], "activity_plan")
    if not isinstance(payload.get("activities"), list) or not payload["activities"]:
        raise ValueError("activity_plan.activities must be a non-empty list")
    activity_required = schema["properties"]["activities"]["items"]["required"]
    for index, activity in enumerate(payload["activities"], start=1):
        ensure_required_fields(activity, activity_required, f"activity[{index}]")
        if activity.get("activity_type") == "freeform_html" and not activity.get("html_content"):
            raise ValueError(f"activity[{index}] freeform_html requires html_content")
        validate_activity_metadata(activity, index)
        validate_activity_writing_zones(activity, index)
        if activity.get("activity_type") == "freeform_html":
            validate_freeform_html(activity, index)


def validate_activity_metadata(activity: dict, index: int) -> None:
    if activity.get("object_role") not in {
        "learning_note",
        "activity_area",
        "reference_material",
        "worksheet",
        "ai_courseware",
    }:
        raise ValueError(f"activity[{index}] has invalid object_role")
    if activity.get("lesson_flow_stage") not in {"before", "during", "after"}:
        raise ValueError(f"activity[{index}] has invalid lesson_flow_stage")


def validate_activity_writing_zones(activity: dict, index: int) -> None:
    zones = activity.get("student_writing_zones")
    if not isinstance(zones, list):
        raise ValueError(f"activity[{index}] student_writing_zones must be a list")
    if not zones:
        raise ValueError(f"activity[{index}] must describe at least one student_writing_zone")
    for zone_index, zone in enumerate(zones, start=1):
        required = {"zone_id", "label", "input_area_type", "min_height"}
        missing = sorted(required.difference(zone))
        if missing:
            raise ValueError(
                f"activity[{index}].student_writing_zones[{zone_index}] missing required fields: {', '.join(missing)}"
            )


def validate_freeform_html(activity: dict, index: int) -> None:
    html_content = activity.get("html_content", "")
    normalized_html = html_content.lower().replace(" ", "")
    if "<html" not in normalized_html or "<body" not in normalized_html:
        raise ValueError(f"activity[{index}] freeform_html must be a full standalone HTML document")
    if "1600px" not in normalized_html:
        raise ValueError(f"activity[{index}] freeform_html should target a 1600px-wide Numbers canvas")
    zone_heights = [
        int(zone.get("min_height", 0))
        for zone in activity.get("student_writing_zones", [])
        if str(zone.get("min_height", "")).isdigit() or isinstance(zone.get("min_height"), int)
    ]
    css_min_heights = [int(match) for match in re.findall(r"min-height\s*:\s*(\d+)px", html_content, flags=re.IGNORECASE)]
    tall_zone = max(zone_heights + css_min_heights, default=0)
    if tall_zone < 220:
        raise ValueError(f"activity[{index}] freeform_html must include a writing zone at least 220px tall")
    if activity.get("lesson_flow_stage") in {"during", "after"} and tall_zone < 420:
        raise ValueError(f"activity[{index}] {activity['lesson_flow_stage']} freeform_html needs a main writing zone of 420px+")


def build_schedule_draft(config: dict, chart_path: Path | None) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "sections": [
            {
                "sheet_name": section["sheet_name"],
                "lesson_title": section["title"],
                "title_query": section.get("title_query", section["title"]),
            }
            for section in config["sections"]
        ],
    }

    if chart_path:
        payload["chart_path"] = str(chart_path)
        try:
            swift_script = config["project_root"] / "scripts" / "ocr_progress_chart.swift"
            ocr_lines = chart_draft.run_ocr(swift_script, chart_path)
            filtered_lines = chart_draft.filter_lines(ocr_lines, None, None)
            parsed_sections = chart_draft.parse_sections(filtered_lines)
            payload["ocr_lines"] = [line["text"] for line in filtered_lines]
            payload["ocr_sections"] = parsed_sections
        except Exception as exc:
            payload["chart_error"] = str(exc)

    return payload


def build_textbook_context(config: dict, artifact_dir: Path) -> tuple[list[dict], list[Path]]:
    analyses: list[dict] = []
    analysis_paths: list[Path] = []
    context_sections = []
    doc = fitz.open(config["pdf_path"])
    try:
        for section in config["sections"]:
            analysis = lesson_analysis_builder.build_analysis(doc, section)
            analyses.append(analysis)

            section_key = contracts.section_artifact_stem(section)
            analysis_path = artifact_dir / "local_baseline" / f"{section_key}.lesson_analysis.json"
            write_json(analysis_path, analysis)
            analysis_paths.append(analysis_path)

            section_text = []
            for page in section["pdf_pages"]:
                section_text.append(doc[page - 1].get_text("text").strip())

            context_sections.append(
                {
                    "section_key": section_key,
                    "sheet_name": section["sheet_name"],
                    "lesson_title": section["title"],
                    "title_query": section.get("title_query", section["title"]),
                    "pdf_pages": section["pdf_pages"],
                    "baseline_analysis_path": str(analysis_path),
                    "extracted_text": "\n\n".join(section_text),
                }
            )
    finally:
        doc.close()

    context = {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "pdf_path": str(config["pdf_path"]),
        "sections": context_sections,
    }
    write_json(artifact_dir / "textbook_context.json", context)
    return analyses, analysis_paths


def build_section_prompt_context(textbook_context: dict, target_sheet_name: str) -> dict:
    sections = textbook_context["sections"]
    index = next(
        (position for position, item in enumerate(sections) if item["sheet_name"] == target_sheet_name),
        None,
    )
    if index is None:
        raise ValueError(f"Could not find section context for '{target_sheet_name}'")

    current = dict(sections[index])
    compact_current = {
        "sheet_name": current["sheet_name"],
        "lesson_title": current["lesson_title"],
        "title_query": current["title_query"],
        "pdf_pages": current["pdf_pages"],
        "baseline_analysis_path": current["baseline_analysis_path"],
        "extracted_text": current["extracted_text"],
    }

    neighbors = []
    for neighbor_index in (index - 1, index + 1):
        if 0 <= neighbor_index < len(sections):
            neighbor = sections[neighbor_index]
            neighbors.append(
                {
                    "relation": "previous" if neighbor_index < index else "next",
                    "sheet_name": neighbor["sheet_name"],
                    "lesson_title": neighbor["lesson_title"],
                    "title_query": neighbor["title_query"],
                    "pdf_pages": neighbor["pdf_pages"],
                }
            )

    return {
        "schema_version": textbook_context.get("schema_version", "1.0.0"),
        "generated_at": utc_now(),
        "pdf_path": textbook_context["pdf_path"],
        "current_section": compact_current,
        "neighbor_sections": neighbors,
    }


def build_section_prompt_context_by_key(textbook_context: dict, target_section_key: str) -> dict:
    sections = textbook_context["sections"]
    index = next(
        (position for position, item in enumerate(sections) if item.get("section_key") == target_section_key),
        None,
    )
    if index is None:
        raise ValueError(f"Could not find section context for '{target_section_key}'")

    current = dict(sections[index])
    compact_current = {
        "section_key": current["section_key"],
        "sheet_name": current["sheet_name"],
        "lesson_title": current["lesson_title"],
        "title_query": current["title_query"],
        "pdf_pages": current["pdf_pages"],
        "baseline_analysis_path": current["baseline_analysis_path"],
        "extracted_text": current["extracted_text"][:LESSON_CONTEXT_TEXT_LIMIT],
        "extracted_text_truncated": len(current["extracted_text"]) > LESSON_CONTEXT_TEXT_LIMIT,
    }

    neighbors = []
    for neighbor_index in (index - 1, index + 1):
        if 0 <= neighbor_index < len(sections):
            neighbor = sections[neighbor_index]
            neighbors.append(
                {
                    "relation": "previous" if neighbor_index < index else "next",
                    "section_key": neighbor.get("section_key"),
                    "sheet_name": neighbor["sheet_name"],
                    "lesson_title": neighbor["lesson_title"],
                    "title_query": neighbor["title_query"],
                    "pdf_pages": neighbor["pdf_pages"],
                }
            )

    return {
        "schema_version": textbook_context.get("schema_version", "1.0.0"),
        "generated_at": utc_now(),
        "pdf_path": textbook_context["pdf_path"],
        "current_section": compact_current,
        "neighbor_sections": neighbors,
    }


def compact_baseline_for_prompt(baseline_analysis: dict) -> dict:
    return {
        "lesson_id": baseline_analysis.get("lesson_id"),
        "sheet_name": baseline_analysis.get("sheet_name"),
        "lesson_title": baseline_analysis.get("lesson_title"),
        "lesson_type": baseline_analysis.get("lesson_type"),
        "pdf_pages": baseline_analysis.get("pdf_pages", []),
        "essential_question": baseline_analysis.get("essential_question"),
        "learning_goals": baseline_analysis.get("learning_goals", [])[:4],
        "key_concepts": baseline_analysis.get("key_concepts", [])[:6],
        "vocabulary": baseline_analysis.get("vocabulary", [])[:10],
        "misconceptions": baseline_analysis.get("misconceptions", [])[:6],
        "difficulty_band": baseline_analysis.get("difficulty_band"),
        "content_chunks": [
            {
                "chunk_id": chunk.get("chunk_id"),
                "label": chunk.get("label"),
                "knowledge_type": chunk.get("knowledge_type"),
                "summary": chunk.get("summary"),
                "source_pages": chunk.get("source_pages", []),
            }
            for chunk in baseline_analysis.get("content_chunks", [])[:5]
        ],
        "source_page_refs": baseline_analysis.get("source_page_refs", [])[:8],
        "analysis_confidence": baseline_analysis.get("analysis_confidence"),
        "notes": baseline_analysis.get("notes"),
    }


def compact_schedule_draft_for_prompt(schedule_draft: dict, section: dict) -> dict:
    entries = schedule_draft.get("sections", [])
    index = next(
        (
            i
            for i, item in enumerate(entries)
            if item.get("lesson_title") == section.get("title") and item.get("sheet_name") == section.get("sheet_name")
        ),
        None,
    )
    if index is None:
        index = next((i for i, item in enumerate(entries) if item.get("lesson_title") == section.get("title")), None)

    if index is None:
        window = entries[:3]
    else:
        start = max(0, index - 1)
        end = min(len(entries), index + 2)
        window = entries[start:end]

    return {
        "schema_version": schedule_draft.get("schema_version", "1.0.0"),
        "generated_at": schedule_draft.get("generated_at"),
        "sections": window,
    }


def compact_section_for_prompt(section: dict) -> dict:
    textbook_source = next(
        (source for source in section.get("sources", []) if source.get("role", "textbook") == "textbook"),
        section.get("sources", [{}])[0] if section.get("sources") else {},
    )
    inference = textbook_source.get("_inference", {}) if isinstance(textbook_source, dict) else {}
    return {
        "sheet_name": section.get("sheet_name"),
        "card_file": section.get("card_file"),
        "title": section.get("title"),
        "badge": section.get("badge"),
        "pdf_pages": section.get("pdf_pages", []),
        "textbook_source": {
            "resource_id": textbook_source.get("resource_id"),
            "title_query": textbook_source.get("title_query"),
            "start_page": inference.get("start_page"),
            "end_page": inference.get("end_page"),
            "confidence": inference.get("confidence"),
            "status": inference.get("status"),
        },
    }


def compact_lesson_schema_for_prompt() -> dict:
    return {
        "required_root_fields": [
            "schema_version",
            "generated_at",
            "lesson_id",
            "sheet_name",
            "lesson_title",
            "pdf_pages",
            "essential_question",
            "learning_goals",
            "key_concepts",
            "vocabulary",
            "misconceptions",
            "content_chunks",
            "source_page_refs",
            "analysis_confidence",
        ],
        "optional_root_fields": [
            "lesson_type",
            "difficulty_band",
            "review_status",
            "notes",
        ],
        "lesson_type_enum": ["intro", "core", "review", "summary", "mixed"],
        "difficulty_band_enum": ["core", "on-level", "extension", "mixed"],
        "review_status_enum": ["draft", "reviewed", "approved", "rejected"],
        "required_content_chunk_fields": [
            "chunk_id",
            "label",
            "content_type",
            "knowledge_type",
            "summary",
            "source_pages",
        ],
        "content_type_enum": ["text", "image", "diagram", "map", "activity", "summary", "mixed"],
        "knowledge_type_enum": ["fact", "concept", "procedure", "comparison", "cause-effect", "opinion", "application", "mixed"],
        "constraints": {
            "pdf_pages_min_items": 1,
            "learning_goals_min_items": 1,
            "key_concepts_min_items": 1,
            "content_chunks_min_items": 1,
            "source_page_refs_min_items": 1,
            "analysis_confidence_range": [0, 1],
            "additional_properties": False,
        },
    }


def build_lesson_prompt(section: dict, baseline_analysis: dict, schedule_draft: dict, prompt_context: dict) -> str:
    compact_section = compact_section_for_prompt(section)
    compact_baseline = compact_baseline_for_prompt(baseline_analysis)
    compact_schedule = compact_schedule_draft_for_prompt(schedule_draft, section)
    compact_schema = compact_lesson_schema_for_prompt()
    task_prompt = (
        read_prompt("system_analyze.md")
        + "\n\n"
        + read_prompt("user_analyze.md").format(
            section_json=json.dumps(compact_section, ensure_ascii=False, indent=2),
            baseline_json=json.dumps(compact_baseline, ensure_ascii=False, indent=2),
            schedule_json=json.dumps(compact_schedule, ensure_ascii=False, indent=2),
            context_json=json.dumps(prompt_context, ensure_ascii=False, indent=2),
            schema_json=json.dumps(compact_schema, ensure_ascii=False, indent=2),
        )
    )
    return agent_runtime.build_agent_prompt(agent_name="lesson_analysis_agent", task_prompt=task_prompt)


def build_activity_prompt(analysis: dict) -> str:
    compact_analysis = {
        "lesson_id": analysis["lesson_id"],
        "sheet_name": analysis["sheet_name"],
        "lesson_title": analysis["lesson_title"],
        "lesson_type": analysis.get("lesson_type", "core"),
        "pdf_pages": analysis["pdf_pages"],
        "essential_question": analysis["essential_question"],
        "learning_goals": analysis["learning_goals"][:3],
        "key_concepts": analysis["key_concepts"][:5],
        "vocabulary": analysis.get("vocabulary", [])[:8],
        "misconceptions": analysis.get("misconceptions", [])[:4],
        "content_chunks": [
            {
                "chunk_id": chunk["chunk_id"],
                "label": chunk["label"],
                "knowledge_type": chunk["knowledge_type"],
                "summary": chunk["summary"],
                "source_pages": chunk["source_pages"],
            }
            for chunk in analysis.get("content_chunks", [])[:4]
        ],
        "source_page_refs": analysis["source_page_refs"],
    }
    compact_schema = {
        "required_root_fields": ["schema_version", "generated_at", "lesson_id", "activities"],
        "required_activity_fields": [
            "activity_id",
            "lesson_id",
            "object_role",
            "lesson_flow_stage",
            "activity_type",
            "level",
            "learning_goal",
            "prompt_text",
            "layout_template",
            "html_content",
            "source_refs",
            "student_writing_zones",
            "estimated_minutes",
            "review_status",
        ],
        "activity_type_enum": [
            "freeform_html",
            "learning_note",
            "see_think_wonder",
            "worksheet",
            "frayer_model",
            "reference_response",
            "spectrum_sorting",
        ],
        "level_enum": ["core", "on-level", "extension"],
        "input_area_type_enum": ["lined", "free-writing", "inline-answer", "grid", "spectrum"],
    }
    task_prompt = (
        read_prompt("system_plan.md")
        + "\n\n"
        + read_prompt("user_plan.md").format(
            analysis_json=json.dumps(compact_analysis, ensure_ascii=False, indent=2),
            schema_json=json.dumps(compact_schema, ensure_ascii=False, indent=2),
            example_json=json.dumps(ACTIVITY_PLAN_EXAMPLE, ensure_ascii=False, indent=2),
        )
    )
    return agent_runtime.build_agent_prompt(agent_name="activity_plan_agent", task_prompt=task_prompt)


def build_activity_repair_prompt(analysis: dict, candidate_payload: dict, validation_error: str) -> str:
    return (
        build_activity_prompt(analysis)
        + "\n\n"
        + "Validation failed for your previous candidate.\n"
        + f"Failure reason: {validation_error}\n\n"
        + "Previous candidate JSON:\n"
        + json.dumps(candidate_payload, ensure_ascii=False, indent=2)
        + "\n\n"
        + "Rewrite the full activity_plan JSON so it passes the schema and keeps the lesson intent.\n"
        + "Do not explain. Return one corrected JSON object only.\n"
    )


def normalize_lesson_analysis(ai_payload: dict, baseline: dict) -> dict:
    normalized = json.loads(json.dumps(ai_payload, ensure_ascii=False))
    normalized.setdefault("schema_version", "1.0.0")
    normalized["generated_at"] = utc_now()
    normalized["lesson_id"] = baseline.get("lesson_id")
    for key in (
        "sheet_name",
        "lesson_title",
        "lesson_type",
        "pdf_pages",
        "essential_question",
        "learning_goals",
        "key_concepts",
        "vocabulary",
        "misconceptions",
        "difficulty_band",
        "content_chunks",
        "source_page_refs",
    ):
        normalized.setdefault(key, baseline.get(key))
    normalized["analysis_confidence"] = float(normalized.get("analysis_confidence", baseline.get("analysis_confidence", 0.7)))
    normalized["review_status"] = "draft"
    normalized.setdefault("notes", "Gemini CLI draft normalized by local pipeline.")
    validate_lesson_analysis(normalized)
    return normalized


def normalize_activity_plan(ai_payload: dict, analysis: dict) -> dict:
    normalized = json.loads(json.dumps(ai_payload, ensure_ascii=False))
    normalized.setdefault("schema_version", "1.0.0")
    normalized["generated_at"] = utc_now()
    normalized["lesson_id"] = analysis["lesson_id"]
    activities = normalized.get("activities")
    if not isinstance(activities, list):
        raise ValueError("activity_plan.activities must be a list")
    for index, activity in enumerate(activities, start=1):
        activity.setdefault("activity_id", f"{analysis['lesson_id']}-activity-{index}")
        activity["lesson_id"] = analysis["lesson_id"]
        activity.setdefault("object_role", infer_object_role(activity))
        activity.setdefault("lesson_flow_stage", infer_lesson_flow_stage(activity))
        activity.setdefault("learning_goal", analysis["learning_goals"][0])
        activity.setdefault("source_refs", analysis["source_page_refs"])
        activity.setdefault("teacher_notes", "")
        activity.setdefault("review_status", "draft")
        normalize_student_writing_zones(activity)
        if activity.get("html_content"):
            activity["activity_type"] = "freeform_html"
            activity["layout_template"] = "freeform_html"
            activity.setdefault("estimated_minutes", 15)
    return normalized


def infer_object_role(activity: dict) -> str:
    activity_type = activity.get("activity_type")
    if activity_type == "learning_note":
        return "learning_note"
    if activity_type == "worksheet":
        return "worksheet"
    if activity_type == "reference_response":
        return "reference_material"
    return "activity_area"


def infer_lesson_flow_stage(activity: dict) -> str:
    role = activity.get("object_role")
    if role in {"reference_material"}:
        return "before"
    if role in {"worksheet", "ai_courseware"}:
        return "after"
    return "during"


def normalize_student_writing_zones(activity: dict) -> None:
    zones = activity.get("student_writing_zones")
    if not isinstance(zones, list):
        activity["student_writing_zones"] = []
        zones = activity["student_writing_zones"]
    for zone in zones:
        if "input_area_type" not in zone and "type" in zone:
            zone["input_area_type"] = zone.pop("type")
        zone.setdefault("input_area_type", "free-writing")
        zone.setdefault("min_height", 420 if activity.get("lesson_flow_stage") in {"during", "after"} else 220)


def invoke_textbook_only(config_path: Path) -> None:
    subprocess.run(
        ["python3", str(PROJECT_ROOT / "scripts" / "generate_numbers_lesson.py"), "--config", str(config_path)],
        check=True,
    )


def build_artifact_root(config_path: Path, requested_root: str | None) -> Path:
    if requested_root:
        root = Path(requested_root)
    else:
        root = PROJECT_ROOT / "artifacts" / "gemini" / sanitize_name(config_path.stem) / run_timestamp()
    root.mkdir(parents=True, exist_ok=True)
    return root


def process_section(
    index: int,
    section: dict,
    baseline_analysis: dict,
    schedule_draft: dict,
    textbook_context: dict,
    artifact_root: Path,
    args: argparse.Namespace,
) -> tuple[int, Path, Path]:
    section_stem = contracts.section_artifact_stem(section)
    lesson_dir = artifact_root / "sections" / section_stem
    lesson_dir.mkdir(parents=True, exist_ok=True)

    try:
        section_prompt_context = build_section_prompt_context(textbook_context, section["sheet_name"])
        write_json(lesson_dir / "lesson_analysis.context.json", section_prompt_context)
        lesson_prompt = build_lesson_prompt(section, baseline_analysis, schedule_draft, section_prompt_context)
        (lesson_dir / "lesson_analysis.prompt.md").write_text(lesson_prompt, encoding="utf-8")
        lesson_ai, _ = invoke_gemini_json(
            prompt=lesson_prompt,
            artifact_dir=lesson_dir,
            stem="lesson_analysis_ai",
            gemini_bin=args.gemini_bin,
            gemini_model=args.gemini_model,
            gemini_extensions=args.gemini_extensions,
            approval_mode=args.approval_mode,
            debug_artifacts=args.debug_artifacts,
            timeout_sec=args.gemini_timeout_sec,
        )
        normalized_analysis = normalize_lesson_analysis(lesson_ai, baseline_analysis)
    except Exception as exc:
        (lesson_dir / "lesson_analysis.error.txt").write_text(str(exc), encoding="utf-8")
        normalized_analysis = json.loads(json.dumps(baseline_analysis, ensure_ascii=False))
        normalized_analysis["notes"] = f"{normalized_analysis.get('notes', '')} Gemini fallback used: {exc}".strip()

    analysis_path = lesson_dir / "lesson_analysis.json"
    write_json(analysis_path, normalized_analysis)

    try:
        activity_prompt = build_activity_prompt(normalized_analysis)
        (lesson_dir / "activity_plan.prompt.md").write_text(activity_prompt, encoding="utf-8")
        activity_ai, _ = invoke_gemini_json(
            prompt=activity_prompt,
            artifact_dir=lesson_dir,
            stem="activity_plan_ai",
            gemini_bin=args.gemini_bin,
            gemini_model=args.gemini_model,
            gemini_extensions=args.gemini_extensions,
            approval_mode=args.approval_mode,
            debug_artifacts=args.debug_artifacts,
            timeout_sec=args.gemini_timeout_sec,
        )
        try:
            normalized_plan = normalize_activity_plan(activity_ai, normalized_analysis)
        except Exception as validation_exc:
            repair_prompt = build_activity_repair_prompt(normalized_analysis, activity_ai, str(validation_exc))
            (lesson_dir / "activity_plan.repair.prompt.md").write_text(repair_prompt, encoding="utf-8")
            repaired_ai, _ = invoke_gemini_json(
                prompt=repair_prompt,
                artifact_dir=lesson_dir,
                stem="activity_plan_ai_repair",
                gemini_bin=args.gemini_bin,
                gemini_model=args.gemini_model,
                gemini_extensions=args.gemini_extensions,
                approval_mode=args.approval_mode,
                debug_artifacts=args.debug_artifacts,
                timeout_sec=args.gemini_timeout_sec,
            )
            normalized_plan = normalize_activity_plan(repaired_ai, normalized_analysis)
    except Exception as exc:
        (lesson_dir / "activity_plan.error.txt").write_text(str(exc), encoding="utf-8")
        normalized_plan = activity_plan_builder.build_activity_plan(normalized_analysis)
        normalized_plan["notes"] = f"Gemini fallback used: {exc}"

    plan_path = lesson_dir / "activity_plan.json"
    write_json(plan_path, normalized_plan)
    return index, analysis_path, plan_path


def main_with_args(args: argparse.Namespace) -> int:
    global LAST_ARTIFACT_ROOT
    config_path = Path(args.config).resolve()
    artifact_root = build_artifact_root(config_path, args.output_root)
    LAST_ARTIFACT_ROOT = artifact_root

    config = textbook.load_config(config_path)
    effective_config_path = config_path
    if args.pdf:
        config["pdf_path"] = Path(args.pdf).resolve()
        overridden = json.loads(config_path.read_text(encoding="utf-8"))
        overridden["pdf_path"] = str(config["pdf_path"])
        effective_config_path = artifact_root / "effective_config.json"
        write_json(effective_config_path, overridden)
    textbook.infer_section_pages(config)

    chart_path = Path(args.chart).resolve() if args.chart else None
    schedule_draft = build_schedule_draft(config, chart_path)
    write_json(artifact_root / "schedule_draft.json", schedule_draft)

    baseline_analyses, _ = build_textbook_context(config, artifact_root)
    textbook_context = json.loads((artifact_root / "textbook_context.json").read_text(encoding="utf-8"))

    ordered_results: dict[int, tuple[Path, Path]] = {}
    max_workers = max(1, args.max_workers)
    section_inputs = list(enumerate(zip(config["sections"], baseline_analyses)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_section,
                index,
                section,
                baseline_analysis,
                schedule_draft,
                textbook_context,
                artifact_root,
                args,
            )
            for index, (section, baseline_analysis) in section_inputs
        ]
        for future in concurrent.futures.as_completed(futures):
            index, analysis_path, plan_path = future.result()
            ordered_results[index] = (analysis_path, plan_path)

    lesson_analysis_paths = [ordered_results[index][0] for index in range(len(section_inputs))]
    activity_plan_paths = [ordered_results[index][1] for index in range(len(section_inputs))]

    summary = {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "config_path": str(config_path),
        "artifact_root": str(artifact_root),
        "lesson_analysis_paths": [str(path) for path in lesson_analysis_paths],
        "activity_plan_paths": [str(path) for path in activity_plan_paths],
        "output_file": str(config["output_file"]),
    }
    write_json(artifact_root / "run_summary.json", summary)

    if args.dry_run:
        print(artifact_root)
        return 0

    try:
        pipeline_args = argparse.Namespace(
            config=str(effective_config_path),
            activity_plan=[str(path) for path in activity_plan_paths],
            manifest_output=str(artifact_root / "render_manifest.json"),
            keep_assets=args.keep_artifacts,
            include_status=args.include_status,
        )
        numbers_with_activities.main(pipeline_args)
    except Exception:
        if not args.textbook_only_fallback:
            raise
        invoke_textbook_only(effective_config_path)

    print(config["output_file"])
    print(artifact_root)
    return 0


def main() -> int:
    return main_with_args(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
