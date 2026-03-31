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

import generate_activity_plan as local_activity_builder  # noqa: E402
import agent_runtime  # noqa: E402
import agent_runner  # noqa: E402
import orchestrator_events  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402


ACTIVITY_PLAN_SCHEMA_PATH = PROJECT_ROOT / "schemas" / "activity_plan.schema.json"


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


def build_activity_status(run_id: str, lesson_id: str, started_at: str, input_refs: list[str], output_refs: list[str]) -> dict:
    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "activity_plan_agent",
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
        "agent_spec_path": str(agent_runtime.agent_doc_path("activity_plan_agent")),
        "attempt_count": 0,
        "repair_attempted": False,
        "validation_errors": [],
    }


def process_lesson_dir(
    *,
    lesson_dir: Path,
    run_id: str,
    extensions: list[str],
    gemini_bin: str,
    gemini_model: str | None,
    approval_mode: str,
    debug_artifacts: bool,
    gemini_timeout_sec: int | None,
    gemini_idle_timeout_sec: int | None,
) -> dict:
    analysis_path = lesson_dir / "lesson_analysis.json"
    analysis = read_json(analysis_path)
    lesson_id = analysis["lesson_id"]
    started_at = contracts.utc_now()

    plan_path = lesson_dir / "activity_plan.json"
    ai_path = lesson_dir / "activity_plan_ai.json"
    status_path = lesson_dir / "activity_plan.status.json"

    status = build_activity_status(
        run_id=run_id,
        lesson_id=lesson_id,
        started_at=started_at,
        input_refs=[str(analysis_path)],
        output_refs=[str(ai_path), str(plan_path)],
    )
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=lesson_dir.parent.parent,
        run_id=run_id,
        event_type="lesson_started",
        stage="activity_plan_agent",
        lesson_id=lesson_id,
        status="running",
        payload={
            "agent_spec_path": status["agent_spec_path"],
            "input_refs": status["input_refs"],
        },
    )

    fallback_used = False
    try:
        prompt = gemini_pipeline.build_activity_prompt(analysis)
        (lesson_dir / "activity_plan.prompt.md").write_text(prompt, encoding="utf-8")
        status["attempt_count"] = 1
        activity_ai, _ = gemini_pipeline.invoke_gemini_json(
            prompt=prompt,
            artifact_dir=lesson_dir,
            stem="activity_plan_ai",
            gemini_bin=gemini_bin,
            gemini_model=gemini_model,
            gemini_extensions=extensions,
            approval_mode=approval_mode,
            debug_artifacts=debug_artifacts,
            timeout_sec=gemini_timeout_sec,
            idle_timeout_sec=gemini_idle_timeout_sec,
        )
        contracts.write_json(ai_path, activity_ai)
        try:
            normalized = gemini_pipeline.normalize_activity_plan(activity_ai, analysis)
            status["status"] = "succeeded"
        except Exception as validation_exc:
            status["repair_attempted"] = True
            status["validation_errors"].append(str(validation_exc))
            repair_prompt = gemini_pipeline.build_activity_repair_prompt(analysis, activity_ai, str(validation_exc))
            (lesson_dir / "activity_plan.repair.prompt.md").write_text(repair_prompt, encoding="utf-8")
            status["attempt_count"] = 2
            repaired_ai, _ = gemini_pipeline.invoke_gemini_json(
                prompt=repair_prompt,
                artifact_dir=lesson_dir,
                stem="activity_plan_ai_repair",
                gemini_bin=gemini_bin,
                gemini_model=gemini_model,
                gemini_extensions=extensions,
                approval_mode=approval_mode,
                debug_artifacts=debug_artifacts,
                timeout_sec=gemini_timeout_sec,
                idle_timeout_sec=gemini_idle_timeout_sec,
            )
            contracts.write_json(lesson_dir / "activity_plan_ai_repair.json", repaired_ai)
            normalized = gemini_pipeline.normalize_activity_plan(repaired_ai, analysis)
            status["status"] = "succeeded_with_warning"
    except Exception as exc:
        fallback_used = True
        fallback_category, fallback_reason = gemini_pipeline.classify_gemini_failure(exc)
        status["status"] = "succeeded_with_warning"
        status["fallback_used"] = True
        status["fallback_category"] = fallback_category
        status["fallback_reason"] = fallback_reason
        status["errors"].append(str(exc))
        normalized = local_activity_builder.build_activity_plan(analysis)
        normalized["notes"] = f"Gemini fallback used: {exc}"
    contracts.write_json(plan_path, normalized)

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=lesson_dir.parent.parent,
        run_id=run_id,
        event_type="lesson_finished",
        stage="activity_plan_agent",
        lesson_id=lesson_id,
        status=status["status"],
        payload={
            "fallback_used": fallback_used,
            "fallback_category": status.get("fallback_category"),
            "warning_used": status["status"] == "succeeded_with_warning",
            "attempt_count": status["attempt_count"],
            "repair_attempted": status["repair_attempted"],
            "output_refs": status["output_refs"],
        },
    )

    return {
        "plan_path": plan_path,
        "fallback_used": fallback_used,
        "fallback_category": status.get("fallback_category"),
        "warning_used": status["status"] == "succeeded_with_warning",
        "lesson_id": lesson_id,
        "section_key": lesson_dir.name,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-lesson", action="store_true", help="Run one activity plan job")
    parser.add_argument("--run-root")
    parser.add_argument("--run-id")
    parser.add_argument("--section-key")
    parser.add_argument("--gemini-bin", default="gemini")
    parser.add_argument("--gemini-model")
    parser.add_argument("--gemini-extensions", nargs="*", default=["stitch-skills"])
    parser.add_argument("--approval-mode", default="yolo")
    parser.add_argument("--debug-artifacts", action="store_true")
    parser.add_argument("--gemini-timeout-sec", type=int, default=0)
    parser.add_argument("--gemini-idle-timeout-sec", type=int, default=240)
    return parser.parse_args()


def run_single_lesson_job(args: argparse.Namespace) -> int:
    if not args.run_root or not args.run_id or not args.section_key:
        raise ValueError("--run-root, --run-id, and --section-key are required for --single-lesson")
    lesson_dir = Path(args.run_root).resolve() / "sections" / args.section_key
    gemini_timeout_sec = None if args.gemini_timeout_sec <= 0 else args.gemini_timeout_sec
    gemini_idle_timeout_sec = None if args.gemini_idle_timeout_sec <= 0 else args.gemini_idle_timeout_sec
    result = process_lesson_dir(
        lesson_dir=lesson_dir,
        run_id=args.run_id,
        extensions=args.gemini_extensions,
        gemini_bin=args.gemini_bin,
        gemini_model=args.gemini_model,
        approval_mode=args.approval_mode,
        debug_artifacts=args.debug_artifacts,
        gemini_timeout_sec=gemini_timeout_sec,
        gemini_idle_timeout_sec=gemini_idle_timeout_sec,
    )
    print(json.dumps({"result": serialize_jsonable(result)}, ensure_ascii=False))
    return 0


def process_lesson_dir_subprocess(
    *,
    lesson_dir: Path,
    run_id: str,
    extensions: list[str],
    gemini_bin: str,
    gemini_model: str | None,
    approval_mode: str,
    debug_artifacts: bool,
    gemini_timeout_sec: int | None,
    gemini_idle_timeout_sec: int | None,
) -> dict:
    run_root = lesson_dir.parent.parent
    stdout_log_path = lesson_dir / "activity_plan.worker.stdout.log"
    stderr_log_path = lesson_dir / "activity_plan.worker.stderr.log"
    repair_stdout_log_path = lesson_dir / "activity_plan.repair.worker.stdout.log"
    repair_stderr_log_path = lesson_dir / "activity_plan.repair.worker.stderr.log"
    error_path = lesson_dir / "activity_plan.worker.error.json"
    runner_status_path = lesson_dir / "activity_plan.worker.status.json"
    repair_runner_status_path = lesson_dir / "activity_plan.repair.worker.status.json"
    plan_path = lesson_dir / "activity_plan.json"
    ai_path = lesson_dir / "activity_plan_ai.json"
    repair_ai_path = lesson_dir / "activity_plan_ai_repair.json"
    status_path = lesson_dir / "activity_plan.status.json"
    analysis = read_json(lesson_dir / "lesson_analysis.json")
    lesson_id = analysis["lesson_id"]
    started_at = contracts.utc_now()

    status = build_activity_status(
        run_id=run_id,
        lesson_id=lesson_id,
        started_at=started_at,
        input_refs=[str(lesson_dir / "lesson_analysis.json")],
        output_refs=[str(ai_path), str(plan_path)],
    )
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_started",
        stage="activity_plan_agent",
        lesson_id=lesson_id,
        status="running",
        payload={
            "agent_spec_path": status["agent_spec_path"],
            "input_refs": status["input_refs"],
        },
    )

    prompt = gemini_pipeline.build_activity_prompt(analysis)
    prompt_path = lesson_dir / "activity_plan.prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    job_spec = {
        "job_id": f"activity-plan-{lesson_dir.name}",
        "stage": "activity_plan_agent",
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
        "output_schema_path": str(ACTIVITY_PLAN_SCHEMA_PATH),
        "timeout_sec": gemini_timeout_sec,
        "idle_timeout_sec": gemini_idle_timeout_sec,
        "metadata": {
            "section_key": lesson_dir.name,
            "lesson_id": lesson_id,
        },
    }
    with tempfile.NamedTemporaryFile("w", suffix=".activity_plan.job.json", delete=False, encoding="utf-8") as handle:
        handle.write(json.dumps(job_spec, ensure_ascii=False))
        job_spec_path = Path(handle.name)

    def invoke_runner(job_path: Path) -> None:
        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "agent_runner.py"), "--job-spec", str(job_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

    def should_retry_aborted() -> bool:
        if not runner_status_path.exists():
            return False
        runner_status = read_json(runner_status_path)
        runner_errors = runner_status.get("errors", [])
        runner_reason = "; ".join(runner_errors) or "runner failed"
        category, _ = gemini_pipeline.classify_gemini_failure(Exception(runner_reason))
        return category == "aborted"

    try:
        try:
            invoke_runner(job_spec_path)
        except subprocess.CalledProcessError:
            if should_retry_aborted():
                status["attempt_count"] = 2
                invoke_runner(job_spec_path)
            else:
                raise
    except subprocess.CalledProcessError as exc:
        runner_status = read_json(runner_status_path) if runner_status_path.exists() else {}
        runner_errors = runner_status.get("errors", [])
        runner_reason = "; ".join(runner_errors) or str(exc)
        fallback_category, fallback_reason = gemini_pipeline.classify_gemini_failure(Exception(runner_reason))
        contracts.write_json(
            error_path,
            {
                "error_type": "worker_failed",
                "section_key": lesson_dir.name,
                "returncode": exc.returncode,
                "runner": "gemini",
                "runner_errors": runner_errors,
            },
        )
        normalized = local_activity_builder.build_activity_plan(analysis)
        normalized["notes"] = f"Gemini fallback used: {fallback_reason}"
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
                    "section_key": lesson_dir.name,
                    "runner": runner_status.get("runner"),
                    "runner_errors": runner_errors,
                },
            )
            normalized = local_activity_builder.build_activity_plan(analysis)
            normalized["notes"] = f"Gemini fallback used: {fallback_reason}"
            status["status"] = "succeeded_with_warning"
            status["fallback_used"] = True
            status["fallback_category"] = fallback_category
            status["fallback_reason"] = fallback_reason
            status["errors"].extend(runner_errors)
        else:
            activity_ai = read_json(ai_path)
            try:
                normalized = gemini_pipeline.normalize_activity_plan(activity_ai, analysis)
                status["status"] = "succeeded"
            except Exception as validation_exc:
                status["repair_attempted"] = True
                status["validation_errors"].append(str(validation_exc))
                repair_prompt = gemini_pipeline.build_activity_repair_prompt(analysis, activity_ai, str(validation_exc))
                repair_prompt_path = lesson_dir / "activity_plan.repair.prompt.md"
                repair_prompt_path.write_text(repair_prompt, encoding="utf-8")
                repair_job_spec = {
                    "job_id": f"activity-plan-repair-{lesson_dir.name}",
                    "stage": "activity_plan_agent",
                    "cwd": str(PROJECT_ROOT),
                    "output_path": str(repair_ai_path),
                    "status_path": str(repair_runner_status_path),
                    "stdout_log": str(repair_stdout_log_path),
                    "stderr_log": str(repair_stderr_log_path),
                    "prompt_path": str(repair_prompt_path),
                    "cli_bin": gemini_bin,
                    "approval_mode": approval_mode,
                    "extensions": extensions,
                    "model": gemini_model,
                    "output_schema_path": str(ACTIVITY_PLAN_SCHEMA_PATH),
                    "timeout_sec": gemini_timeout_sec,
                    "idle_timeout_sec": gemini_idle_timeout_sec,
                    "metadata": {
                        "section_key": lesson_dir.name,
                        "lesson_id": lesson_id,
                        "repair": True,
                    },
                }
                with tempfile.NamedTemporaryFile("w", suffix=".activity_plan.repair.job.json", delete=False, encoding="utf-8") as handle:
                    handle.write(json.dumps(repair_job_spec, ensure_ascii=False))
                    repair_job_spec_path = Path(handle.name)
                try:
                    subprocess.run(
                        [sys.executable, str(SCRIPT_DIR / "agent_runner.py"), "--job-spec", str(repair_job_spec_path)],
                        cwd=str(PROJECT_ROOT),
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    repaired_ai = read_json(repair_ai_path)
                    normalized = gemini_pipeline.normalize_activity_plan(repaired_ai, analysis)
                    status["status"] = "succeeded_with_warning"
                except Exception as repair_exc:
                    repair_runner_status = read_json(repair_runner_status_path) if repair_runner_status_path.exists() else {}
                    repair_errors = repair_runner_status.get("errors", [])
                    repair_reason = "; ".join(repair_errors) or str(repair_exc)
                    fallback_category, fallback_reason = gemini_pipeline.classify_gemini_failure(Exception(repair_reason))
                    normalized = local_activity_builder.build_activity_plan(analysis)
                    normalized["notes"] = f"Gemini fallback used: {fallback_reason}"
                    status["status"] = "succeeded_with_warning"
                    status["fallback_used"] = True
                    status["fallback_category"] = fallback_category
                    status["fallback_reason"] = fallback_reason
                    status["errors"].append(str(repair_exc))
                finally:
                    repair_job_spec_path.unlink(missing_ok=True)

    contracts.write_json(plan_path, normalized)
    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_finished",
        stage="activity_plan_agent",
        lesson_id=lesson_id,
        status=status["status"],
        payload={
            "fallback_used": bool(status.get("fallback_used")),
            "fallback_category": status.get("fallback_category"),
            "warning_used": status["status"] == "succeeded_with_warning",
            "attempt_count": len(read_json(runner_status_path).get("attempts", [])) if runner_status_path.exists() else 1,
            "repair_attempted": bool(status.get("repair_attempted")),
            "output_refs": status["output_refs"],
        },
    )

    return {
        "plan_path": plan_path,
        "fallback_used": bool(status.get("fallback_used")),
        "fallback_category": status.get("fallback_category"),
        "warning_used": status.get("status") == "succeeded_with_warning",
        "lesson_id": lesson_id,
        "section_key": lesson_dir.name,
    }


