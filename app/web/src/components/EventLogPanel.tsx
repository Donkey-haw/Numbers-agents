import { useRunStore } from '../stores/useRunStore';
import { STAGE_LABELS } from '../types/events';
import { STATUS_STYLES } from '../utils/statusColors';
import type { StageStatus, EventType } from '../types/events';

const EVENT_ICONS: Record<EventType, string> = {
  run_created: '◆',
  run_started: '▶',
  stage_started: '●',
  stage_finished: '✓',
  lesson_started: '▸',
  lesson_finished: '◂',
  job_started: '◷',
  job_finished: '☑',
  lesson_pipeline_completed: '✦',
  run_finished: '■',
};

const EVENT_LABELS: Record<EventType, string> = {
  run_created: 'Run 생성',
  run_started: 'Run 시작',
  stage_started: 'Stage 시작',
  stage_finished: 'Stage 종료',
  lesson_started: '차시 시작',
  lesson_finished: '차시 종료',
  job_started: 'Job 시작',
  job_finished: 'Job 종료',
  lesson_pipeline_completed: '차시 파이프라인 완료',
  run_finished: 'Run 완료',
};

export function EventLogPanel() {
  const events = useRunStore((s) => s.events);

  return (
    <div
      id="event-log-panel"
      style={{
        padding: '12px 20px',
        fontFamily: 'var(--font-sans)',
        fontSize: 12,
        color: 'var(--text-secondary)',
        overflowY: 'auto',
        height: '100%',
      }}
    >
      <div
        style={{
          fontSize: 10,
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          color: 'var(--text-muted)',
          marginBottom: 10,
          padding: '0 4px',
          fontFamily: 'var(--font-mono)',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}
      >
        <span>Event Log</span>
        <span
          style={{
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            borderRadius: 4,
            padding: '1px 6px',
            color: '#93c5fd',
            fontSize: 10,
            fontWeight: 600,
          }}
        >
          {events.length}
        </span>
      </div>
      {events.length === 0 ? (
        <div style={{ color: 'var(--text-muted)', padding: 12 }}>이벤트 없음</div>
      ) : (
        [...events].reverse().map((evt, i) => {
          const icon = EVENT_ICONS[evt.event_type] ?? '•';
          const label = EVENT_LABELS[evt.event_type] ?? evt.event_type;
          const stageName = evt.stage
            ? STAGE_LABELS[evt.stage] ?? evt.stage
            : '';
          const status = evt.status as StageStatus | null;
          const statusStyle = status ? STATUS_STYLES[status] : null;

          return (
            <div
              key={evt.event_id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '5px 6px',
                borderBottom: '1px solid var(--border-subtle)',
                animation: i < 3 ? `fade-in 0.3s ease ${i * 0.1}s` : undefined,
              }}
            >
              <span
                style={{
                  fontSize: 10,
                  width: 16,
                  textAlign: 'center',
                  color: statusStyle?.text ?? 'var(--text-muted)',
                  flexShrink: 0,
                }}
              >
                {icon}
              </span>
              <span
                style={{
                  color: 'var(--text-muted)',
                  width: 56,
                  flexShrink: 0,
                  fontFamily: 'var(--font-mono)',
                  fontSize: 10,
                }}
              >
                {new Date(evt.timestamp).toLocaleTimeString('ko-KR', {
                  hour12: false,
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                })}
              </span>
              <span
                style={{
                  fontWeight: 500,
                  color: 'var(--text-secondary)',
                  fontSize: 12,
                }}
              >
                {label}
              </span>
              {stageName && (
                <span style={{ color: 'var(--text-tertiary)', fontSize: 12 }}>
                  {stageName}
                </span>
              )}
              {evt.lesson_id && (
                <span
                  style={{
                    background: 'var(--bg-overlay)',
                    borderRadius: 4,
                    padding: '1px 6px',
                    color: 'var(--text-secondary)',
                    fontSize: 10,
                    fontFamily: 'var(--font-mono)',
                  }}
                >
                  {evt.lesson_id}
                </span>
              )}
              {statusStyle && (
                <span
                  style={{
                    marginLeft: 'auto',
                    fontSize: 10,
                    color: statusStyle.text,
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 600,
                  }}
                >
                  {statusStyle.label}
                </span>
              )}
            </div>
          );
        })
      )}
    </div>
  );
}
