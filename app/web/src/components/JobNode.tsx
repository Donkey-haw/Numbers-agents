import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { StageStatus } from '../types/events';
import { STATUS_STYLES } from '../utils/statusColors';
import { JOB_NODE_WIDTH } from '../utils/graphLayout';

interface JobNodeData {
  lesson_id: string;
  status: StageStatus;
  fallback_used?: boolean;
  warning_used?: boolean;
  [key: string]: unknown;
}

function JobNodeInner({ data }: NodeProps) {
  const nodeData = data as unknown as JobNodeData;
  const style = STATUS_STYLES[nodeData.status] ?? STATUS_STYLES.pending;

  return (
    <div
      style={{
        width: JOB_NODE_WIDTH,
        borderRadius: 12,
        overflow: 'hidden',
        background: style.bgGradient,
        border: `1px solid ${style.border}`,
        boxShadow: `0 0 10px ${style.glow}, 0 4px 14px rgba(0,0,0,0.2)`,
      }}
    >
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
      <div style={{ padding: '10px 12px' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 8,
            marginBottom: 6,
          }}
        >
          <div
            style={{
              fontSize: 12,
              fontWeight: 700,
              color: 'var(--text-primary)',
              minWidth: 0,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {nodeData.lesson_id}
          </div>
          <div
            style={{
              fontSize: 9,
              color: style.text,
              fontFamily: 'var(--font-mono)',
              fontWeight: 700,
              flexShrink: 0,
            }}
          >
            {style.icon} {style.label}
          </div>
        </div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {nodeData.fallback_used ? 'fallback' : 'direct'}
          {nodeData.warning_used ? ' · warning' : ''}
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
    </div>
  );
}

export const JobNode = memo(JobNodeInner);
