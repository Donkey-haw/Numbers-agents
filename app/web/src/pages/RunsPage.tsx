import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { STATUS_STYLES } from '../utils/statusColors';
import type { RunSummary, StageStatus } from '../types/events';

export function RunsPage() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingRunId, setDeletingRunId] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const html = document.documentElement;
    const body = document.body;
    const root = document.getElementById('root');

    const previousHtmlOverflow = html.style.overflow;
    const previousBodyOverflow = body.style.overflow;
    const previousRootOverflow = root?.style.overflow ?? '';
    const previousRootHeight = root?.style.height ?? '';

    html.style.overflow = 'auto';
    body.style.overflow = 'auto';
    if (root) {
      root.style.overflow = 'visible';
      root.style.height = 'auto';
    }

    fetch('/api/runs')
      .then((r) => r.json())
      .then((data) => {
        setRuns(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    return () => {
      html.style.overflow = previousHtmlOverflow;
      body.style.overflow = previousBodyOverflow;
      if (root) {
        root.style.overflow = previousRootOverflow;
        root.style.height = previousRootHeight;
      }
    };
  }, []);

  const statusToStageStatus = (s: string): StageStatus => {
    if (s === 'success') return 'succeeded';
    if (s === 'failed') return 'failed';
    if (s === 'running') return 'running';
    return 'pending';
  };

  const handleDeleteRun = async (runId: string) => {
    const confirmed = window.confirm(`'${runId}' run을 삭제할까요? 이 작업은 되돌릴 수 없습니다.`);
    if (!confirmed) return;

    setDeletingRunId(runId);
    try {
      const response = await fetch(`/api/runs/${encodeURIComponent(runId)}/delete`, {
        method: 'POST',
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || 'Failed to delete run');
      }
      setRuns((current) => current.filter((run) => run.run_id !== runId));
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete run';
      window.alert(message);
    } finally {
      setDeletingRunId(null);
    }
  };

  return (
    <div
      id="runs-page"
      style={{
        minHeight: '100vh',
        background: 'var(--bg-base)',
        fontFamily: 'var(--font-sans)',
        color: 'var(--text-primary)',
        padding: '48px 40px',
        overflow: 'auto',
      }}
    >
      {/* Hero header */}
      <div style={{ maxWidth: 900, margin: '0 auto' }}>
        <div style={{ marginBottom: 40, animation: 'slide-up 0.5s ease', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1
              style={{
                fontSize: 32,
                fontWeight: 800,
                marginBottom: 8,
                letterSpacing: '-0.02em',
                background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%)',
                backgroundSize: '200% 200%',
                animation: 'gradient-flow 4s ease infinite',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Pipeline Monitor
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, fontWeight: 400 }}>
              NumbersAuto 파이프라인 실행 이력 · 실시간 모니터링
            </p>
          </div>
          <button
            id="new-run-btn"
            onClick={() => navigate('/runs/new')}
            style={{
              padding: '10px 24px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              border: 'none',
              color: '#fff',
              fontSize: 14,
              fontWeight: 600,
              cursor: 'pointer',
              fontFamily: 'var(--font-sans)',
              transition: 'all 0.2s ease',
              boxShadow: '0 4px 16px rgba(59, 130, 246, 0.3)',
              flexShrink: 0,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 6px 24px rgba(59, 130, 246, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 16px rgba(59, 130, 246, 0.3)';
            }}
          >
            + 새 Run
          </button>
        </div>

        {/* Stats bar */}
        {!loading && runs.length > 0 && (
          <div
            style={{
              display: 'flex',
              gap: 16,
              marginBottom: 24,
              animation: 'slide-up 0.6s ease',
            }}
          >
            {[
              { label: '전체', value: runs.length, color: '#94a3b8' },
              { label: '성공', value: runs.filter((r) => r.final_status === 'success').length, color: '#10b981' },
              { label: '실패', value: runs.filter((r) => r.final_status === 'failed').length, color: '#ef4444' },
            ].map((stat) => (
              <div
                key={stat.label}
                style={{
                  padding: '10px 20px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'baseline',
                  gap: 8,
                }}
              >
                <span
                  style={{
                    fontSize: 20,
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)',
                    color: stat.color,
                  }}
                >
                  {stat.value}
                </span>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  {stat.label}
                </span>
              </div>
            ))}
          </div>
        )}

        {loading ? (
          <div
            style={{
              color: 'var(--text-muted)',
              padding: 64,
              textAlign: 'center',
              fontSize: 14,
            }}
          >
            <div
              style={{
                width: 200,
                height: 3,
                borderRadius: 2,
                margin: '0 auto 16px',
                background: 'linear-gradient(90deg, transparent, rgba(59,130,246,0.5), transparent)',
                backgroundSize: '200% 100%',
                animation: 'shimmer 1.5s ease-in-out infinite',
              }}
            />
            로딩 중...
          </div>
        ) : runs.length === 0 ? (
          <div
            style={{
              color: 'var(--text-muted)',
              textAlign: 'center',
              padding: 80,
              background: 'var(--bg-surface)',
              borderRadius: 'var(--radius-xl)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            아직 실행된 run이 없습니다.
          </div>
        ) : (
          <div style={{ display: 'grid', gap: 8 }}>
            {runs.map((run, i) => {
              const mapped = statusToStageStatus(run.final_status);
              const style = STATUS_STYLES[mapped];
              return (
                <div
                  key={run.run_id}
                  onClick={() => navigate(`/runs/${run.run_id}`)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 16,
                    padding: '16px 20px',
                    background: style.bgGradient,
                    backdropFilter: 'blur(16px)',
                    borderRadius: 'var(--radius-lg)',
                    border: `1px solid ${style.border}`,
                    cursor: 'pointer',
                    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                    animation: `slide-up ${0.4 + i * 0.05}s ease`,
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = `0 8px 32px ${style.glow}`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  {/* Status icon */}
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: 8,
                      background: style.iconBg,
                      border: `1px solid ${style.border}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 14,
                      color: style.text,
                      flexShrink: 0,
                    }}
                  >
                    {style.icon}
                  </div>

                  {/* Info */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontWeight: 600,
                        fontSize: 14,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        marginBottom: 2,
                      }}
                    >
                      {run.run_id}
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      {run.selected_unit ?? ''}{run.selected_unit && run.workflow_mode ? ' · ' : ''}{run.workflow_mode ?? ''}
                    </div>
                  </div>

                  {/* Status badge */}
                  <div
                    style={{
                      padding: '4px 12px',
                      borderRadius: 'var(--radius-sm)',
                      background: style.iconBg,
                      border: `1px solid ${style.border}`,
                      color: style.text,
                      fontSize: 11,
                      fontWeight: 600,
                      fontFamily: 'var(--font-mono)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      flexShrink: 0,
                    }}
                  >
                    {style.label}
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
                    {/* Time */}
                    <div
                      style={{
                        fontSize: 11,
                        color: 'var(--text-muted)',
                        fontFamily: 'var(--font-mono)',
                        minWidth: 100,
                        textAlign: 'right',
                        flexShrink: 0,
                      }}
                    >
                      {run.started_at
                        ? new Date(run.started_at).toLocaleDateString('ko-KR', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: false,
                          })
                        : '—'}
                    </div>

                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        void handleDeleteRun(run.run_id);
                      }}
                      disabled={deletingRunId === run.run_id}
                      style={{
                        padding: '6px 10px',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid rgba(239, 68, 68, 0.35)',
                        background: deletingRunId === run.run_id ? 'rgba(239, 68, 68, 0.08)' : 'rgba(15, 23, 42, 0.28)',
                        color: deletingRunId === run.run_id ? 'rgba(248, 113, 113, 0.8)' : '#f87171',
                        fontSize: 11,
                        fontWeight: 700,
                        cursor: deletingRunId === run.run_id ? 'default' : 'pointer',
                        flexShrink: 0,
                      }}
                    >
                      {deletingRunId === run.run_id ? '삭제 중...' : '삭제'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
