import argparse
import concurrent.futures
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import pipeline_contracts as contracts  # noqa: E402
import orchestrator_events  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402
import agent_runtime  # noqa: E402
import agent_runner  # noqa: E402


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def serialize_jsonable(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: serialize_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_jsonable(item) for item in value]
    return value


def section_dir(run_root: Path, section: dict) -> Path:
    lesson_dir = run_root / "sections" / contracts.section_artifact_stem(section)
    lesson_dir.mkdir(parents=True, exist_ok=True)
    return lesson_dir


def build_lesson_status(run_id: str, lesson_id: str, started_at: str, input_refs: list[str], output_refs: list[str]) -> dict:
    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "lesson_analysis_agent",
        "lesson_id": lesson_id,
        "status": "running",
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": None,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "fallback_used": False,
        "fallback_category": None,
        "fallback_reason": None,
        "warnings": [],
        "errors": [],
        "model": None,
        "agent_spec_path": str(agent_runtime.agent_doc_path("lesson_analysis_agent")),
        "attempt_count": 0,
        "validation_errors": [],
    }


def process_section(
    *,
    section: dict,
    run_root: Path,
    run_id: str,
    source_dir: Path,
    schedule_draft: dict,
    textbook_context: dict,
    gemini_bin: str,
    gemini_model: str | None,
    extensions: list[str],
    approval_mode: str,
    debug_artifacts: bool,
    gemini_timeout_sec: int | None,
    gemini_idle_timeout_sec: int | None,
) -> dict:
    lesson_dir = section_dir(run_root, section)
    started_at = contracts.utc_now()
    baseline_path = source_dir / "local_baseline" / f"{contracts.section_artifact_stem(section)}.lesson_analysis.json"
    baseline_analysis = read_json(baseline_path)

    analysis_path = lesson_dir / "lesson_analysis.json"
    ai_path = lesson_dir / "lesson_analysis_ai.json"
    status_path = lesson_dir / "lesson_analysis.status.json"

    status = build_lesson_status(
        run_id=run_id,
        lesson_id=section["sheet_name"],
        started_at=started_at,
        input_refs=[
            str(source_dir / "schedule_draft.json"),
            str(source_dir / "textbook_context.json"),
            str(baseline_path),
        ],
        output_refs=[str(ai_path), str(analysis_path)],
    )
    status["model"] = gemini_model or gemini_bin
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_started",
        stage="lesson_analysis_agent",
        lesson_id=section["sheet_name"],
        status="running",
        payload={
            "agent_spec_path": status["agent_spec_path"],
            "input_refs": status["input_refs"],
        },
    )

    fallback_used = False
    try:
        prompt_context = gemini_pipeline.build_section_prompt_context_by_key(
            textbook_context,
            contracts.section_artifact_stem(section),
        )
        contracts.write_json(lesson_dir / "lesson_analysis.context.json", prompt_context)
        prompt = gemini_pipeline.build_lesson_prompt(section, baseline_analysis, schedule_draft, prompt_context)
        (lesson_dir / "lesson_analysis.prompt.md").write_text(prompt, encoding="utf-8")
        status["attempt_count"] = 1
        lesson_ai, _ = gemini_pipeline.invoke_gemini_json(
            prompt=prompt,
            artifact_dir=lesson_dir,
            stem="lesson_analysis_ai",
            gemini_bin=gemini_bin,
            gemini_model=gemini_model,
            gemini_extensions=extensions,
            approval_mode=approval_mode,
            debug_artifacts=debug_artifacts,
            timeout_sec=gemini_timeout_sec,
            idle_timeout_sec=gemini_idle_timeout_sec,
        )
        contracts.write_json(ai_path, lesson_ai)
        normalized = gemini_pipeline.normalize_lesson_analysis(lesson_ai, baseline_analysis)
        status["status"] = "succeeded"
    except Exception as exc:
        fallback_used = True
        fallback_category, fallback_reason = gemini_pipeline.classify_gemini_failure(exc)
        status["status"] = "succeeded_with_warning"
        status["fallback_used"] = True
        status["fallback_category"] = fallback_category
        status["fallback_reason"] = fallback_reason
        status["errors"].append(str(exc))
        normalized = json.loads(json.dumps(baseline_analysis, ensure_ascii=False))
        normalized["notes"] = f"{normalized.get('notes', '')} Gemini fallback used: {exc}".strip()
    contracts.write_json(analysis_path, normalized)

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_finished",
        stage="lesson_analysis_agent",
        lesson_id=section["sheet_name"],
        status=status["status"],
        payload={
            "fallback_used": fallback_used,
            "fallback_category": status.get("fallback_category"),
            "warning_used": status["status"] == "succeeded_with_warning",
            "attempt_count": status["attempt_count"],
            "output_refs": status["output_refs"],
        },
    )

    return {
        "analysis_path": analysis_path,
        "fallback_used": fallback_used,
        "fallback_category": status.get("fallback_category"),
        "warning_used": status["status"] == "succeeded_with_warning",
        "lesson_id": section["sheet_name"],
        "section_key": lesson_dir.name,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-lesson", action="store_true", help="Run one lesson analysis job")
    parser.add_argument("--run-root")
    parser.add_argument("--run-id")
    parser.add_argument("--section-key")
    parser.add_argument("--gemini-bin", default="gemini")
    parser.add_argument("--gemini-model")
    parser.add_argument("--gemini-extensions", nargs="*", default=["stitch-skills"])
    parser.add_argument("--approval-mode", default="yolo")
    parser.add_argument("--debug-artifacts", action="store_true")
    parser.add_argument("--gemini-timeout-sec", type=int, default=0)
    parser.add_argument("--gemini-idle-timeout-sec", type=int, default=180)
    return parser.parse_args()


def find_section_by_key(runtime_config: dict, section_key: str) -> dict:
    for section in runtime_config.get("sections", []):
        if contracts.section_artifact_stem(section) == section_key:
            return section
    raise ValueError(f"Could not find section for key: {section_key}")


def run_single_lesson_job(args: argparse.Namespace) -> int:
    if not args.run_root or not args.run_id or not args.section_key:
        raise ValueError("--run-root, --run-id, and --section-key are required for --single-lesson")

    gemini_timeout_sec = None if args.gemini_timeout_sec <= 0 else args.gemini_timeout_sec
    gemini_idle_timeout_sec = None if args.gemini_idle_timeout_sec <= 0 else args.gemini_idle_timeout_sec
    run_root = Path(args.run_root).resolve()
    source_dir = run_root / "source"
    runtime_config = read_json(source_dir / "runtime_config.json")
    schedule_draft = read_json(source_dir / "schedule_draft.json")
    textbook_context = read_json(source_dir / "textbook_context.json")
    section = find_section_by_key(runtime_config, args.section_key)
    result = process_section(
        section=section,
        run_root=run_root,
        run_id=args.run_id,
        source_dir=source_dir,
        schedule_draft=schedule_draft,
        textbook_context=textbook_context,
        gemini_bin=args.gemini_bin,
        gemini_model=args.gemini_model,
        extensions=args.gemini_extensions,
        approval_mode=args.approval_mode,
        debug_artifacts=args.debug_artifacts,
        gemini_timeout_sec=gemini_timeout_sec,
        gemini_idle_timeout_sec=gemini_idle_timeout_sec,
    )
    print(json.dumps({"result": serialize_jsonable(result)}, ensure_ascii=False))
    return 0


def process_section_subprocess(
    *,
    section: dict,
    run_root: Path,
    run_id: str,
    gemini_bin: str,
    gemini_model: str | None,
    extensions: list[str],
    approval_mode: str,
    debug_artifacts: bool,
    gemini_timeout_sec: int | None,
    gemini_idle_timeout_sec: int | None,
) -> dict:
    lesson_dir = section_dir(run_root, section)
    source_dir = run_root / "source"
    baseline_path = source_dir / "local_baseline" / f"{contracts.section_artifact_stem(section)}.lesson_analysis.json"
    baseline_analysis = read_json(baseline_path)
    schedule_draft = read_json(source_dir / "schedule_draft.json")
    textbook_context = read_json(source_dir / "textbook_context.json")

    stdout_log_path = lesson_dir / "lesson_analysis.worker.stdout.log"
    stderr_log_path = lesson_dir / "lesson_analysis.worker.stderr.log"
    error_path = lesson_dir / "lesson_analysis.worker.error.json"
    runner_status_path = lesson_dir / "lesson_analysis.worker.status.json"
    analysis_path = lesson_dir / "lesson_analysis.json"
    ai_path = lesson_dir / "lesson_analysis_ai.json"
    status_path = lesson_dir / "lesson_analysis.status.json"
    started_at = contracts.utc_now()

    status = build_lesson_status(
        run_id=run_id,
        lesson_id=section["sheet_name"],
        started_at=started_at,
        input_refs=[
            str(source_dir / "schedule_draft.json"),
            str(source_dir / "textbook_context.json"),
            str(baseline_path),
        ],
        output_refs=[str(ai_path), str(analysis_path)],
    )
    status["model"] = gemini_model or gemini_bin
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_started",
        stage="lesson_analysis_agent",
        lesson_id=section["sheet_name"],
        status="running",
        payload={
            "agent_spec_path": status["agent_spec_path"],
            "input_refs": status["input_refs"],
        },
    )

    prompt_context = gemini_pipeline.build_section_prompt_context_by_key(
        textbook_context,
        contracts.section_artifact_stem(section),
    )
    contracts.write_json(lesson_dir / "lesson_analysis.context.json", prompt_context)
    prompt = gemini_pipeline.build_lesson_prompt(section, baseline_analysis, schedule_draft, prompt_context)
    prompt_path = lesson_dir / "lesson_analysis.prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    job_spec = {
        "job_id": f"lesson-analysis-{contracts.section_artifact_stem(section)}",
        "stage": "lesson_analysis_agent",
        "cwd": str(PROJECT_ROOT),
        "output_path": str(ai_path),
        "status_path": str(runner_status_path),
        "stdout_log": str(stdout_log_path),
        "stderr_log": str(stderr_log_path),
        "prompt_path": str(prompt_path),
        "cli_bin": gemini_bin,
        "approval_mode": approval_mode,
        "extensions": extensions,
        "model": gemini_model,
        "timeout_sec": gemini_timeout_sec,
        "idle_timeout_sec": gemini_idle_timeout_sec,
        "metadata": {
            "section_key": contracts.section_artifact_stem(section),
            "lesson_id": section["sheet_name"],
        },
    }
    with tempfile.NamedTemporaryFile("w", suffix=".lesson_analysis.job.json", delete=False, encoding="utf-8") as handle:
        handle.write(json.dumps(job_spec, ensure_ascii=False))
        job_spec_path = Path(handle.name)
    try:
        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "agent_runner.py"), "--job-spec", str(job_spec_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        runner_status = read_json(runner_status_path) if runner_status_path.exists() else {}
        runner_errors = runner_status.get("errors", [])
        runner_reason = "; ".join(runner_errors) or str(exc)
        fallback_category, fallback_reason = gemini_pipeline.classify_gemini_failure(Exception(runner_reason))
        contracts.write_json(
            error_path,
            {
                "error_type": "worker_failed",
                "section_key": contracts.section_artifact_stem(section),
                "lesson_id": section["sheet_name"],
                "returncode": exc.returncode,
                "runner": "gemini",
                "runner_errors": runner_errors,
            },
        )
        normalized = json.loads(json.dumps(baseline_analysis, ensure_ascii=False))
        status["status"] = "succeeded_with_warning"
        status["fallback_used"] = True
        status["fallback_category"] = fallback_category
        status["fallback_reason"] = fallback_reason
        status["errors"].append(str(exc))
    finally:
        job_spec_path.unlink(missing_ok=True)
    if "normalized" not in locals():
        runner_status = read_json(runner_status_path)
        if runner_status.get("status") != "succeeded":
            runner_errors = runner_status.get("errors", [])
            runner_reason = "; ".join(runner_errors) or "runner failed"
            fallback_category, fallback_reason = gemini_pipeline.classify_gemini_failure(Exception(runner_reason))
            contracts.write_json(
                error_path,
                {
                    "error_type": "worker_failed",
                    "section_key": contracts.section_artifact_stem(section),
                    "lesson_id": section["sheet_name"],
                    "runner": runner_status.get("runner"),
                    "runner_errors": runner_errors,
                },
            )
            normalized = json.loads(json.dumps(baseline_analysis, ensure_ascii=False))
            status["status"] = "succeeded_with_warning"
            status["fallback_used"] = True
            status["fallback_category"] = fallback_category
            status["fallback_reason"] = fallback_reason
            status["errors"].extend(runner_errors)
        else:
            lesson_ai = read_json(ai_path)
            try:
                normalized = gemini_pipeline.normalize_lesson_analysis(lesson_ai, baseline_analysis)
                status["status"] = "succeeded"
            except Exception as exc:
                normalized = json.loads(json.dumps(baseline_analysis, ensure_ascii=False))
                status["status"] = "succeeded_with_warning"
                status["fallback_used"] = True
                status["fallback_category"] = "validation_error"
                status["fallback_reason"] = str(exc)
                status["errors"].append(str(exc))

    contracts.write_json(analysis_path, normalized)
    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_finished",
        stage="lesson_analysis_agent",
        lesson_id=section["sheet_name"],
        status=status["status"],
        payload={
            "fallback_used": bool(status.get("fallback_used")),
            "fallback_category": status.get("fallback_category"),
            "warning_used": status["status"] == "succeeded_with_warning",
            "attempt_count": len(read_json(runner_status_path).get("attempts", [])) if runner_status_path.exists() else 1,
            "output_refs": status["output_refs"],
        },
    )

    return {
        "analysis_path": analysis_path,
        "fallback_used": bool(status.get("fallback_used")),
        "fallback_category": status.get("fallback_category"),
        "warning_used": status.get("status") == "succeeded_with_warning",
        "lesson_id": section["sheet_name"],
        "section_key": lesson_dir.name,
    }


