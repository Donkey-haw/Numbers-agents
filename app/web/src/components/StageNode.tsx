import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { StageStatus } from '../types/events';
import { STAGE_LABELS } from '../types/events';
import { STATUS_STYLES } from '../utils/statusColors';
import { NODE_WIDTH } from '../utils/graphLayout';
import { useRunStore } from '../stores/useRunStore';

interface StageNodeData {
  stage: string;
  status: StageStatus;
  [key: string]: unknown;
}

function StageNodeInner({ data }: NodeProps) {
  const nodeData = data as unknown as StageNodeData;
  const { stage, status } = nodeData;
  const style = STATUS_STYLES[status] ?? STATUS_STYLES.pending;
  const label = STAGE_LABELS[stage] ?? stage;
  const lessonStates = useRunStore((s) => s.lessonStates[stage]);

  const lessonCount = lessonStates ? Object.keys(lessonStates).length : 0;
  const lessonDone = lessonStates
    ? Object.values(lessonStates).filter(
        (l) => l.status !== 'running' && l.status !== 'pending',
      ).length
    : 0;

  return (
    <div
      style={{
        width: NODE_WIDTH,
        position: 'relative',
        borderRadius: 16,
        overflow: 'hidden',
        cursor: 'default',
      }}
    >
      {/* Glow backdrop for running/active states */}
      <div
        style={{
          position: 'absolute',
          inset: -1,
          borderRadius: 17,
          background: style.pulse
            ? `conic-gradient(from 0deg, ${style.border}, transparent, ${style.border})`
            : 'none',
          animation: style.pulse ? 'orbit-glow 3s linear infinite' : undefined,
          opacity: 0.6,
        }}
      />

      {/* Main card body */}
      <div
        style={{
          position: 'relative',
          background: style.bgGradient,
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: `1px solid ${style.border}`,
          borderRadius: 16,
          padding: '14px 16px',
          boxShadow: `0 0 16px ${style.glow}, 0 4px 20px rgba(0,0,0,0.3)`,
        }}
      >
        <Handle type="target" position={Position.Top} style={{ opacity: 0, top: -2 }} />

        {/* Top row: icon + name */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: style.iconBg,
              border: `1px solid ${style.border}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 13,
              flexShrink: 0,
              color: style.text,
              fontWeight: 600,
            }}
          >
            {style.icon}
          </div>
          <div
            style={{
              fontWeight: 600,
              fontSize: 13,
              color: 'var(--text-primary)',
              fontFamily: 'var(--font-sans)',
              lineHeight: 1.3,
            }}
          >
            {label}
          </div>
        </div>

        {/* Bottom row: status badge + lesson count */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span
            style={{
              fontSize: 10,
              fontWeight: 600,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              color: style.text,
              background: style.iconBg,
              border: `1px solid ${style.border}`,
              borderRadius: 6,
              padding: '2px 8px',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {style.label}
          </span>
          {lessonCount > 0 && (
            <span
              style={{
                fontSize: 11,
                color: 'var(--text-tertiary)',
                fontFamily: 'var(--font-mono)',
                fontWeight: 500,
              }}
            >
              {lessonDone}/{lessonCount}
            </span>
          )}
        </div>

        {/* Lesson progress micro-bar */}
        {lessonCount > 0 && (
          <div
            style={{
              marginTop: 8,
              height: 3,
              borderRadius: 2,
              background: 'rgba(255,255,255,0.06)',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                width: `${(lessonDone / lessonCount) * 100}%`,
                height: '100%',
                borderRadius: 2,
                background: `linear-gradient(90deg, ${style.border}, ${style.text})`,
                transition: 'width 0.5s ease',
              }}
            />
          </div>
        )}

        <Handle type="source" position={Position.Bottom} style={{ opacity: 0, bottom: -2 }} />
      </div>
    </div>
  );
}

export const StageNode = memo(StageNodeInner);
