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

import agent_runtime  # noqa: E402
import agent_runner  # noqa: E402
import orchestrator_events  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402


REVIEW_SCHEMA_PATH = PROJECT_ROOT / "schemas" / "lesson_review.schema.json"


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


def build_lesson_review(lesson_id: str, analysis: dict) -> dict:
    findings = []
    warnings = []
    blocking_issues = []
    decision = "pass"

    if not analysis.get("learning_goals"):
        blocking_issues.append("learning_goals is empty")
    if not analysis.get("key_concepts"):
        blocking_issues.append("key_concepts is empty")
    if not analysis.get("source_page_refs"):
        blocking_issues.append("source_page_refs is empty")
    if not analysis.get("misconceptions"):
        warnings.append("misconceptions is empty")
        findings.append({"severity": "warning", "message": "오개념 후보가 비어 있습니다.", "evidence_refs": []})
    if analysis.get("notes"):
        findings.append({"severity": "info", "message": analysis["notes"], "evidence_refs": []})

    if blocking_issues:
        decision = "blocked"
    elif warnings:
        decision = "pass_with_warning"

    status = "succeeded" if decision == "pass" else "succeeded_with_warning"
    if decision == "blocked":
        status = "blocked"

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "lesson_review_agent",
        "lesson_id": lesson_id,
        "status": status,
        "decision": decision,
        "findings": findings,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }


def build_lesson_review_prompt(analysis: dict) -> str:
    lesson_id = analysis["lesson_id"]
    task_prompt = (
        "다음 lesson_analysis.json을 검토하고 review_result schema를 만족하는 JSON만 반환하라.\n"
        "검토 목적은 구조적 결함과 downstream 진행 가능 여부를 판단하는 것이다.\n"
        "반드시 다음 규칙을 지켜라.\n"
        "- stage는 'lesson_review_agent'로 설정한다.\n"
        f"- lesson_id는 '{lesson_id}'로 유지한다.\n"
        "- decision은 pass, pass_with_warning, blocked 중 하나만 사용한다.\n"
        "- status는 decision에 맞게 succeeded, succeeded_with_warning, blocked 중 하나로 설정한다.\n"
        "- findings는 severity/message/evidence_refs 구조를 지킨다.\n"
        "- blocking_issues와 warnings는 문자열 배열로 채운다.\n"
        "- 설명 문장이나 코드블록 없이 JSON 객체만 출력한다.\n\n"
        "입력 lesson_analysis.json:\n"
        f"{json.dumps(analysis, ensure_ascii=False, indent=2)}"
    )
    return agent_runtime.build_agent_prompt(agent_name="lesson_review_agent", task_prompt=task_prompt)


