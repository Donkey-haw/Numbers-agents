import { useRunStore } from '../stores/useRunStore';
import { STAGE_LABELS } from '../types/events';
import { STATUS_STYLES } from '../utils/statusColors';

export function LessonSubnodeGroup({ stage }: { stage: string }) {
  const lessonStates = useRunStore((s) => s.lessonStates[stage]);
  const expanded = useRunStore((s) => s.expandedNodes.has(stage));
  const toggleExpand = useRunStore((s) => s.toggleExpand);

  if (!lessonStates || Object.keys(lessonStates).length === 0) return null;

  const lessons = Object.values(lessonStates);
  const done = lessons.filter(
    (l) => l.status !== 'running' && l.status !== 'pending',
  ).length;
  const total = lessons.length;
  const hasFallback = lessons.some((l) => l.fallback_used);

  return (
    <div
      style={{
        marginTop: 4,
        background: 'var(--bg-elevated)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        overflow: 'hidden',
      }}
    >
      <button
        onClick={() => toggleExpand(stage)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 14px',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          color: 'var(--text-secondary)',
          fontSize: 12,
          fontFamily: 'var(--font-sans)',
          fontWeight: 500,
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 11, opacity: 0.6 }}>📚</span>
          {STAGE_LABELS[stage] ?? stage} 차시
          <span
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
              color: 'var(--text-muted)',
            }}
          >
            ({done}/{total})
          </span>
        </span>
        <span style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          {hasFallback && (
            <span
              style={{
                fontSize: 9,
                fontWeight: 700,
                color: '#fdba74',
                background: 'rgba(249, 115, 22, 0.1)',
                border: '1px solid rgba(249, 115, 22, 0.2)',
                borderRadius: 4,
                padding: '1px 5px',
                fontFamily: 'var(--font-mono)',
                letterSpacing: '0.05em',
              }}
            >
              FB
            </span>
          )}
          <span
            style={{
              transform: expanded ? 'rotate(180deg)' : 'rotate(0)',
              transition: 'transform 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
              fontSize: 10,
              opacity: 0.5,
            }}
          >
            ▾
          </span>
        </span>
      </button>

      {expanded && (
        <div style={{ padding: '0 8px 8px' }}>
          {lessons.map((l, i) => {
            const ls = STATUS_STYLES[l.status] ?? STATUS_STYLES.pending;
            return (
              <div
                key={l.lesson_id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '6px 10px',
                  borderRadius: 'var(--radius-sm)',
                  background: ls.bgGradient,
                  border: `1px solid ${ls.border}`,
                  marginBottom: 3,
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  animation: `slide-up ${0.15 + i * 0.04}s ease`,
                }}
              >
                <span style={{ fontWeight: 500 }}>{l.lesson_id}</span>
                <span
                  style={{
                    fontSize: 9,
                    color: ls.text,
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  {ls.icon} {ls.label}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