def execute_lesson_analysis(
    *,
    run_root: Path,
    run_id: str,
    gemini_bin: str = "gemini",
    gemini_model: str | None = None,
    gemini_extensions: list[str] | None = None,
    approval_mode: str = "yolo",
    debug_artifacts: bool = False,
    gemini_timeout_sec: int | None = None,
    gemini_idle_timeout_sec: int | None = None,
    max_workers: int = 2,
) -> dict:
    source_dir = run_root / "source"
    runtime_config = read_json(source_dir / "runtime_config.json")
    schedule_draft = read_json(source_dir / "schedule_draft.json")
    textbook_context = read_json(source_dir / "textbook_context.json")
    extensions = gemini_extensions or ["stitch-skills"]

    analyses = []
    fallback_count = 0
    warning_count = 0
    fallback_category_counts: dict[str, int] = {}

    ordered_results: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
        futures = {
            executor.submit(
                process_section_subprocess,
                section=section,
                run_root=run_root,
                run_id=run_id,
                gemini_bin=gemini_bin,
                gemini_model=gemini_model,
                extensions=extensions,
                approval_mode=approval_mode,
                debug_artifacts=debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec,
                gemini_idle_timeout_sec=gemini_idle_timeout_sec,
            ): section["sheet_name"]
            for section in runtime_config["sections"]
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            ordered_results[result["section_key"]] = result

    for section in runtime_config["sections"]:
        result = ordered_results[contracts.section_artifact_stem(section)]
        analyses.append(result["analysis_path"])
        if result["fallback_used"]:
            fallback_count += 1
            category = result.get("fallback_category") or "unknown"
            fallback_category_counts[category] = fallback_category_counts.get(category, 0) + 1
        if result["warning_used"]:
            warning_count += 1

    return {
        "analysis_paths": analyses,
        "fallback_count": fallback_count,
        "warning_count": warning_count,
        "fallback_category_counts": fallback_category_counts,
    }


def main() -> int:
    args = parse_args()
    if args.single_lesson:
        return run_single_lesson_job(args)
    raise SystemExit("lesson_analysis_agent.py is intended to be imported or run with --single-lesson")


if __name__ == "__main__":
    raise SystemExit(main())