def execute_activity_planning(
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
    sections_root = run_root / "sections"
    extensions = gemini_extensions or ["stitch-skills"]

    plan_paths = []
    fallback_count = 0
    warning_count = 0
    fallback_category_counts: dict[str, int] = {}

    lesson_dirs = sorted(path for path in sections_root.iterdir() if path.is_dir())
    ordered_results: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
        futures = {
            executor.submit(
                process_lesson_dir_subprocess,
                lesson_dir=lesson_dir,
                run_id=run_id,
                extensions=extensions,
                gemini_bin=gemini_bin,
                gemini_model=gemini_model,
                approval_mode=approval_mode,
                debug_artifacts=debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec,
                gemini_idle_timeout_sec=gemini_idle_timeout_sec,
            ): lesson_dir.name
            for lesson_dir in lesson_dirs
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            ordered_results[result["section_key"]] = result

    for lesson_dir in lesson_dirs:
        result = ordered_results[lesson_dir.name]
        plan_paths.append(result["plan_path"])
        if result["fallback_used"]:
            fallback_count += 1
            category = result.get("fallback_category") or "unknown"
            fallback_category_counts[category] = fallback_category_counts.get(category, 0) + 1
        if result["warning_used"]:
            warning_count += 1

    return {
        "plan_paths": plan_paths,
        "fallback_count": fallback_count,
        "warning_count": warning_count,
        "fallback_category_counts": fallback_category_counts,
    }


def main() -> int:
    args = parse_args()
    if args.single_lesson:
        return run_single_lesson_job(args)
    raise SystemExit("activity_plan_agent.py is intended to be imported or run with --single-lesson")


if __name__ == "__main__":
    raise SystemExit(main())
