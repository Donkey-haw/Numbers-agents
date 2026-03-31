import { useMemo } from 'react';
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  type NodeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useRunStore } from '../stores/useRunStore';
import { buildNodes, buildEdges } from '../utils/graphLayout';
import { StageNode } from './StageNode';
import { JobNode } from './JobNode';

const nodeTypes: NodeTypes = {
  stageNode: StageNode as unknown as NodeTypes['stageNode'],
  jobNode: JobNode as unknown as NodeTypes['jobNode'],
};

export function RunGraph() {
  const manifest = useRunStore((s) => s.manifest);
  const nodeStates = useRunStore((s) => s.nodeStates);
  const lessonStates = useRunStore((s) => s.lessonStates);

  const stageOrder = manifest?.stage_order ?? [];

  const nodes = useMemo(
    () => buildNodes(stageOrder, nodeStates, lessonStates),
    [stageOrder, nodeStates, lessonStates],
  );

  const edges = useMemo(
    () => buildEdges(stageOrder, nodeStates, lessonStates),
    [stageOrder, nodeStates, lessonStates],
  );

  if (!manifest) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          color: '#6b7280',
          fontFamily: 'Inter, sans-serif',
        }}
      >
        Run을 선택하면 파이프라인 그래프가 표시됩니다.
      </div>
    );
  }

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      fitView
      fitViewOptions={{ padding: 0.3 }}
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable={false}
      proOptions={{ hideAttribution: true }}
      style={{ background: 'var(--bg-base)' }}
    >
      <Background
        variant={BackgroundVariant.Dots}
        color="rgba(255,255,255,0.04)"
        gap={24}
        size={1}
      />
    </ReactFlow>
  );
}
