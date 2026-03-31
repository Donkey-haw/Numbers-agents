import { useRunStore } from '../stores/useRunStore';
import { STAGE_LABELS } from '../types/events';
import { STATUS_STYLES } from '../utils/statusColors';

export function AgentJobPanel() {
  const manifest = useRunStore((s) => s.manifest);
  const lessonStates = useRunStore((s) => s.lessonStates);

  if (!manifest) return null;

  const stagesWithJobs = manifest.stage_order.filter((stage) => {
    const jobs = lessonStates[stage];
    const isGlobal = (manifest.status_summary || []).some(s => s.stage === stage && (s.stage === 'curriculum_analysis_agent' || s.stage === 'pdf_extract_agent'));
    return (jobs && Object.keys(jobs).length > 0) || isGlobal;
  });

  return (
    <div
      style={{
        padding: 20,
        borderTop: '1px solid var(--border-subtle)',
      }}
    >
      <div
        style={{
          fontSize: 10,
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          color: 'var(--text-muted)',
          marginBottom: 12,
          fontFamily: 'var(--font-mono)',
        }}
      >
        Agent Jobs
      </div>

      {stagesWithJobs.length === 0 ? (
        <div style={{ color: 'var(--text-muted)', fontSize: 12, lineHeight: 1.6 }}>
          병렬 agent job이 아직 시작되지 않았습니다.
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {stagesWithJobs.map((stage) => {
            const jobs = Object.values(lessonStates[stage] ?? {});
            const runningCount = jobs.filter((job) => job.status === 'running').length;
            const doneCount = jobs.filter((job) => job.status !== 'running' && job.status !== 'pending').length;

            return (
              <div
                key={stage}
                style={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '10px 12px',
                    borderBottom: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
                    {STAGE_LABELS[stage] ?? stage}
                  </div>
                  <div
                    style={{
                      fontSize: 10,
                      color: 'var(--text-muted)',
                      fontFamily: 'var(--font-mono)',
                    }}
                  >
                    {doneCount}/{jobs.length}
                    {runningCount > 0 ? ` · ▶${runningCount}` : ''}
                  </div>
                </div>

                <div style={{ padding: 8, display: 'grid', gap: 6 }}>
                    {jobs.length === 0 ? (
                      (() => {
                        const stageSummary = (manifest.status_summary || []).find(s => s.stage === stage);
                        if (!stageSummary) return null;
                        const style = STATUS_STYLES[stageSummary.status] ?? STATUS_STYLES.pending;
                        return (
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              gap: 8,
                              padding: '8px 10px',
                              borderRadius: 'var(--radius-sm)',
                              background: style.bgGradient,
                              border: `1px solid ${style.border}`,
                            }}
                          >
                            <div style={{ minWidth: 0 }}>
                              <div style={{ fontSize: 12, color: 'var(--text-primary)', fontWeight: 600 }}>
                                전역 처리 (Global)
                              </div>
                            </div>
                            <div style={{ fontSize: 10, color: style.text, fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                              {style.icon} {style.label}
                            </div>
                          </div>
                        );
                      })()
                    ) : (
                      jobs.map((job) => {
                        const style = STATUS_STYLES[job.status] ?? STATUS_STYLES.pending;
                        return (
                          <div
                            key={`${stage}:${job.lesson_id}`}
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              gap: 8,
                              padding: '8px 10px',
                              borderRadius: 'var(--radius-sm)',
                              background: style.bgGradient,
                              border: `1px solid ${style.border}`,
                            }}
                          >
                            <div style={{ minWidth: 0 }}>
                              <div
                                style={{
                                  fontSize: 12,
                                  color: 'var(--text-primary)',
                                  fontWeight: 600,
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap',
                                }}
                              >
                                {job.lesson_id}
                              </div>
                              <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                                {job.fallback_used ? 'fallback' : 'direct'}
                                {job.warning_used ? ' · warning' : ''}
                              </div>
                            </div>
                            <div
                              style={{
                                fontSize: 10,
                                color: style.text,
                                fontFamily: 'var(--font-mono)',
                                fontWeight: 700,
                                flexShrink: 0,
                              }}
                            >
                              {style.icon} {style.label}
                            </div>
                          </div>
                        );
                      })
                    )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
