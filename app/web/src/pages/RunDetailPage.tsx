import { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useRunStore } from '../stores/useRunStore';
import {
  useEventStream,
  fetchAndLoadEvents,
  fetchManifest,
} from '../hooks/useEventStream';
import { RunHeader } from '../components/RunHeader';
import { RunGraph } from '../components/RunGraph';
import { EventLogPanel } from '../components/EventLogPanel';

export function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>();
  const setRunId = useRunStore((s) => s.setRunId);
  const reset = useRunStore((s) => s.reset);
  const manifest = useRunStore((s) => s.manifest);

  useEffect(() => {
    if (!runId) return;
    reset();
    setRunId(runId);
    fetchManifest(runId);
    fetchAndLoadEvents(runId);
  }, [runId, reset, setRunId]);

  useEventStream(runId ?? null);

  const isFinished =
    manifest?.final_status === 'success' ||
    manifest?.final_status === 'failed';

  return (
    <div
      id="run-detail-page"
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg-base)',
        fontFamily: 'var(--font-sans)',
        color: 'var(--text-primary)',
      }}
    >
      {/* Top nav */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '8px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          fontSize: 13,
          background: 'rgba(8, 12, 20, 0.9)',
          backdropFilter: 'blur(12px)',
        }}
      >
        <Link
          to="/"
          style={{
            color: 'var(--text-muted)',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 12,
            fontWeight: 500,
            transition: 'color 0.2s',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
        >
          ← Runs
        </Link>
        {!isFinished && manifest && (
          <span
            style={{
              marginLeft: 'auto',
              fontSize: 10,
              color: '#3b82f6',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              fontFamily: 'var(--font-mono)',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
            }}
          >
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: '#3b82f6',
                animation: 'pulse 1.5s ease-in-out infinite',
              }}
            />
            Live
          </span>
        )}
      </div>

      <RunHeader />

      {/* Main content: unified graph */}
      <div
        style={{
          flex: 1,
          minHeight: 0,
        }}
      >
        <RunGraph />
      </div>

      {/* Event log */}
      <div
        style={{
          height: 180,
          borderTop: '1px solid var(--border-subtle)',
          overflowY: 'auto',
          background: 'rgba(8, 12, 20, 0.8)',
          backdropFilter: 'blur(12px)',
        }}
      >
        <EventLogPanel />
      </div>
    </div>
  );
}
