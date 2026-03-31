"""Lesson-level pipelined DAG scheduler.

Replaces stage-barrier execution with per-lesson dependency chains.
Each lesson independently progresses through:

    lesson_analysis → lesson_review → activity_plan → activity_review → html_card

All lesson chains run concurrently.  A global barrier fires only after
every lesson's html_card job completes.
"""

from __future__ import annotations

import concurrent.futures
import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pipeline_contracts as contracts
import orchestrator_events


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class LessonJob:
    """Single unit of work in the lesson pipeline."""

    job_id: str
    section_key: str
    stage: str
    status: str = "pending"  # pending → ready → running → succeeded / failed
    depends_on: list[str] = field(default_factory=list)
    result: dict | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------
class LessonPipelineScheduler:
    """Build and execute a per-lesson DAG using a thread-pool."""

    def __init__(
        self,
        *,
        sections: list[dict],
        lesson_stages: list[str] | None = None,
        max_workers: int = 4,
        run_root: Path,
        run_id: str,
        stage_executors: dict[str, Callable[..., dict]],
        stop_after: str | None = None,
    ) -> None:
        self._sections = sections
        self._lesson_stages = lesson_stages or list(contracts.LESSON_LEVEL_STAGES)
        self._max_workers = max(1, max_workers)
        self._run_root = run_root
        self._run_id = run_id
        self._stage_executors = stage_executors
        self._stop_after = stop_after

        # map job_id → LessonJob
        self._jobs: dict[str, LessonJob] = {}
        # map section_key → ordered list of job_ids
        self._section_chains: dict[str, list[str]] = {}
        self._lock = threading.Lock()

        self._build_graph()

    # -- graph construction --------------------------------------------------

    def _build_graph(self) -> None:
        for section in self._sections:
            section_key = contracts.section_artifact_stem(section)
            prev_job_id: str | None = None
            chain: list[str] = []

            for stage in self._lesson_stages:
                job_id = f"{stage}::{section_key}"
                depends = [prev_job_id] if prev_job_id else []
                job = LessonJob(
                    job_id=job_id,
                    section_key=section_key,
                    stage=stage,
                    depends_on=depends,
                )
                self._jobs[job_id] = job
                chain.append(job_id)
                prev_job_id = job_id

            self._section_chains[section_key] = chain

        # Mark initially ready jobs (those with no dependencies)
        for job in self._jobs.values():
            if not job.depends_on:
                job.status = "ready"

    # -- queries -------------------------------------------------------------

    def build_job_graph(self) -> dict:
        """Return a JSON-serialisable snapshot of the full job graph."""
        return {
            "schema_version": contracts.SCHEMA_VERSION,
            "run_id": self._run_id,
            "generated_at": contracts.utc_now(),
            "jobs": [
                {
                    "job_id": j.job_id,
                    "section_key": j.section_key,
                    "stage": j.stage,
                    "status": j.status,
                    "depends_on": j.depends_on,
                }
                for j in self._jobs.values()
            ],
        }

    def get_ready_jobs(self) -> list[LessonJob]:
        with self._lock:
            return [j for j in self._jobs.values() if j.status == "ready"]

    def all_lesson_jobs_done(self) -> bool:
        with self._lock:
            return all(
                j.status in ("succeeded", "succeeded_with_warning")
                for j in self._jobs.values()
            )

    def has_failures(self) -> bool:
        with self._lock:
            return any(j.status in ("failed", "blocked") for j in self._jobs.values())

    # -- mutations -----------------------------------------------------------

    def mark_running(self, job_id: str) -> None:
        with self._lock:
            self._jobs[job_id].status = "running"

    def mark_completed(self, job_id: str, result: dict) -> None:
        with self._lock:
            job = self._jobs[job_id]
            # Determine final status from result
            if result.get("blocked_count", 0) > 0:
                job.status = "blocked"
            elif result.get("warning_count", 0) > 0 or result.get("fallback_used"):
                job.status = "succeeded_with_warning"
            else:
                job.status = "succeeded"
            job.result = result
            self._unlock_downstream(job_id)

    def mark_failed(self, job_id: str, error: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "failed"
            job.error = error
            # Block downstream jobs in same chain
            self._block_downstream(job_id)

    def _unlock_downstream(self, completed_job_id: str) -> None:
        """Must be called while holding self._lock."""
        for job in self._jobs.values():
            if job.status != "pending":
                continue
            if completed_job_id in job.depends_on:
                # Check if ALL dependencies are done
                all_deps_done = all(
                    self._jobs[dep].status in ("succeeded", "succeeded_with_warning")
                    for dep in job.depends_on
                )
                if all_deps_done:
                    job.status = "ready"

    def _block_downstream(self, failed_job_id: str) -> None:
        """Must be called while holding self._lock."""
        for job in self._jobs.values():
            if job.status == "pending" and failed_job_id in job.depends_on:
                job.status = "blocked"
                job.error = f"blocked by {failed_job_id}"
                self._block_downstream(job.job_id)

    # -- stage result aggregation --------------------------------------------

    def aggregate_stage_results(self) -> dict[str, dict]:
        """Aggregate per-stage results across all lessons for manifest updates."""
        stage_results: dict[str, dict] = {}
        for stage in self._lesson_stages:
            fallback_count = 0
            warning_count = 0
            blocked_count = 0
            fallback_category_counts: dict[str, int] = {}

            for job in self._jobs.values():
                if job.stage != stage:
                    continue
                if job.result:
                    if job.result.get("fallback_used"):
                        fallback_count += 1
                        cat = job.result.get("fallback_category") or "unknown"
                        fallback_category_counts[cat] = fallback_category_counts.get(cat, 0) + 1
                    if job.result.get("warning_used") or job.result.get("warning_count"):
                        warning_count += 1
                    if job.result.get("blocked_used") or job.result.get("blocked_count"):
                        blocked_count += 1
                elif job.status in ("failed", "blocked"):
                    blocked_count += 1

            stage_results[stage] = {
                "fallback_count": fallback_count,
                "warning_count": warning_count,
                "blocked_count": blocked_count,
                "fallback_category_counts": fallback_category_counts,
            }

        return stage_results

    # -- main execution loop -------------------------------------------------

    def run(self) -> dict[str, dict]:
        """Execute all lesson-level jobs respecting dependencies.

        Returns aggregated stage results.
        """
        # Write initial job graph
        contracts.write_json(self._run_root / "job_graph.json", self.build_job_graph())

        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            pending_futures: dict[concurrent.futures.Future, str] = {}

            while True:
                # Submit ready jobs
                ready = self.get_ready_jobs()
                for job in ready:
                    self.mark_running(job.job_id)
                    orchestrator_events.append_event(
                        run_root=self._run_root,
                        run_id=self._run_id,
                        event_type="job_started",
                        stage=job.stage,
                        lesson_id=job.section_key,
                        status="running",
                        payload={"job_id": job.job_id},
                    )
                    future = executor.submit(self._execute_job, job)
                    pending_futures[future] = job.job_id

                if not pending_futures:
                    # No running jobs and no ready jobs — we're done
                    break

                # Wait for at least one to complete
                done, _ = concurrent.futures.wait(
                    pending_futures.keys(),
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )

                for future in done:
                    job_id = pending_futures.pop(future)
                    try:
                        result = future.result()
                        self.mark_completed(job_id, result)
                        orchestrator_events.append_event(
                            run_root=self._run_root,
                            run_id=self._run_id,
                            event_type="job_finished",
                            stage=self._jobs[job_id].stage,
                            lesson_id=self._jobs[job_id].section_key,
                            status=self._jobs[job_id].status,
                            payload={
                                "job_id": job_id,
                                "result_keys": list(result.keys()) if result else [],
                            },
                        )
                    except Exception as exc:
                        self.mark_failed(job_id, str(exc))
                        orchestrator_events.append_event(
                            run_root=self._run_root,
                            run_id=self._run_id,
                            event_type="job_finished",
                            stage=self._jobs[job_id].stage,
                            lesson_id=self._jobs[job_id].section_key,
                            status="failed",
                            payload={
                                "job_id": job_id,
                                "error": str(exc),
                            },
                        )

                # Update job graph snapshot
                contracts.write_json(self._run_root / "job_graph.json", self.build_job_graph())

                # Check stop_after: if all jobs for the target stage are done, stop
                if self._stop_after and self._stop_after in self._lesson_stages:
                    stage_idx = self._lesson_stages.index(self._stop_after)
                    stages_to_check = self._lesson_stages[: stage_idx + 1]
                    all_done = all(
                        self._jobs[jid].status in ("succeeded", "succeeded_with_warning", "failed", "blocked")
                        for jid in self._jobs
                        if self._jobs[jid].stage in stages_to_check
                    )
                    if all_done:
                        # Cancel remaining pending/ready jobs
                        with self._lock:
                            for j in self._jobs.values():
                                if j.status in ("pending", "ready"):
                                    j.status = "blocked"
                                    j.error = f"stopped after {self._stop_after}"
                        break

        # Final snapshot
        contracts.write_json(self._run_root / "job_graph.json", self.build_job_graph())

        # Emit lesson_pipeline_completed event
        orchestrator_events.append_event(
            run_root=self._run_root,
            run_id=self._run_id,
            event_type="lesson_pipeline_completed",
            status="succeeded" if self.all_lesson_jobs_done() else "partial",
            payload={
                "total_jobs": len(self._jobs),
                "succeeded": sum(1 for j in self._jobs.values() if j.status in ("succeeded", "succeeded_with_warning")),
                "failed": sum(1 for j in self._jobs.values() if j.status in ("failed", "blocked")),
            },
        )

        return self.aggregate_stage_results()

    def _execute_job(self, job: LessonJob) -> dict:
        """Dispatch a single job to the appropriate stage executor."""
        executor_fn = self._stage_executors.get(job.stage)
        if executor_fn is None:
            raise ValueError(f"No executor registered for stage: {job.stage}")
        return executor_fn(section_key=job.section_key)
