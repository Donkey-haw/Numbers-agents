/* ------------------------------------------------------------------ */
/*  Event & state type definitions (matches orchestrator_events.py)   */
/* ------------------------------------------------------------------ */

export type StageStatus =
  | 'pending'
  | 'running'
  | 'succeeded'
  | 'succeeded_with_warning'
  | 'failed'
  | 'blocked';

export type EventType =
  | 'run_created'
  | 'run_started'
  | 'stage_started'
  | 'stage_finished'
  | 'lesson_started'
  | 'lesson_finished'
  | 'job_started'
  | 'job_finished'
  | 'lesson_pipeline_completed'
  | 'run_finished';

export interface RunEvent {
  event_id: string;
  run_id: string;
  timestamp: string;
  event_type: EventType;
  stage: string | null;
  lesson_id: string | null;
  status: StageStatus | string | null;
  payload: Record<string, unknown>;
}

export interface StageSummary {
  stage: string;
  status: StageStatus;
  fallback_used: boolean;
  warning_count: number;
  error_count: number;
}

export interface RunManifest {
  schema_version: string;
  run_id: string;
  workflow_mode: string;
  config_path: string;
  selected_unit: string | null;
  selected_lessons: string[];
  stage_order: string[];
  started_at: string;
  finished_at: string | null;
  final_status: string;
  final_output_file: string | null;
  curriculum_pdf: string | null;
  status_summary: StageSummary[];
}

export interface RunSummary {
  run_id: string;
  started_at: string | null;
  finished_at: string | null;
  final_status: string;
  workflow_mode: string | null;
  selected_unit: string | null;
}

export interface LessonStatus {
  lesson_id: string;
  stage: string;
  status: StageStatus;
  fallback_used: boolean;
  warning_used: boolean;
}

export interface JobGraphEntry {
  job_id: string;
  section_key: string;
  stage: string;
  status: string;
  depends_on: string[];
}

export interface JobGraph {
  schema_version: string;
  run_id: string;
  generated_at?: string;
  jobs: JobGraphEntry[];
}

export const LESSON_LEVEL_STAGES = [
  'lesson_analysis_agent',
  'lesson_review_agent',
  'activity_plan_agent',
  'activity_review_agent',
  'html_card_agent',
] as const;

export const GRAPH_STAGE_FOLDS: Record<string, string> = {
  lesson_review_agent: 'lesson_analysis_agent',
  activity_review_agent: 'activity_plan_agent',
};

export const STAGE_LABELS: Record<string, string> = {
  document_inventory_agent: '입력 문서 확인',
  pdf_extract_agent: 'PDF 텍스트 추출',
  page_index_agent: '페이지 인덱싱',
  schedule_parse_agent: '진도 구조 파싱',
  lesson_query_agent: '차시 쿼리 생성',
  page_candidate_agent: '후보 페이지 선정',
  boundary_decision_agent: '경계 결정',
  boundary_validation_agent: '경계 검증',
  source_boundary_agent: '교과서 경계 추론',
  source_validation_agent: '교과서 경계 검토',
  curriculum_analysis_agent: '국가수준 교육과정 분석',
  lesson_analysis_agent: '차시 분석',
  lesson_review_agent: '차시 검토',
  activity_plan_agent: '활동 계획',
  activity_review_agent: '활동 검토',
  html_card_agent: 'HTML 렌더링',
  capture_agent: '이미지 캡처',
  numbers_compose_agent: 'Numbers 조합',
  review_manifest_agent: '결과 검토',
  verify_agent: '최종 검증',
};

export const DISPLAY_STAGE_LABELS: Record<string, string> = {
  lesson_analysis_agent: '차시 분석 + 검토',
  activity_plan_agent: '활동 계획 + 검토',
};
