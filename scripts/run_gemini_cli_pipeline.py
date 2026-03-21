import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import fitz


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import draft_config_from_progress_chart as chart_draft  # noqa: E402
import generate_activity_plan as activity_plan_builder  # noqa: E402
import generate_lesson_analysis as lesson_analysis_builder  # noqa: E402
import generate_numbers_lesson as textbook  # noqa: E402
import generate_numbers_with_activities as numbers_with_activities  # noqa: E402


PROMPTS_DIR = PROJECT_ROOT / "prompts" / "gemini"
WORKSPACE_PROMPT_DIR = PROJECT_ROOT / "artifacts" / "_gemini_prompts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to textbook config JSON")
    parser.add_argument("--pdf", help="Optional override for textbook PDF path")
    parser.add_argument("--chart", help="Optional progress chart image path")
    parser.add_argument("--gemini-bin", default="gemini", help="Gemini CLI binary path")
    parser.add_argument("--gemini-model", help="Gemini model name")
    parser.add_argument("--output-root", help="Artifact root directory")
    parser.add_argument("--approval-mode", default="yolo", help="Gemini CLI approval mode")
    parser.add_argument("--keep-artifacts", action="store_true", help="Keep generated assets from downstream renderer")
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
    return path.read_text(encoding="utf-8")


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_prompt(name: str) -> str:
    return read_text(PROMPTS_DIR / name)


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


def extract_json_from_response_text(text: str) -> dict:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = extract_last_json_object(text)
    if not isinstance(parsed, dict):
        raise ValueError("Gemini response did not contain a JSON object")
    return parsed


def invoke_gemini_json(
    prompt: str,
    artifact_dir: Path,
    stem: str,
    gemini_bin: str,
    gemini_model: str | None,
    approval_mode: str,
) -> tuple[dict, str]:
    WORKSPACE_PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    prompt_path = WORKSPACE_PROMPT_DIR / f"{sanitize_name(artifact_dir.name)}-{stem}.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    command = [
        gemini_bin,
        "-p",
        f"Read {prompt_path} and follow it exactly. Return JSON only.",
        "-o",
        "json",
        "--approval-mode",
        approval_mode,
    ]
    if gemini_model:
        command.extend(["-m", gemini_model])

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        (artifact_dir / f"{stem}.stdout.txt").write_text(exc.stdout or "", encoding="utf-8")
        (artifact_dir / f"{stem}.stderr.txt").write_text(exc.stderr or "", encoding="utf-8")
        raise

    raw_output = result.stdout
    raw_path = artifact_dir / f"{stem}.raw.txt"
    raw_path.write_text(raw_output, encoding="utf-8")
    stderr_path = artifact_dir / f"{stem}.stderr.txt"
    stderr_path.write_text(result.stderr, encoding="utf-8")

    wrapper = extract_last_json_object(raw_output)
    wrapper_path = artifact_dir / f"{stem}.wrapper.json"
    write_json(wrapper_path, wrapper)

    response_text = wrapper.get("response", "")
    parsed = extract_json_from_response_text(response_text)
    parsed_path = artifact_dir / f"{stem}.response.json"
    write_json(parsed_path, parsed)
    return parsed, raw_output


