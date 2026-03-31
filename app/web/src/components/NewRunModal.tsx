import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface PDF {
  filename: string;
  path: string;
  relative_path: string;
}

interface Subject {
  subject: string;
  pdfs: PDF[];
}

interface ManualLessonDraft {
  id: string;
  sheet_name: string;
  title: string;
  selected_pages: number[];
}

interface ManualValidationResult {
  blockingIssues: string[];
  warnings: string[];
}

interface PdfMetadata {
  page_count: number;
  filename: string;
  pdf_path: string;
}

interface DragSelectionState {
  active: boolean;
  mode: 'add' | 'remove';
}

const SUBJECT_COLORS: Record<string, string> = {
  국어: '#3b82f6',
  사회: '#10b981',
  수학: '#f59e0b',
  도덕: '#8b5cf6',
  미술: '#ec4899',
  실과: '#06b6d4',
};

export function NewRunModal({
  onClose,
  pageMode = false,
}: {
  onClose: () => void;
  pageMode?: boolean;
}) {
  const navigate = useNavigate();

  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
  const [selectedTextbook, setSelectedTextbook] = useState<PDF | null>(null);

  const [manualLessons, setManualLessons] = useState<ManualLessonDraft[]>([
    { id: crypto.randomUUID(), sheet_name: '1차시', title: '', selected_pages: [] },
  ]);
  const [selectedManualLessonId, setSelectedManualLessonId] = useState<string | null>(null);
  const [dragSelection, setDragSelection] = useState<DragSelectionState | null>(null);

  const [manualPdfMetadata, setManualPdfMetadata] = useState<PdfMetadata | null>(null);
  const [loadingPdfMetadata, setLoadingPdfMetadata] = useState(false);
  const [serverManualValidation, setServerManualValidation] = useState<ManualValidationResult>({
    blockingIssues: [],
    warnings: [],
  });
  const [validatingPageMap, setValidatingPageMap] = useState(false);

  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/textbooks')
      .then((r) => r.json())
      .then((data) => {
        setSubjects(data);
        if (data.length > 0) {
          setSelectedSubject(data[0]);
        }
      })
      .finally(() => setLoadingSubjects(false));
  }, []);

  useEffect(() => {
    if (!selectedSubject) {
      setSelectedTextbook(null);
      return;
    }
    setSelectedTextbook(selectedSubject.pdfs[0] ?? null);
  }, [selectedSubject]);

  useEffect(() => {
    if (!selectedManualLessonId && manualLessons.length > 0) {
      setSelectedManualLessonId(manualLessons[0].id);
      return;
    }
    if (selectedManualLessonId && !manualLessons.some((lesson) => lesson.id === selectedManualLessonId)) {
      setSelectedManualLessonId(manualLessons[0]?.id ?? null);
    }
  }, [manualLessons, selectedManualLessonId]);

  useEffect(() => {
    const handleMouseUp = () => setDragSelection(null);
    window.addEventListener('mouseup', handleMouseUp);
    return () => window.removeEventListener('mouseup', handleMouseUp);
  }, []);

  useEffect(() => {
    if (!selectedTextbook) {
      setManualPdfMetadata(null);
      setLoadingPdfMetadata(false);
      return;
    }

    let cancelled = false;
    setLoadingPdfMetadata(true);

    fetch('/api/pdf-metadata', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pdf_path: selectedTextbook.relative_path }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Metadata fetch failed' }));
          throw new Error(err.detail);
        }
        return res.json();
      })
      .then((data) => {
        if (!cancelled) {
          setManualPdfMetadata(data);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setManualPdfMetadata(null);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoadingPdfMetadata(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedTextbook]);

  useEffect(() => {
    const lessonsReadyForValidation = manualLessons.filter(
      (lesson) => lesson.sheet_name.trim() && lesson.selected_pages.length > 0,
    );

    if (lessonsReadyForValidation.length === 0) {
      setServerManualValidation({ blockingIssues: [], warnings: [] });
      setValidatingPageMap(false);
      return;
    }

    const timeoutId = window.setTimeout(async () => {
      setValidatingPageMap(true);
      try {
        const res = await fetch('/api/validate-page-map', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            lessons: lessonsReadyForValidation.map((lesson) => ({
              sheet_name: lesson.sheet_name.trim(),
              title: lesson.title.trim() || lesson.sheet_name.trim(),
              pdf_pages: lesson.selected_pages,
            })),
          }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Validation failed' }));
          throw new Error(err.detail);
        }
        const data = await res.json();
        setServerManualValidation({
          blockingIssues: data.blocking_issues ?? [],
          warnings: data.warnings ?? [],
        });
      } catch (e) {
        setServerManualValidation({
          blockingIssues: [(e as Error).message],
          warnings: [],
        });
      } finally {
        setValidatingPageMap(false);
      }
    }, 250);

    return () => window.clearTimeout(timeoutId);
  }, [manualLessons]);

  const localManualValidation = validateManualLessons(manualLessons, manualPdfMetadata?.page_count ?? null);
  const manualValidation = mergeManualValidation(localManualValidation, serverManualValidation);
  const selectedManualLesson = manualLessons.find((lesson) => lesson.id === selectedManualLessonId) ?? null;
  const manualModeReady =
    !!selectedSubject &&
    !!selectedTextbook &&
    manualLessons.length > 0 &&
    manualLessons.every((lesson) => lesson.sheet_name.trim() && lesson.selected_pages.length > 0) &&
    !validatingPageMap &&
    manualValidation.blockingIssues.length === 0;

  const updateManualLesson = (id: string, key: keyof Pick<ManualLessonDraft, 'sheet_name' | 'title'>, value: string) => {
    setManualLessons((prev) => prev.map((lesson) => (lesson.id === id ? { ...lesson, [key]: value } : lesson)));
  };

  const applyManualLessonPageToggle = (id: string, page: number, mode: 'add' | 'remove') => {
    setManualLessons((prev) =>
      prev.map((lesson) => {
        if (lesson.id !== id) return lesson;
        const pageSet = new Set(lesson.selected_pages);
        if (mode === 'add') {
          pageSet.add(page);
        } else {
          pageSet.delete(page);
        }
        return {
          ...lesson,
          selected_pages: Array.from(pageSet).sort((a, b) => a - b),
        };
      }),
    );
  };

  const addManualLesson = () => {
    const newId = crypto.randomUUID();
    setManualLessons((prev) => [
      ...prev,
      {
        id: newId,
        sheet_name: `${prev.length + 1}차시`,
        title: '',
        selected_pages: [],
      },
    ]);
    setSelectedManualLessonId(newId);
  };

  const rebuildLessonNames = (lessons: ManualLessonDraft[]) =>
    lessons.map((lesson, index) => ({
      ...lesson,
      sheet_name: `${index + 1}차시`,
    }));

  const removeManualLessonAndRenumber = (id: string) => {
    setManualLessons((prev) => {
      if (prev.length === 1) return prev;
      return rebuildLessonNames(prev.filter((lesson) => lesson.id !== id));
    });
  };

  const startPipeline = async (configPath: string) => {
    const res = await fetch('/api/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        config_path: configPath,
        workflow_mode: 'stable',
        keep_run_artifacts: true,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Start failed' }));
      throw new Error(err.detail);
    }
    const data = await res.json();
    onClose();
    navigate(`/runs/${data.run_id}`);
  };

  const handleStartManual = async () => {
    if (!selectedSubject || !selectedTextbook || !manualModeReady) return;
    setStarting(true);
    setError(null);
    try {
      const generatedUnitTitle = selectedTextbook.filename.replace(/\.pdf$/i, '').trim() || `${selectedSubject.subject}_manual`;
      const lessons = manualLessons.map((lesson) => ({
        sheet_name: lesson.sheet_name.trim(),
        title: lesson.title.trim() || lesson.sheet_name.trim(),
        pdf_pages: lesson.selected_pages,
      }));
      const res = await fetch('/api/create-config-from-page-map', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: selectedSubject.subject,
          pdf_path: selectedTextbook.relative_path,
          unit_title: generatedUnitTitle,
          output_filename: `output/${selectedSubject.subject}_${generatedUnitTitle}.numbers`,
          footer: `${selectedSubject.subject} · ${generatedUnitTitle}`,
          lessons,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Manual config creation failed' }));
        throw new Error(err.detail);
      }
      const data = await res.json();
      await startPipeline(data.config_path);
    } catch (e) {
      setError((e as Error).message);
      setStarting(false);
    }
  };

  return (
    <div
      style={{
        position: pageMode ? 'relative' : 'fixed',
        inset: pageMode ? 'auto' : 0,
        zIndex: pageMode ? 'auto' : 1000,
        display: pageMode ? 'block' : 'flex',
        alignItems: pageMode ? 'initial' : 'center',
        justifyContent: 'center',
        minHeight: pageMode ? '100vh' : 'auto',
        background: pageMode ? 'var(--bg-base)' : 'rgba(0, 0, 0, 0.6)',
        backdropFilter: pageMode ? 'none' : 'blur(8px)',
        animation: pageMode ? 'none' : 'fade-in 0.2s ease',
        padding: pageMode ? 0 : 0,
      }}
      onClick={pageMode ? undefined : onClose}
    >
      <div
        onClick={pageMode ? undefined : (e) => e.stopPropagation()}
        style={{
          width: pageMode ? '100%' : 760,
          maxHeight: pageMode ? 'none' : '88vh',
          minHeight: pageMode ? '100vh' : 'auto',
          overflowY: pageMode ? 'visible' : 'auto',
          background: 'var(--bg-surface)',
          border: pageMode ? 'none' : '1px solid var(--border-default)',
          borderRadius: pageMode ? 0 : 'var(--radius-xl)',
          boxShadow: pageMode ? 'none' : '0 24px 80px rgba(0, 0, 0, 0.5)',
          animation: pageMode ? 'none' : 'slide-up 0.3s ease',
        }}
      >
        <div
          style={{
            padding: '24px 28px 16px',
            borderBottom: '1px solid var(--border-subtle)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-sans)' }}>
                수동 페이지 선택
              </h2>
              <p style={{ marginTop: 6, color: 'var(--text-muted)', fontSize: 12, lineHeight: 1.6 }}>
                교사가 차시별 교과서 페이지를 직접 선택하고, 그 결과로 final config를 생성합니다.
              </p>
            </div>
            <button
              onClick={onClose}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: 18, cursor: 'pointer' }}
            >
              {pageMode ? '목록으로' : '✕'}
            </button>
          </div>
        </div>

        <div style={{ padding: pageMode ? '28px 40px 40px' : '20px 28px 24px', display: 'grid', gap: 20 }}>
          <div>
            <SectionLabel>교과 선택</SectionLabel>
            {loadingSubjects ? (
              <div style={{ color: 'var(--text-muted)', padding: 20, fontSize: 13 }}>로딩 중...</div>
            ) : (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {subjects.map((subject) => {
                  const selected = selectedSubject?.subject === subject.subject;
                  const accent = SUBJECT_COLORS[subject.subject] ?? '#8b5cf6';
                  return (
                    <button
                      key={subject.subject}
                      onClick={() => setSelectedSubject(subject)}
                      style={{
                        padding: '10px 14px',
                        borderRadius: 999,
                        background: selected ? `linear-gradient(135deg, ${accent}20, ${accent}08)` : 'var(--bg-elevated)',
                        border: `1px solid ${selected ? `${accent}60` : 'var(--border-subtle)'}`,
                        color: selected ? 'var(--text-primary)' : 'var(--text-secondary)',
                        fontSize: 13,
                        fontWeight: 600,
                        cursor: 'pointer',
                        fontFamily: 'var(--font-sans)',
                        textAlign: 'center',
                      }}
                    >
                      {subject.subject}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {selectedSubject && (
            <div>
              <SectionLabel>교과서 선택</SectionLabel>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {selectedSubject.pdfs.map((pdf) => {
                  const selected = selectedTextbook?.path === pdf.path;
                  return (
                    <button
                      key={pdf.path}
                      onClick={() => setSelectedTextbook(pdf)}
                      style={{
                        padding: '10px 14px',
                        borderRadius: 999,
                        background: selected ? 'rgba(59, 130, 246, 0.08)' : 'var(--bg-elevated)',
                        border: `1px solid ${selected ? 'rgba(59, 130, 246, 0.3)' : 'var(--border-subtle)'}`,
                        color: selected ? 'var(--text-primary)' : 'var(--text-secondary)',
                        fontSize: 12,
                        textAlign: 'center',
                        cursor: 'pointer',
                      }}
                    >
                      {pdf.filename}
                    </button>
                  );
                })}
              </div>
              <div
                style={{
                  marginTop: 10,
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-muted)',
                  fontSize: 12,
                }}
              >
                {loadingPdfMetadata && 'PDF 메타데이터 확인 중...'}
                {!loadingPdfMetadata && manualPdfMetadata && `전체 ${manualPdfMetadata.page_count}페이지`}
                {!loadingPdfMetadata && !manualPdfMetadata && '페이지 수를 아직 불러오지 못했습니다.'}
              </div>
            </div>
          )}

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: pageMode ? 'minmax(0, 1fr) 360px' : 'minmax(0, 1fr)',
              gap: 24,
              alignItems: 'start',
            }}
          >
            <div style={{ minWidth: 0 }}>
              {manualPdfMetadata && selectedTextbook && selectedManualLesson ? (
                <>
                  <SectionLabel>교과서 페이지</SectionLabel>
                  <div style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: 8 }}>
                    현재 선택 차시: {selectedManualLesson.sheet_name}
                    {selectedManualLesson.title ? ` / ${selectedManualLesson.title}` : ''}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: 12 }}>
                    페이지를 클릭하면 선택 또는 해제됩니다. 드래그하면 여러 페이지를 한 번에 선택하거나 해제할 수 있습니다.
                  </div>
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: pageMode ? 'repeat(5, minmax(0, 1fr))' : 'repeat(4, minmax(0, 1fr))',
                      gap: 12,
                    }}
                  >
                    {Array.from({ length: manualPdfMetadata.page_count }, (_, index) => {
                      const pageNum = index + 1;
                      const isSelected = selectedManualLesson.selected_pages.includes(pageNum);
                      return (
                        <button
                          key={pageNum}
                          onMouseDown={() => {
                            const nextMode: 'add' | 'remove' = isSelected ? 'remove' : 'add';
                            setDragSelection({ active: true, mode: nextMode });
                            applyManualLessonPageToggle(selectedManualLesson.id, pageNum, nextMode);
                          }}
                          onMouseEnter={() => {
                            if (!dragSelection?.active) return;
                            applyManualLessonPageToggle(selectedManualLesson.id, pageNum, dragSelection.mode);
                          }}
                          onDragStart={(e) => e.preventDefault()}
                          style={{
                            padding: 0,
                            borderRadius: 'var(--radius-sm)',
                            overflow: 'hidden',
                            border: isSelected ? '2px solid #3b82f6' : '1px solid var(--border-subtle)',
                            background: isSelected ? 'rgba(59, 130, 246, 0.08)' : 'var(--bg-elevated)',
                            cursor: 'pointer',
                          }}
                          title={`${pageNum}페이지`}
                        >
                          <img
                            src={`/api/pdf-page-image?pdf_path=${encodeURIComponent(selectedTextbook.relative_path)}&page=${pageNum}&width=220`}
                            alt={`${pageNum}페이지`}
                            style={{ display: 'block', width: '100%', aspectRatio: '0.72', objectFit: 'cover', background: '#fff' }}
                          />
                          <div
                            style={{
                              padding: '7px 8px',
                              fontSize: 11,
                              fontFamily: 'var(--font-mono)',
                              color: isSelected ? '#93c5fd' : 'var(--text-muted)',
                              background: 'rgba(15, 23, 42, 0.92)',
                            }}
                          >
                            {pageNum}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </>
              ) : (
                <div
                  style={{
                    padding: '24px',
                    borderRadius: 'var(--radius-lg)',
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-muted)',
                    fontSize: 13,
                    lineHeight: 1.7,
                  }}
                >
                  교과와 교과서를 고르면 여기에서 교과서 페이지를 여러 장씩 보면서 차시별로 선택할 수 있습니다.
                </div>
              )}
            </div>

            <div
              style={{
                position: pageMode ? 'sticky' : 'static',
                top: pageMode ? 24 : 'auto',
                display: 'grid',
                gap: 14,
              }}
            >
              <div
                style={{
                  padding: '14px',
                  borderRadius: 'var(--radius-lg)',
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <SectionLabel>차시 구성</SectionLabel>
                <div
                  style={{
                    marginBottom: 12,
                    color: 'var(--text-muted)',
                    fontSize: 12,
                    lineHeight: 1.6,
                  }}
                >
                  차시는 자동으로 번호가 붙습니다. 우측에서 차시를 고르고 중앙에서 페이지를 배정하세요.
                </div>
                <div style={{ display: 'grid', gap: 10 }}>
                  {manualLessons.map((lesson) => {
                    const selected = selectedManualLessonId === lesson.id;
                    return (
                      <div
                        key={lesson.id}
                        style={{
                          padding: '12px',
                          borderRadius: 'var(--radius-md)',
                          background: selected ? 'rgba(59, 130, 246, 0.08)' : 'rgba(8, 12, 20, 0.35)',
                          border: selected ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid var(--border-subtle)',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                          <button
                            onClick={() => setSelectedManualLessonId(lesson.id)}
                            style={{
                              background: 'transparent',
                              border: 'none',
                              color: selected ? 'var(--text-primary)' : 'var(--text-secondary)',
                              fontSize: 12,
                              fontWeight: 700,
                              cursor: 'pointer',
                              padding: 0,
                            }}
                          >
                            {lesson.sheet_name}
                          </button>
                          <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                            {lesson.selected_pages.length > 0 ? formatPageSelection(lesson.selected_pages) : '미선택'}
                          </span>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 8, alignItems: 'center' }}>
                          <input
                            value={lesson.title}
                            onChange={(e) => updateManualLesson(lesson.id, 'title', e.target.value)}
                            placeholder="차시 메모 (선택)"
                            style={inputStyle}
                          />
                          <button onClick={() => removeManualLessonAndRenumber(lesson.id)} style={secondaryBtnStyle}>
                            삭제
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div style={{ marginTop: 10 }}>
                  <button onClick={addManualLesson} style={{ ...secondaryBtnStyle, width: '100%' }}>
                    + 차시 추가
                  </button>
                </div>
              </div>

              <div
                style={{
                  padding: '14px',
                  borderRadius: 'var(--radius-lg)',
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  display: 'grid',
                  gap: 10,
                }}
              >
                <SectionLabel>검증</SectionLabel>
                {validatingPageMap && (
                  <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>페이지 매핑 검증 중...</div>
                )}
                {manualPdfMetadata && (
                  <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                    입력 가능한 페이지 범위: 1 ~ {manualPdfMetadata.page_count}
                  </div>
                )}
                {manualValidation.blockingIssues.length > 0 && (
                  <div
                    style={{
                      padding: '12px 14px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.2)',
                      color: '#fca5a5',
                      fontSize: 12,
                      lineHeight: 1.6,
                    }}
                  >
                    {manualValidation.blockingIssues.map((issue) => (
                      <div key={issue}>{issue}</div>
                    ))}
                  </div>
                )}
                {manualValidation.warnings.length > 0 && (
                  <div
                    style={{
                      padding: '12px 14px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(245, 158, 11, 0.1)',
                      border: '1px solid rgba(245, 158, 11, 0.2)',
                      color: '#fcd34d',
                      fontSize: 12,
                      lineHeight: 1.6,
                    }}
                  >
                    {manualValidation.warnings.map((warning) => (
                      <div key={warning}>{warning}</div>
                    ))}
                  </div>
                )}
              </div>

              <div
                style={{
                  padding: '14px',
                  borderRadius: 'var(--radius-lg)',
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  display: 'grid',
                  gap: 10,
                }}
              >
                <SectionLabel>실행</SectionLabel>
                <div style={{ color: 'var(--text-muted)', fontSize: 12, lineHeight: 1.6 }}>
                  현재 선택된 차시와 페이지 매핑으로 final config를 만든 뒤 바로 run을 시작합니다.
                </div>
                {error && (
                  <div
                    style={{
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.2)',
                      color: '#fca5a5',
                      fontSize: 12,
                      lineHeight: 1.6,
                    }}
                  >
                    {error}
                  </div>
                )}
                <button
                  onClick={handleStartManual}
                  disabled={starting || !manualModeReady}
                  style={{
                    ...primaryBtnStyle,
                    width: '100%',
                    opacity: starting || !manualModeReady ? 0.5 : 1,
                    cursor: starting || !manualModeReady ? 'not-allowed' : 'pointer',
                  }}
                >
                  {starting ? '시작 중...' : '▶ 실행'}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div
          style={{
            padding: '16px 28px',
            borderTop: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'flex-start',
            alignItems: 'center',
          }}
        >
          <button onClick={onClose} style={secondaryBtnStyle}>
            취소
          </button>
        </div>
      </div>
    </div>
  );
}

function validateManualLessons(lessons: ManualLessonDraft[], pageCount: number | null): ManualValidationResult {
  const blockingIssues: string[] = [];
  const warnings: string[] = [];
  const pageOwners = new Map<number, string>();

  for (const lesson of lessons) {
    if (!lesson.sheet_name.trim() || lesson.selected_pages.length === 0) {
      continue;
    }
    const normalizedPages = Array.from(new Set(lesson.selected_pages)).sort((a, b) => a - b);
    if (normalizedPages.length !== lesson.selected_pages.length) {
      warnings.push(`${lesson.sheet_name}: 중복 페이지 선택이 정리됩니다.`);
    }
    for (const pageNum of normalizedPages) {
      if (pageNum < 1) {
        blockingIssues.push(`${lesson.sheet_name}: 페이지 번호는 1 이상이어야 합니다.`);
        continue;
      }
      if (pageCount && pageNum > pageCount) {
        blockingIssues.push(`${lesson.sheet_name}: ${pageNum}페이지는 전체 페이지 수를 초과합니다.`);
        continue;
      }
      const previousOwner = pageOwners.get(pageNum);
      if (previousOwner && previousOwner !== lesson.sheet_name) {
        blockingIssues.push(`${lesson.sheet_name}: ${previousOwner}와 ${pageNum}페이지가 겹칩니다.`);
      }
      pageOwners.set(pageNum, lesson.sheet_name);
    }
  }

  return { blockingIssues, warnings };
}

function mergeManualValidation(local: ManualValidationResult, remote: ManualValidationResult): ManualValidationResult {
  return {
    blockingIssues: Array.from(new Set([...local.blockingIssues, ...remote.blockingIssues])),
    warnings: Array.from(new Set([...local.warnings, ...remote.warnings])),
  };
}

function formatPageSelection(pages: number[]): string {
  if (pages.length === 0) return '';
  const sorted = Array.from(new Set(pages)).sort((a, b) => a - b);
  const ranges: string[] = [];
  let start = sorted[0];
  let previous = sorted[0];

  for (let i = 1; i < sorted.length; i += 1) {
    const current = sorted[i];
    if (current === previous + 1) {
      previous = current;
      continue;
    }
    ranges.push(start === previous ? `${start}` : `${start}-${previous}`);
    start = current;
    previous = current;
  }
  ranges.push(start === previous ? `${start}` : `${start}-${previous}`);
  return ranges.join(', ');
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        fontSize: 10,
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        color: 'var(--text-muted)',
        fontFamily: 'var(--font-mono)',
        marginBottom: 8,
      }}
    >
      {children}
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 12px',
  borderRadius: 'var(--radius-sm)',
  background: 'var(--bg-surface)',
  border: '1px solid var(--border-default)',
  color: 'var(--text-primary)',
  fontSize: 13,
  fontFamily: 'var(--font-sans)',
  outline: 'none',
};

const primaryBtnStyle: React.CSSProperties = {
  padding: '8px 24px',
  borderRadius: 'var(--radius-sm)',
  background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
  border: 'none',
  color: '#fff',
  fontSize: 13,
  fontWeight: 600,
  fontFamily: 'var(--font-sans)',
  transition: 'all 0.2s ease',
};

const secondaryBtnStyle: React.CSSProperties = {
  padding: '8px 20px',
  borderRadius: 'var(--radius-sm)',
  background: 'transparent',
  border: '1px solid var(--border-default)',
  color: 'var(--text-secondary)',
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
  fontFamily: 'var(--font-sans)',
};
