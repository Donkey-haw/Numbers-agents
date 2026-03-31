import { useEffect, useRef } from 'react';
import { useRunStore } from '../stores/useRunStore';
import type { RunEvent } from '../types/events';

/**
 * Connects to the SSE stream for a given run and applies events
 * to the Zustand store. Automatically reconnects on error.
 */
export function useEventStream(runId: string | null) {
  const applyEvent = useRunStore((s) => s.applyEvent);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!runId) return;

    const es = new EventSource(`/api/runs/${runId}/stream`);
    esRef.current = es;

    es.onmessage = (msg) => {
      try {
        const evt: RunEvent = JSON.parse(msg.data);
        applyEvent(evt);
      } catch {
        /* ignore parse errors */
      }
    };

    es.onerror = () => {
      es.close();
      /* SSE auto-reconnect: browser retries after a short delay */
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [runId, applyEvent]);
}

/**
 * Fetches all existing events for a run and loads them into the store.
 * Use this for past/completed runs or to hydrate on page load.
 */
export async function fetchAndLoadEvents(runId: string) {
  const res = await fetch(`/api/runs/${runId}/events`);
  if (!res.ok) return;
  const events: RunEvent[] = await res.json();
  useRunStore.getState().loadEvents(events);
}

/**
 * Fetches the run manifest and loads it into the store.
 */
export async function fetchManifest(runId: string) {
  const res = await fetch(`/api/runs/${runId}`);
  if (!res.ok) return;
  const manifest = await res.json();
  useRunStore.getState().setManifest(manifest);
}
