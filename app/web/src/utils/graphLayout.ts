import type { Edge, Node } from '@xyflow/react';
import type { LessonStatus, StageStatus, StageSummary } from '../types/events';

const STAGE_NODE_WIDTH = 220;
const JOB_NODE_WIDTH = 170;
const NODE_GAP_X = 260;
const START_X = 40;
const STAGE_ROW_Y = 70;
const JOB_ROW_START_Y = 230;
const JOB_GAP_Y = 76;

export { JOB_NODE_WIDTH, STAGE_NODE_WIDTH as NODE_WIDTH };

export function buildNodes(
  stageOrder: string[],
  statusMap: Record<string, StageStatus>,
  lessonStates: Record<string, Record<string, LessonStatus>>,
): Node[] {
  const nodes: Node[] = [];

  stageOrder.forEach((stage, index) => {
    const stageX = START_X + index * NODE_GAP_X;
    nodes.push({
      id: stage,
      type: 'stageNode',
      position: { x: stageX, y: STAGE_ROW_Y },
      data: {
        stage,
        status: statusMap[stage] ?? 'pending',
      },
    });

    const jobs = Object.values(lessonStates[stage] ?? {}).sort((a, b) =>
      a.lesson_id.localeCompare(b.lesson_id, 'ko-KR', { numeric: true }),
    );

    jobs.forEach((job, jobIndex) => {
      nodes.push({
        id: jobNodeId(stage, job.lesson_id),
        type: 'jobNode',
        position: {
          x: stageX + (STAGE_NODE_WIDTH - JOB_NODE_WIDTH) / 2,
          y: JOB_ROW_START_Y + jobIndex * JOB_GAP_Y,
        },
        data: {
          stage,
          lesson_id: job.lesson_id,
          status: job.status,
          fallback_used: job.fallback_used,
          warning_used: job.warning_used,
        },
      });
    });
  });

  return nodes;
}

export function buildEdges(
  stageOrder: string[],
  statusMap: Record<string, StageStatus>,
  lessonStates: Record<string, Record<string, LessonStatus>>,
): Edge[] {
  const edges: Edge[] = [];

  stageOrder.slice(0, -1).forEach((stage, index) => {
    const nextStage = stageOrder[index + 1];
    const srcStatus = statusMap[stage] ?? 'pending';
    const tgtStatus = statusMap[nextStage] ?? 'pending';

    let stroke = '#4b5563';
    let dasharray: string | undefined = '5,5';
    let animated = false;

    if (srcStatus === 'running' || tgtStatus === 'running') {
      stroke = '#3b82f6';
      dasharray = undefined;
      animated = true;
    } else if (srcStatus === 'failed' || srcStatus === 'blocked') {
      stroke = '#ef4444';
      dasharray = undefined;
    } else if (
      (srcStatus === 'succeeded' || srcStatus === 'succeeded_with_warning') &&
      tgtStatus !== 'pending'
    ) {
      stroke = '#10b981';
      dasharray = undefined;
    }

    edges.push({
      id: `${stage}->${nextStage}`,
      source: stage,
      target: nextStage,
      animated,
      style: { stroke, strokeWidth: 2, strokeDasharray: dasharray },
    });
  });

  Object.entries(lessonStates).forEach(([stage, jobs]) => {
    Object.values(jobs).forEach((job) => {
      const jobId = jobNodeId(stage, job.lesson_id);
      const style = edgeStyleForStatus(job.status);
      edges.push({
        id: `${stage}->${jobId}`,
        source: stage,
        target: jobId,
        animated: job.status === 'running',
        style,
      });
    });
  });

  return edges;
}

export function statusMapFromSummary(
  summary: StageSummary[],
): Record<string, StageStatus> {
  const map: Record<string, StageStatus> = {};
  for (const stage of summary) {
    map[stage.stage] = stage.status;
  }
  return map;
}

function edgeStyleForStatus(status: StageStatus): { stroke: string; strokeWidth: number; strokeDasharray?: string } {
  if (status === 'running') return { stroke: '#3b82f6', strokeWidth: 2 };
  if (status === 'failed' || status === 'blocked') return { stroke: '#ef4444', strokeWidth: 2 };
  if (status === 'succeeded' || status === 'succeeded_with_warning') return { stroke: '#10b981', strokeWidth: 2 };
  return { stroke: '#4b5563', strokeWidth: 2, strokeDasharray: '5,5' };
}

function jobNodeId(stage: string, lessonId: string): string {
  return `${stage}::${lessonId}`;
}
