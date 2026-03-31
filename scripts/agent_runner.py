import argparse
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import pipeline_contracts as contracts  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402


CONFIG_PATH = PROJECT_ROOT / "agent_runtime.config.json"


@dataclass
class RunnerSettings:
    runner: str
    model: str | None
    fallback_runner: str | None
    fallback_model: str | None
    max_parallel_jobs: int | None
    timeout_sec: int | None
    idle_timeout_sec: int | None


@dataclass
class JobSpec:
    job_id: str
    stage: str
    runner: str
    model: str | None
    command: list[str] | None
    cwd: str
    input_path: str | None
    output_path: str | None
    status_path: str
    stdout_log: str
    stderr_log: str
    prompt_path: str | None
    prompt_text: str | None
    output_schema_path: str | None
    cli_bin: str | None
    approval_mode: str | None
    extensions: list[str]
    timeout_sec: int | None
    idle_timeout_sec: int | None
    metadata: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-spec", required=True, help="Path to job spec JSON")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict | list) -> None:
    contracts.write_json(path, payload)


def normalize_timeout(value: int | None) -> int | None:
    if value in (None, 0):
        return None
    return max(1, int(value))


def load_runtime_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"defaults": {}, "agents": {}}
    return read_json(CONFIG_PATH)


def resolve_runner_settings(stage: str) -> RunnerSettings:
    config = load_runtime_config()
    defaults = config.get("defaults", {})
    agent_overrides = config.get("agents", {}).get(stage, {})
    merged = {**defaults, **agent_overrides}
    return RunnerSettings(
        runner=merged.get("runner", "python"),
        model=merged.get("model"),
        fallback_runner=merged.get("fallback_runner"),
        fallback_model=merged.get("fallback_model"),
        max_parallel_jobs=merged.get("max_parallel_jobs"),
        timeout_sec=normalize_timeout(merged.get("timeout_sec")),
        idle_timeout_sec=normalize_timeout(merged.get("idle_timeout_sec")),
    )


def load_job_spec(path: Path) -> JobSpec:
    payload = read_json(path)
    stage = payload["stage"]
    settings = resolve_runner_settings(stage)
    return JobSpec(
        job_id=payload["job_id"],
        stage=stage,
        runner=payload.get("runner") or settings.runner,
        model=payload.get("model", settings.model),
        command=list(payload["command"]) if payload.get("command") else None,
        cwd=payload.get("cwd", str(PROJECT_ROOT)),
        input_path=payload.get("input_path"),
        output_path=payload.get("output_path"),
        status_path=payload["status_path"],
        stdout_log=payload["stdout_log"],
        stderr_log=payload["stderr_log"],
        prompt_path=payload.get("prompt_path"),
        prompt_text=payload.get("prompt_text"),
        output_schema_path=payload.get("output_schema_path"),
        cli_bin=payload.get("cli_bin"),
        approval_mode=payload.get("approval_mode"),
        extensions=list(payload.get("extensions", [])),
        timeout_sec=normalize_timeout(payload.get("timeout_sec", settings.timeout_sec)),
        idle_timeout_sec=normalize_timeout(payload.get("idle_timeout_sec", settings.idle_timeout_sec)),
        metadata=payload.get("metadata", {}),
    )