def process_lesson_dir(*, lesson_dir: Path, run_root: Path, run_id: str) -> dict:
    analysis_path = lesson_dir / "lesson_analysis.json"
    analysis = read_json(analysis_path)
    lesson_id = analysis["lesson_id"]
    review_path = lesson_dir / "lesson_review.json"
    status_path = lesson_dir / "lesson_review.status.json"
    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "lesson_review_agent",
        "lesson_id": lesson_id,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(analysis_path)],
        "output_refs": [str(review_path)],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path("lesson_review_agent")),
    }
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_started",
        stage="lesson_review_agent",
        lesson_id=lesson_id,
        status="running",
        payload={"agent_spec_path": status["agent_spec_path"], "input_refs": status["input_refs"]},
    )

    review = build_lesson_review(lesson_id, analysis)
    contracts.write_json(review_path, review)
    status["finished_at"] = contracts.utc_now()
    status["status"] = review["status"]
    status["warnings"].extend(review["warnings"])
    status["errors"].extend(review["blocking_issues"])
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_finished",
        stage="lesson_review_agent",
        lesson_id=lesson_id,
        status=status["status"],
        payload={
            "fallback_used": False,
            "warning_used": review["decision"] != "pass",
            "output_refs": status["output_refs"],
        },
    )
    return {
        "lesson_id": lesson_id,
        "section_key": lesson_dir.name,
        "review_path": review_path,
        "warning_used": review["decision"] == "pass_with_warning",
        "blocked_used": review["decision"] == "blocked",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--single-lesson", action="store_true", help="Run one lesson review job")
    parser.add_argument("--run-root")
    parser.add_argument("--run-id")
    parser.add_argument("--section-key")
    return parser.parse_args()


def run_single_lesson_job(args: argparse.Namespace) -> int:
    if not args.run_root or not args.run_id or not args.section_key:
        raise ValueError("--run-root, --run-id, and --section-key are required for --single-lesson")
    run_root = Path(args.run_root).resolve()
    lesson_dir = run_root / "sections" / args.section_key
    result = process_lesson_dir(lesson_dir=lesson_dir, run_root=run_root, run_id=args.run_id)
    print(json.dumps({"result": serialize_jsonable(result)}, ensure_ascii=False))
    return 0


def process_lesson_dir_subprocess(*, lesson_dir: Path, run_root: Path, run_id: str) -> dict:
    stdout_log_path = lesson_dir / "lesson_review.worker.stdout.log"
    stderr_log_path = lesson_dir / "lesson_review.worker.stderr.log"
    error_path = lesson_dir / "lesson_review.worker.error.json"
    runner_status_path = lesson_dir / "lesson_review.worker.status.json"
    review_path = lesson_dir / "lesson_review.json"
    analysis = read_json(lesson_dir / "lesson_analysis.json")
    prompt_path = lesson_dir / "lesson_review.prompt.md"
    prompt_path.write_text(build_lesson_review_prompt(analysis), encoding="utf-8")
    status_path = lesson_dir / "lesson_review.status.json"
    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "lesson_review_agent",
        "lesson_id": analysis["lesson_id"],
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(lesson_dir / "lesson_analysis.json")],
        "output_refs": [str(review_path)],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path("lesson_review_agent")),
    }
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_started",
        stage="lesson_review_agent",
        lesson_id=analysis["lesson_id"],
        status="running",
        payload={"agent_spec_path": status["agent_spec_path"], "input_refs": status["input_refs"]},
    )
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--single-lesson",
        "--run-root",
        str(run_root),
        "--run-id",
        run_id,
        "--section-key",
        lesson_dir.name,
    ]

    job_spec = {
        "job_id": f"lesson-review-{lesson_dir.name}",
        "stage": "lesson_review_agent",
        "command": cmd,
        "cwd": str(PROJECT_ROOT),
        "output_path": str(review_path),
        "status_path": str(runner_status_path),
        "stdout_log": str(stdout_log_path),
        "stderr_log": str(stderr_log_path),
        "prompt_path": str(prompt_path),
        "output_schema_path": str(REVIEW_SCHEMA_PATH),
        "cli_bin": "codex",
        "timeout_sec": 60,
        "idle_timeout_sec": 60,
        "metadata": {
            "section_key": lesson_dir.name,
            "lesson_id": analysis["lesson_id"],
        },
    }
    with tempfile.NamedTemporaryFile("w", suffix=".lesson_review.job.json", delete=False, encoding="utf-8") as handle:
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
        contracts.write_json(
            error_path,
            {
                "error_type": "worker_failed",
                "section_key": lesson_dir.name,
                "returncode": exc.returncode,
                "command": cmd,
                "runner_errors": runner_status.get("errors", []),
            },
        )
        raise RuntimeError(f"lesson_review worker failed for {lesson_dir.name} with exit code {exc.returncode}") from exc
    finally:
        job_spec_path.unlink(missing_ok=True)

    runner_status = read_json(runner_status_path)
    if runner_status.get("status") != "succeeded":
        contracts.write_json(
            error_path,
            {
                "error_type": "worker_failed",
                "section_key": lesson_dir.name,
                "command": cmd,
                "runner_errors": runner_status.get("errors", []),
            },
        )
        raise RuntimeError(f"lesson_review worker failed for {lesson_dir.name}: {runner_status.get('errors', [])}")

    review = read_json(review_path)
    status["finished_at"] = contracts.utc_now()
    status["status"] = review["status"]
    status["warnings"].extend(review["warnings"])
    status["errors"].extend(review["blocking_issues"])
    status["fallback_used"] = bool(runner_status.get("fallback_used"))
    contracts.write_json(status_path, status)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="lesson_finished",
        stage="lesson_review_agent",
        lesson_id=analysis["lesson_id"],
        status=status["status"],
        payload={
            "fallback_used": bool(runner_status.get("fallback_used")),
            "warning_used": review["decision"] != "pass",
            "output_refs": status["output_refs"],
        },
    )
    return {
        "lesson_id": analysis["lesson_id"],
        "section_key": lesson_dir.name,
        "review_path": review_path,
        "warning_used": status.get("status") == "succeeded_with_warning",
        "blocked_used": status.get("status") == "blocked",
    }


def execute_lesson_review(*, run_root: Path, run_id: str, max_workers: int = 2) -> dict:
    sections_root = run_root / "sections"
    lesson_dirs = sorted(path for path in sections_root.iterdir() if path.is_dir() and (path / "lesson_analysis.json").exists())
    review_paths = []
    warning_count = 0
    blocked_count = 0
    ordered_results: dict[str, dict] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
        futures = {
            executor.submit(process_lesson_dir_subprocess, lesson_dir=lesson_dir, run_root=run_root, run_id=run_id): lesson_dir.name
            for lesson_dir in lesson_dirs
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            ordered_results[result["section_key"]] = result

    for lesson_dir in lesson_dirs:
        result = ordered_results[lesson_dir.name]
        review_paths.append(result["review_path"])
        if result["warning_used"]:
            warning_count += 1
        if result["blocked_used"]:
            blocked_count += 1

    return {
        "review_paths": review_paths,
        "warning_count": warning_count,
        "blocked_count": blocked_count,
    }


def main() -> int:
    args = parse_args()
    if args.single_lesson:
        return run_single_lesson_job(args)
    raise SystemExit("lesson_review_agent.py is intended to be imported or run with --single-lesson")


if __name__ == "__main__":
    raise SystemExit(main())
