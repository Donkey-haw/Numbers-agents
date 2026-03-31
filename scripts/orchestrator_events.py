import json
import uuid
from pathlib import Path

import pipeline_contracts as contracts


EVENT_TYPES = {
    "run_created",
    "run_started",
    "stage_started",
    "stage_finished",
    "lesson_started",
    "lesson_finished",
    "job_started",
    "job_finished",
    "lesson_pipeline_completed",
    "run_finished",
}


def ensure_event_dirs(run_root: Path) -> Path:
    events_dir = run_root / "events"
    events_dir.mkdir(parents=True, exist_ok=True)
    return events_dir / "run_events.jsonl"


def append_event(
    *,
    run_root: Path,
    run_id: str,
    event_type: str,
    stage: str | None = None,
    status: str | None = None,
    lesson_id: str | None = None,
    payload: dict | None = None,
) -> dict:
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unsupported event_type: {event_type}")
    event = {
        "event_id": f"evt_{uuid.uuid4().hex}",
        "run_id": run_id,
        "timestamp": contracts.utc_now(),
        "event_type": event_type,
        "stage": stage,
        "lesson_id": lesson_id,
        "status": status,
        "payload": payload or {},
    }
    event_path = ensure_event_dirs(run_root)
    with event_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event
