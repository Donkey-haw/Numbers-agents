import json
import unicodedata
from pathlib import Path
import fitz

def execute_curriculum_analysis(
    *,
    curriculum_pdf_path: Path,
    subject_name: str,
    run_root: Path,
    section_key: str,
    section_title: str,
    gemini_bin: str = "gemini",
    gemini_model: str | None = None,
    gemini_extensions: list[str] | None = None,
    approval_mode: str = "yolo",
    debug_artifacts: bool = False,
    timeout_sec: int = 300,
) -> dict:
    """Targeted alignment between a specific lesson and the National Curriculum."""
    import agent_runtime
    import pipeline_contracts as contracts
    import run_gemini_cli_pipeline as gemini_pipeline

    lesson_dir = run_root / "sections" / section_key
    lesson_analysis_path = lesson_dir / "lesson_analysis.json"
    
    if not lesson_analysis_path.exists():
        return {"status": "failed", "blocked_count": 1, "errors": [f"Lesson analysis not found: {lesson_analysis_path}"]}

    lesson_analysis = json.loads(lesson_analysis_path.read_text(encoding="utf-8"))
    
    # 1. Keywords for targeted search
    keywords = set([section_title, subject_name])
    keywords.update(lesson_analysis.get("key_concepts", [])[:3])
    keywords.update(lesson_analysis.get("vocabulary", [])[:3])
    
    # 2. Search PDF for relevant pages
    relevant_text = []
    try:
        with fitz.open(curriculum_pdf_path) as doc:
            matched_pages = set()
            # Basic keyword search to find relevant context
            for page_num in range(doc.page_count):
                page_text = doc[page_num].get_text("text")
                if any(kw.lower() in page_text.lower() for kw in keywords if kw):
                    matched_pages.add(page_num)
                if len(matched_pages) >= 5: # Limit to 5 most relevant pages
                    break
            
            # Plus always include the first 2 pages for general subject context
            matched_pages.update([0, 1])
            
            for p in sorted(matched_pages):
                if p < doc.page_count:
                    relevant_text.append(f"--- Page {p+1} ---\n{doc[p].get_text('text')}")
    except Exception as e:
        print(f"Warning: PDF search failed: {e}")

    context_str = "\n\n".join(relevant_text)

    # 3. Build targeted prompt
    task_prompt = (
        f"당신은 국가수준 교육과정 전문가입니다. 다음 수업 분석 결과({section_title})를 바탕으로,\n"
        "제시된 교육과정 원문에서 이 수업과 가장 핵심적으로 연관된 '성취기준'과 '교수학습 방법'을 찾아 정렬하십시오.\n\n"
        "### 수업 키워드\n"
        f"- 주제: {section_title}\n"
        f"- 핵심 개념: {', '.join(lesson_analysis.get('key_concepts', []))}\n"
        f"- 학습 목표: {', '.join(lesson_analysis.get('learning_goals', []))}\n\n"
        "### 교육과정 원문 (검색된 부분)\n"
        f"{context_str}\n\n"
        "### 요구사항\n"
        "1. 교과서의 학습 목표가 교육과정의 성취기준과 정합하는지 확인하십시오.\n"
        "2. 해당 차시 수업에서 강조해야 할 교육과정상의 '교수학습 유의사항'을 추출하십시오.\n"
        "3. 결과를 curriculum_alignment.json 형식으로 반환하십시오.\n"
    )
    
    prompt = agent_runtime.build_agent_prompt(
        agent_name="curriculum_analysis_agent",
        task_prompt=task_prompt
    )
    
    if debug_artifacts:
        (lesson_dir / "curriculum_alignment.prompt.md").write_text(prompt, encoding="utf-8")
    
    try:
        result_json, _ = gemini_pipeline.invoke_gemini_json(
            prompt=prompt,
            artifact_dir=lesson_dir,
            stem="curriculum_alignment_ai",
            gemini_bin=gemini_bin,
            gemini_model=gemini_model,
            gemini_extensions=gemini_extensions or ["stitch-skills"],
            approval_mode=approval_mode,
            debug_artifacts=debug_artifacts,
            timeout_sec=timeout_sec,
        )
        
        output_path = lesson_dir / "curriculum_alignment.json"
        contracts.write_json(output_path, result_json)
        
        return {
            "alignment_path": str(output_path),
            "status": "succeeded",
            "warning_count": 0,
            "blocked_count": 0
        }
    except Exception as e:
        return {
            "status": "failed",
            "blocked_count": 1,
            "errors": [f"Gemini alignment failed: {e}"]
        }