def build_initial_status(spec: JobSpec) -> dict:
    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "job_id": spec.job_id,
        "stage": spec.stage,
        "runner": spec.runner,
        "model": spec.model,
        "requested_runner": spec.runner,
        "requested_model": spec.model,
        "status": "running",
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "command": spec.command,
        "cwd": spec.cwd,
        "input_path": spec.input_path,
        "output_path": spec.output_path,
        "stdout_log": spec.stdout_log,
        "stderr_log": spec.stderr_log,
        "timeout_sec": spec.timeout_sec,
        "idle_timeout_sec": spec.idle_timeout_sec,
        "metadata": spec.metadata,
        "attempts": [],
        "fallback_used": False,
        "errors": [],
    }


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_log_tail(path: Path, limit: int = 2000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if len(text) <= limit:
        return text.strip()
    return text[-limit:].strip()


def terminate_process_tree(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=3)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    process.wait(timeout=3)


def load_prompt_text(spec: JobSpec) -> str:
    if spec.prompt_text:
        return spec.prompt_text
    if spec.prompt_path:
        return Path(spec.prompt_path).read_text(encoding="utf-8")
    raise ValueError(f"Job '{spec.job_id}' requires prompt_text or prompt_path for runner '{spec.runner}'")


def build_command(spec: JobSpec, *, runner: str, model: str | None) -> tuple[list[str], str | None]:
    if runner == "python":
        if not spec.command:
            raise ValueError(f"Job '{spec.job_id}' has no command for python runner")
        return spec.command, None

    if runner == "gemini":
        prompt = load_prompt_text(spec)
        cli_bin = spec.cli_bin or "gemini"
        command = [cli_bin, "-o", "json", "--approval-mode", spec.approval_mode or "yolo"]
        if model:
            command.extend(["-m", model])
        if spec.extensions:
            command.extend(["-e", *spec.extensions])
        command.extend(["-p", prompt])
        return command, None

    if runner == "codex":
        prompt = load_prompt_text(spec)
        cli_bin = spec.cli_bin or "codex"
        command = [
            cli_bin,
            "exec",
            "-",
            "-C",
            spec.cwd,
            "--skip-git-repo-check",
            "--ephemeral",
            "--sandbox",
            "workspace-write",
        ]
        if model:
            command.extend(["-m", model])
        if spec.output_schema_path:
            command.extend(["--output-schema", spec.output_schema_path])
        if spec.output_path:
            command.extend(["--output-last-message", spec.output_path])
        return command, prompt

    raise ValueError(f"Unsupported runner '{runner}' for job '{spec.job_id}'")


def finalize_runner_output(spec: JobSpec, *, runner: str) -> None:
    if not spec.output_path:
        return
    output_path = Path(spec.output_path)

    if runner == "gemini":
        raw_text = Path(spec.stdout_log).read_text(encoding="utf-8")
        parsed = gemini_pipeline.extract_json_from_response_text(raw_text)
        write_json(output_path, parsed)
        return

    if not output_path.exists():
        raise RuntimeError(f"Job '{spec.job_id}' did not produce expected output: {output_path}")

    if runner == "codex":
        raw_text = output_path.read_text(encoding="utf-8").strip()
        if not raw_text:
            raise RuntimeError(f"Job '{spec.job_id}' produced empty output at {output_path}")
        parsed = json.loads(raw_text)
        write_json(output_path, parsed)


def run_process(
    *,
    spec: JobSpec,
    command: list[str],
    stdin_text: str | None,
    runner: str,
    model: str | None,
) -> None:
    status_path = Path(spec.status_path)
    stdout_log_path = Path(spec.stdout_log)
    stderr_log_path = Path(spec.stderr_log)
    ensure_parent(status_path)
    ensure_parent(stdout_log_path)
    ensure_parent(stderr_log_path)

    start_monotonic = time.monotonic()
    last_activity = start_monotonic

    with stdout_log_path.open("w", encoding="utf-8") as stdout_handle, stderr_log_path.open("w", encoding="utf-8") as stderr_handle:
        process = subprocess.Popen(
            command,
            cwd=spec.cwd,
            stdin=subprocess.PIPE if stdin_text is not None else None,
            stdout=stdout_handle,
            stderr=stderr_handle,
            text=True,
            start_new_session=True,
        )
        if stdin_text is not None and process.stdin is not None:
            process.stdin.write(stdin_text)
            process.stdin.close()
        while True:
            result = process.poll()
            now = time.monotonic()
            stdout_handle.flush()
            stderr_handle.flush()
            try:
                if stdout_log_path.exists():
                    stdout_mtime = stdout_log_path.stat().st_mtime
                    last_activity = max(last_activity, stdout_mtime)
                if stderr_log_path.exists():
                    stderr_mtime = stderr_log_path.stat().st_mtime
                    last_activity = max(last_activity, stderr_mtime)
            except FileNotFoundError:
                pass

            if result is not None:
                break

            if spec.timeout_sec is not None and now - start_monotonic > spec.timeout_sec:
                terminate_process_tree(process)
                raise TimeoutError(f"Job '{spec.job_id}' timed out after {spec.timeout_sec} seconds")

            if spec.idle_timeout_sec is not None and now - last_activity > spec.idle_timeout_sec:
                terminate_process_tree(process)
                raise TimeoutError(
                    f"Job '{spec.job_id}' idle-timed out after {spec.idle_timeout_sec} seconds "
                    f"(runner={runner}, model={model})"
                )

            time.sleep(0.2)

    if process.returncode != 0:
        stderr_tail = read_log_tail(stderr_log_path)
        detail = f" stderr_tail={stderr_tail}" if stderr_tail else ""
        raise RuntimeError(
            f"Job '{spec.job_id}' failed with exit code {process.returncode} (runner={runner}, model={model}){detail}"
        )

    finalize_runner_output(spec, runner=runner)


def attempt_job(spec: JobSpec, *, runner: str, model: str | None, status: dict) -> dict:
    command, stdin_text = build_command(spec, runner=runner, model=model)
    attempt = {
        "runner": runner,
        "model": model,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "status": "running",
        "errors": [],
        "command": command,
    }
    status["runner"] = runner
    status["model"] = model
    status["command"] = command
    status["attempts"].append(attempt)
    write_json(Path(spec.status_path), status)
    try:
        run_process(spec=spec, command=command, stdin_text=stdin_text, runner=runner, model=model)
    except Exception as exc:
        attempt["status"] = "failed"
        attempt["finished_at"] = contracts.utc_now()
        attempt["errors"] = [str(exc)]
        raise
    attempt["status"] = "succeeded"
    attempt["finished_at"] = contracts.utc_now()
    return status


def run_job(spec: JobSpec) -> dict:
    status_path = Path(spec.status_path)
    status = build_initial_status(spec)
    write_json(status_path, status)
    primary_error: Exception | None = None
    try:
        status = attempt_job(spec, runner=spec.runner, model=spec.model, status=status)
        status["status"] = "succeeded"
        status["finished_at"] = contracts.utc_now()
        write_json(status_path, status)
        return status
    except Exception as exc:
        primary_error = exc
        status["errors"] = [str(exc)]
        write_json(status_path, status)

    settings = resolve_runner_settings(spec.stage)
    fallback_runner = settings.fallback_runner
    fallback_model = settings.fallback_model
    if not fallback_runner or fallback_runner == spec.runner:
        raise primary_error  # type: ignore[misc]

    status["fallback_used"] = True
    status["errors"] = []
    write_json(status_path, status)
    try:
        status = attempt_job(spec, runner=fallback_runner, model=fallback_model, status=status)
    except Exception as fallback_exc:
        status["status"] = "failed"
        status["finished_at"] = contracts.utc_now()
        status["errors"] = [str(primary_error), str(fallback_exc)]
        write_json(status_path, status)
        raise fallback_exc

    status["status"] = "succeeded"
    status["finished_at"] = contracts.utc_now()
    write_json(status_path, status)
    return status


def main() -> int:
    args = parse_args()
    spec = load_job_spec(Path(args.job_spec))
    try:
        result = run_job(spec)
    except Exception as exc:
        status_path = Path(spec.status_path)
        if status_path.exists():
            status = read_json(status_path)
        else:
            status = build_initial_status(spec)
        status["status"] = "failed"
        status["finished_at"] = contracts.utc_now()
        status["errors"] = [str(exc)]
        write_json(status_path, status)
        raise
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
