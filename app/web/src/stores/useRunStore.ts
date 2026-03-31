import { create } from 'zustand';
import type {
  RunEvent,
  RunManifest,
  StageStatus,
  LessonStatus,
  JobGraph,
} from '../types/events';

export interface RunState {
  /* core data */
  runId: string | null;
  manifest: RunManifest | null;
  events: RunEvent[];
  nodeStates: Record<string, StageStatus>;
  lessonStates: Record<string, Record<string, LessonStatus>>;
  jobGraph: JobGraph | null;

  /* ui state */
  selectedNode: string | null;
  expandedNodes: Set<string>;

  /* actions */
  setRunId: (id: string | null) => void;
  setManifest: (m: RunManifest) => void;
  setJobGraph: (g: JobGraph) => void;
  applyEvent: (evt: RunEvent) => void;
  loadEvents: (evts: RunEvent[]) => void;
  selectNode: (stage: string | null) => void;
  toggleExpand: (stage: string) => void;
  reset: () => void;
}

const initialState = {
  runId: null as string | null,
  manifest: null as RunManifest | null,
  events: [] as RunEvent[],
  nodeStates: {} as Record<string, StageStatus>,
  lessonStates: {} as Record<string, Record<string, LessonStatus>>,
  jobGraph: null as JobGraph | null,
  selectedNode: null as string | null,
  expandedNodes: new Set<string>(),
};

function applyEventToState(
  state: Pick<RunState, 'events' | 'nodeStates' | 'lessonStates'>,
  evt: RunEvent,
) {
  state.events.push(evt);

  if (
    (evt.event_type === 'stage_started' ||
      evt.event_type === 'stage_finished') &&
    evt.stage
  ) {
    state.nodeStates[evt.stage] = (evt.status as StageStatus) ?? 'running';
  }

  if (
    (evt.event_type === 'lesson_started' ||
      evt.event_type === 'lesson_finished' ||
      evt.event_type === 'job_started' ||
      evt.event_type === 'job_finished') &&
    evt.stage &&
    evt.lesson_id
  ) {
    if (!state.lessonStates[evt.stage]) {
      state.lessonStates[evt.stage] = {};
    }
    state.lessonStates[evt.stage][evt.lesson_id] = {
      lesson_id: evt.lesson_id,
      stage: evt.stage,
      status: (evt.status as StageStatus) ?? 'running',
      fallback_used: (evt.payload?.fallback_used as boolean) ?? false,
      warning_used: (evt.payload?.warning_used as boolean) ?? false,
    };
  }
}

export const useRunStore = create<RunState>((set) => ({
  ...initialState,

  setRunId: (id) => set({ runId: id }),

  setManifest: (m) => {
    const nodeStates: Record<string, StageStatus> = {};
    for (const s of m.status_summary) {
      nodeStates[s.stage] = s.status;
    }
    set({ manifest: m, nodeStates });
  },

  setJobGraph: (g) => set((prev) => {
    const nextLessonStates = { ...prev.lessonStates };
    
    // Pre-populate lessonStates so pending jobs show up in the UI
    for (const job of g.jobs) {
      if (!nextLessonStates[job.stage]) {
        nextLessonStates[job.stage] = {};
      }
      if (!nextLessonStates[job.stage][job.section_key]) {
        nextLessonStates[job.stage][job.section_key] = {
          lesson_id: job.section_key,
          stage: job.stage,
          status: (job.status as StageStatus) ?? 'pending',
          fallback_used: false,
          warning_used: false,
        };
      }
    }
    
    return { jobGraph: g, lessonStates: nextLessonStates };
  }),

  applyEvent: (evt) =>
    set((prev) => {
      // Dedup: skip if event already exists
      if (prev.events.some((e) => e.event_id === evt.event_id)) {
        return prev;
      }
      const next = {
        events: [...prev.events],
        nodeStates: { ...prev.nodeStates },
        lessonStates: { ...prev.lessonStates },
      };
      applyEventToState(next, evt);
      return next;
    }),

  loadEvents: (evts) =>
    set(() => {
      const state = {
        events: [] as RunEvent[],
        nodeStates: {} as Record<string, StageStatus>,
        lessonStates: {} as Record<string, Record<string, LessonStatus>>,
      };
      for (const evt of evts) {
        applyEventToState(state, evt);
      }
      return state;
    }),

  selectNode: (stage) => set({ selectedNode: stage }),

  toggleExpand: (stage) =>
    set((prev) => {
      const next = new Set(prev.expandedNodes);
      if (next.has(stage)) {
        next.delete(stage);
      } else {
        next.add(stage);
      }
      return { expandedNodes: next };
    }),

  reset: () =>
    set({
      ...initialState,
      expandedNodes: new Set<string>(),
    }),
}));
