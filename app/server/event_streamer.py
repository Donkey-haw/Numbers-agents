"""Event streaming — read JSONL event logs and push via SSE.

This module is a pure read-only consumer of the event files produced
by orchestrator_events.py. It never writes to or modifies those files.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RUNS_DIR = PROJECT_ROOT / "artifacts" / "runs"

router = APIRouter()

POLL_INTERVAL_SEC = 0.3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _events_path(run_id: str) -> Path:
    return RUNS_DIR / run_id / "events" / "run_events.jsonl"


def _read_all_events(jsonl_path: Path) -> list[dict[str, Any]]:
    """Read all events from a JSONL file."""
    if not jsonl_path.exists():
        return []
    events: list[dict[str, Any]] = []
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


async def _tail_events(jsonl_path: Path) -> AsyncGenerator[dict[str, Any], None]:
    """Async generator that tails a JSONL file, yielding new events.

    Yields existing events first, then polls for new lines until
    a ``run_finished`` event is encountered.
    """
    last_pos = 0

    # Wait for the file to appear (run may just be starting)
    for _ in range(100):  # ~30 seconds max wait
        if jsonl_path.exists():
            break
        await asyncio.sleep(POLL_INTERVAL_SEC)

    if not jsonl_path.exists():
        return

    while True:
        try:
            with jsonl_path.open("r", encoding="utf-8") as fh:
                fh.seek(last_pos)
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    yield event
                    if event.get("event_type") == "run_finished":
                        return
                last_pos = fh.tell()
        except OSError:
            pass
        await asyncio.sleep(POLL_INTERVAL_SEC)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/runs/{run_id}/events")
async def get_events(run_id: str) -> list[dict[str, Any]]:
    """Return all recorded events for a run."""
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        raise HTTPException(404, f"Run not found: {run_id}")
    return _read_all_events(_events_path(run_id))


@router.get("/runs/{run_id}/stream")
async def stream_events(run_id: str):
    """SSE stream that tails the event JSONL file in realtime."""
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        raise HTTPException(404, f"Run not found: {run_id}")

    async def event_generator():
        async for event in _tail_events(_events_path(run_id)):
            yield {"data": json.dumps(event, ensure_ascii=False)}

    return EventSourceResponse(event_generator())
