"""FastAPI server for NumbersAuto pipeline monitoring.

Reads existing orchestrator outputs (run_manifest.json, run_events.jsonl)
in read-only mode and exposes them via REST + SSE APIs.
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SERVER_DIR = Path(__file__).resolve().parent
APP_DIR = SERVER_DIR.parent
PROJECT_ROOT = APP_DIR.parent

# Make scripts importable so we can reuse contracts
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from run_manager import router as run_router  # noqa: E402
from event_streamer import router as event_router  # noqa: E402

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="NumbersAuto Pipeline Monitor",
    description="N8N-style realtime monitoring API for the NumbersAuto pipeline.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run_router, prefix="/api")
app.include_router(event_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
