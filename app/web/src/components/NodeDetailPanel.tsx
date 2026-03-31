import { useRunStore } from '../stores/useRunStore';
import { STAGE_LABELS } from '../types/events';
import { STATUS_STYLES } from '../utils/statusColors';
import type { StageStatus } from '../types/events';
import { LessonSubnodeGroup } from './LessonSubnodeGroup';

export function NodeDetailPanel() {
  const selectedNode = useRunStore((s) => s.selectedNode);
  const manifest = useRunStore((s) => s.manifest);
  const nodeStates = useRunStore((s) => s.nodeStates);
  const events = useRunStore((s) => s.events);

  if (!selectedNode || !manifest) {
    return (
      <div
        id="node-detail-panel"
        style={{
          padding: 24,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          color: 'var(--text-muted)',
          fontFamily: 'var(--font-sans)',
          fontSize: 13,
          textAlign: 'center',
          gap: 12,
        }}
      >
        <div style={{ fontSize: 32, opacity: 0.3 }}>⬡</div>
        <div>노드를 클릭하면<br/>상세 정보가 표시됩니다</div>
      </div>
    );
  }

  const status: StageStatus = nodeStates[selectedNode] ?? 'pending';
  const style = STATUS_STYLES[status];
  const summary = manifest.status_summary.find(
    (s) => s.stage === selectedNode,
  );
  const stageEvents = events.filter((e) => e.stage === selectedNode);

  const startEvent = stageEvents.find((e) => e.event_type === 'stage_started');
  const endEvent = stageEvents.find((e) => e.event_type === 'stage_finished');

  // Duration calculation
  let duration = '';
  if (startEvent && endEvent) {
    const ms = new Date(endEvent.timestamp).getTime() - new Date(startEvent.timestamp).getTime();
    const secs = Math.round(ms / 1000);
    if (secs < 60) duration = `${secs}s`;
    else duration = `${Math.floor(secs / 60)}m ${secs % 60}s`;
  }

  return (
    <div
      id="node-detail-panel"
      style={{
        padding: 20,
        fontFamily: 'var(--font-sans)',
        fontSize: 13,
        color: 'var(--text-secondary)',
        overflowY: 'auto',
        height: '100%',
        animation: 'slide-up 0.3s ease',
      }}
    >
      {/* Header with icon */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: 10,
            background: style.bgGradient,
            border: `1px solid ${style.border}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 16,
            color: style.text,
            flexShrink: 0,
          }}
        >
          {style.icon}
        </div>
        <div>
          <h3
            style={{
              fontSize: 15,
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: 2,
              letterSpacing: '-0.01em',
            }}
          >
            {STAGE_LABELS[selectedNode] ?? selectedNode}
          </h3>
          <div
            style={{
              fontSize: 10,
              fontWeight: 600,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              color: style.text,
              fontFamily: 'var(--font-mono)',
            }}
          >
            {style.label}
          </div>
        </div>
      </div>

      {/* Details grid */}
      <div
        style={{
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          marginBottom: 16,
        }}
      >
        <DetailRow label="Stage" value={selectedNode} mono />
        {startEvent && (
          <DetailRow
            label="시작"
            value={new Date(startEvent.timestamp).toLocaleTimeString('ko-KR', { hour12: false })}
            mono
          />
        )}
        {endEvent && (
          <DetailRow
            label="종료"
            value={new Date(endEvent.timestamp).toLocaleTimeString('ko-KR', { hour12: false })}
            mono
          />
        )}
        {duration && <DetailRow label="소요" value={duration} mono highlight />}
        {summary && (
          <>
            <DetailRow
              label="Fallback"
              value={summary.fallback_used ? '사용됨' : '—'}
              valueColor={summary.fallback_used ? '#fdba74' : undefined}
            />
            <DetailRow
              label="경고"
              value={`${summary.warning_count}`}
              valueColor={summary.warning_count > 0 ? '#fcd34d' : undefined}
              mono
            />
            <DetailRow
              label="오류"
              value={`${summary.error_count}`}
              valueColor={summary.error_count > 0 ? '#fca5a5' : undefined}
              mono
            />
          </>
        )}
      </div>

      {/* Lesson subnodes (Phase 4) */}
      <LessonSubnodeGroup stage={selectedNode} />
    </div>
  );
}

function DetailRow({
  label,
  value,
  mono,
  highlight,
  valueColor,
}: {
  label: string;
  value: string;
  mono?: boolean;
  highlight?: boolean;
  valueColor?: string;
}) {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 14px',
        borderBottom: '1px solid var(--border-subtle)',
        background: highlight ? 'rgba(59, 130, 246, 0.05)' : undefined,
      }}
    >
      <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>{label}</span>
      <span
        style={{
          fontSize: 12,
          fontFamily: mono ? 'var(--font-mono)' : 'var(--font-sans)',
          fontWeight: 500,
          color: valueColor ?? 'var(--text-secondary)',
        }}
      >
        {value}
      </span>
    </div>
  );
}