def load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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

            analysis_path = artifact_dir / "local_baseline" / f"{section['card_file']}.lesson_analysis.json"
            write_json(analysis_path, analysis)
            analysis_paths.append(analysis_path)

            section_text = []
            for page in section["pdf_pages"]:
                section_text.append(doc[page - 1].get_text("text").strip())

            context_sections.append(
                {
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


def build_lesson_prompt(section: dict, baseline_analysis: dict, schedule_draft: dict, textbook_context: dict) -> str:
    return (
        read_prompt("system_analyze.md")
        + "\n\n"
        + read_prompt("user_analyze.md").format(
            section_json=json.dumps(section, ensure_ascii=False, indent=2),
            baseline_json=json.dumps(baseline_analysis, ensure_ascii=False, indent=2),
            schedule_json=json.dumps(schedule_draft, ensure_ascii=False, indent=2),
            context_json=json.dumps(textbook_context, ensure_ascii=False, indent=2),
            schema_json=read_text(PROJECT_ROOT / "schemas" / "lesson_analysis.schema.json"),
        )
    )


def build_activity_prompt(analysis: dict) -> str:
    return (
        read_prompt("system_plan.md")
        + "\n\n"
        + read_prompt("user_plan.md").format(
            analysis_json=json.dumps(analysis, ensure_ascii=False, indent=2),
            schema_json=read_text(PROJECT_ROOT / "schemas" / "activity_plan.schema.json"),
        )
    )


def normalize_lesson_analysis(ai_payload: dict, baseline: dict) -> dict:
    normalized = json.loads(json.dumps(ai_payload, ensure_ascii=False))
    normalized.setdefault("schema_version", "1.0.0")
    normalized["generated_at"] = utc_now()
    for key in (
        "lesson_id",
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
    normalized.setdefault("lesson_id", analysis["lesson_id"])
    activities = normalized.get("activities")
    if not isinstance(activities, list):
        raise ValueError("activity_plan.activities must be a list")
    for index, activity in enumerate(activities, start=1):
        activity.setdefault("activity_id", f"{analysis['lesson_id']}-activity-{index}")
        activity.setdefault("lesson_id", analysis["lesson_id"])
        activity.setdefault("learning_goal", analysis["learning_goals"][0])
        activity.setdefault("source_refs", analysis["source_page_refs"])
        activity.setdefault("teacher_notes", "")
        activity.setdefault("review_status", "draft")
        if activity.get("html_content"):
            activity["activity_type"] = "freeform_html"
            activity["layout_template"] = "freeform_html"
            activity.setdefault("student_writing_zones", [])
            activity.setdefault("estimated_minutes", 15)
    validate_activity_plan(normalized)
    return normalized


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


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    artifact_root = build_artifact_root(config_path, args.output_root)

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

    lesson_analysis_paths: list[Path] = []
    activity_plan_paths: list[Path] = []

    for section, baseline_analysis in zip(config["sections"], baseline_analyses):
        section_stem = sanitize_name(section["card_file"])
        lesson_dir = artifact_root / "sections" / section_stem
        lesson_dir.mkdir(parents=True, exist_ok=True)

        try:
            lesson_prompt = build_lesson_prompt(section, baseline_analysis, schedule_draft, textbook_context)
            (lesson_dir / "lesson_analysis.prompt.md").write_text(lesson_prompt, encoding="utf-8")
            lesson_ai, _ = invoke_gemini_json(
                prompt=lesson_prompt,
                artifact_dir=lesson_dir,
                stem="lesson_analysis_ai",
                gemini_bin=args.gemini_bin,
                gemini_model=args.gemini_model,
                approval_mode=args.approval_mode,
            )
            normalized_analysis = normalize_lesson_analysis(lesson_ai, baseline_analysis)
        except Exception as exc:
            (lesson_dir / "lesson_analysis.error.txt").write_text(str(exc), encoding="utf-8")
            normalized_analysis = baseline_analysis
            normalized_analysis["notes"] = f"{normalized_analysis.get('notes', '')} Gemini fallback used: {exc}".strip()

        analysis_path = lesson_dir / "lesson_analysis.json"
        write_json(analysis_path, normalized_analysis)
        lesson_analysis_paths.append(analysis_path)

        try:
            activity_prompt = build_activity_prompt(normalized_analysis)
            (lesson_dir / "activity_plan.prompt.md").write_text(activity_prompt, encoding="utf-8")
            activity_ai, _ = invoke_gemini_json(
                prompt=activity_prompt,
                artifact_dir=lesson_dir,
                stem="activity_plan_ai",
                gemini_bin=args.gemini_bin,
                gemini_model=args.gemini_model,
                approval_mode=args.approval_mode,
            )
            normalized_plan = normalize_activity_plan(activity_ai, normalized_analysis)
        except Exception as exc:
            (lesson_dir / "activity_plan.error.txt").write_text(str(exc), encoding="utf-8")
            normalized_plan = activity_plan_builder.build_activity_plan(normalized_analysis)
            normalized_plan["notes"] = f"Gemini fallback used: {exc}"

        plan_path = lesson_dir / "activity_plan.json"
        write_json(plan_path, normalized_plan)
        activity_plan_paths.append(plan_path)

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


if __name__ == "__main__":
    raise SystemExit(main())
