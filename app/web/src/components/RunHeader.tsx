import { useState } from 'react';
import { useRunStore } from '../stores/useRunStore';

export function RunHeader() {
  const manifest = useRunStore((s) => s.manifest);
  const nodeStates = useRunStore((s) => s.nodeStates);
  const [cancelling, setCancelling] = useState(false);

  if (!manifest) return null;

  const total = manifest.stage_order.length;
  const completed = manifest.stage_order.filter((s) => {
    const st = nodeStates[s];
    return st === 'succeeded' || st === 'succeeded_with_warning';
  }).length;
  const running = manifest.stage_order.filter(
    (s) => nodeStates[s] === 'running',
  ).length;
  const failed = manifest.stage_order.filter(
    (s) => nodeStates[s] === 'failed' || nodeStates[s] === 'blocked',
  ).length;
  const progressPct = total > 0 ? Math.round((completed / total) * 100) : 0;

  const finalStatus = manifest.final_status;
  const isFinished = finalStatus === 'success' || finalStatus === 'failed';
  const isRunning = !isFinished && running > 0;

  const barColor =
    finalStatus === 'failed'
      ? 'linear-gradient(90deg, #ef4444, #f87171)'
      : finalStatus === 'success'
        ? 'linear-gradient(90deg, #10b981, #34d399)'
        : 'linear-gradient(90deg, #3b82f6, #818cf8)';

  const handleCancel = async () => {
    if (!manifest.run_id || cancelling) return;
    setCancelling(true);
    try {
      await fetch(`/api/runs/${manifest.run_id}/cancel`, { method: 'POST' });
    } catch { /* ignore */ }
    finally { setCancelling(false); }
  };

  return (
    <div
      id="run-header"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        padding: '14px 24px',
        background: 'rgba(13, 19, 32, 0.85)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: '1px solid var(--border-subtle)',
        fontFamily: 'var(--font-sans)',
        color: 'var(--text-primary)',
        fontSize: 13,
      }}
    >
      {/* Status orb */}
      <div
        style={{
          position: 'relative',
          width: 10,
          height: 10,
          flexShrink: 0,
        }}
      >
        {isRunning && (
          <div
            style={{
              position: 'absolute',
              inset: -3,
              borderRadius: '50%',
              background: 'rgba(59, 130, 246, 0.3)',
              animation: 'pulse 2s ease-in-out infinite',
            }}
          />
        )}
        <div
          style={{
            position: 'relative',
            width: 10,
            height: 10,
            borderRadius: '50%',
            background: isRunning
              ? '#3b82f6'
              : finalStatus === 'success'
                ? '#10b981'
                : finalStatus === 'failed'
                  ? '#ef4444'
                  : '#475569',
          }}
        />
      </div>

      {/* Run ID */}
      <div
        style={{
          fontWeight: 600,
          fontSize: 14,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          maxWidth: 320,
        }}
      >
        {manifest.run_id}
      </div>

      {/* Mode badge */}
      <div
        style={{
          padding: '3px 10px',
          borderRadius: 'var(--radius-sm)',
          background: 'rgba(139, 92, 246, 0.1)',
          border: '1px solid rgba(139, 92, 246, 0.2)',
          color: '#a78bfa',
          fontSize: 11,
          fontWeight: 600,
          fontFamily: 'var(--font-mono)',
          letterSpacing: '0.03em',
          flexShrink: 0,
        }}
      >
        {manifest.workflow_mode}
      </div>

      {/* Unit name */}
      {manifest.selected_unit && (
        <div
          style={{
            color: 'var(--text-tertiary)',
            fontSize: 12,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {manifest.selected_unit}
        </div>
      )}

      <div style={{ flex: 1 }} />

      {/* Stage counters */}
      <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
        {completed > 0 && (
          <span
            style={{
              fontSize: 11,
              color: '#6ee7b7',
              fontFamily: 'var(--font-mono)',
              fontWeight: 500,
            }}
          >
            ✓{completed}
          </span>
        )}
        {running > 0 && (
          <span
            style={{
              fontSize: 11,
              color: '#93c5fd',
              fontFamily: 'var(--font-mono)',
              fontWeight: 500,
            }}
          >
            ▶{running}
          </span>
        )}
        {failed > 0 && (
          <span
            style={{
              fontSize: 11,
              color: '#fca5a5',
              fontFamily: 'var(--font-mono)',
              fontWeight: 500,
            }}
          >
            ✕{failed}
          </span>
        )}
      </div>

      {/* Cancel button */}
      {isRunning && (
        <button
          id="cancel-btn"
          onClick={handleCancel}
          disabled={cancelling}
          style={{
            padding: '5px 16px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            background: 'rgba(239, 68, 68, 0.1)',
            color: '#fca5a5',
            fontSize: 12,
            fontWeight: 600,
            cursor: cancelling ? 'not-allowed' : 'pointer',
            opacity: cancelling ? 0.6 : 1,
            fontFamily: 'var(--font-sans)',
            transition: 'all 0.2s ease',
          }}
        >
          {cancelling ? '취소 중...' : '⏹ 중단'}
        </button>
      )}

      {/* Open output */}
      {isFinished && manifest.final_output_file && (
        <button
          id="open-output-btn"
          onClick={() => window.open(`/api/runs/${manifest.run_id}`, '_blank')}
          style={{
            padding: '5px 16px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            background: 'rgba(16, 185, 129, 0.1)',
            color: '#6ee7b7',
            fontSize: 12,
            fontWeight: 600,
            cursor: 'pointer',
            fontFamily: 'var(--font-sans)',
            transition: 'all 0.2s ease',
          }}
        >
          📂 출력
        </button>
      )}

      {/* Progress bar */}
      <div
        style={{
          width: 140,
          height: 4,
          borderRadius: 2,
          background: 'rgba(255,255,255,0.06)',
          overflow: 'hidden',
          flexShrink: 0,
        }}
      >
        <div
          style={{
            width: `${progressPct}%`,
            height: '100%',
            borderRadius: 2,
            background: barColor,
            transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        />
      </div>
      <span
        style={{
          fontSize: 11,
          color: 'var(--text-tertiary)',
          minWidth: 32,
          textAlign: 'right',
          fontFamily: 'var(--font-mono)',
          fontWeight: 500,
          flexShrink: 0,
        }}
      >
        {progressPct}%
      </span>

      {manifest.finished_at && (
        <span
          style={{
            fontSize: 11,
            color: 'var(--text-muted)',
            fontFamily: 'var(--font-mono)',
            flexShrink: 0,
          }}
        >
          {new Date(manifest.finished_at).toLocaleTimeString('ko-KR', { hour12: false })}
        </span>
      )}
    </div>
  );
}
