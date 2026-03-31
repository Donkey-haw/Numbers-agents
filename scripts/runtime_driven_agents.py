import json
import re
import sys
from pathlib import Path

import fitz

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import agent_runtime  # noqa: E402
import generate_numbers_lesson as textbook  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402

TOKEN_RE = re.compile(r"[0-9A-Za-z가-힣·]+")
GENERIC_QUERY_TERMS = {
    "알아보기",
    "살펴보기",
    "이해하기",
    "파악하기",
    "탐구하기",
    "표현하기",
    "설명하기",
    "해보기",
    "하기",
    "의미",
    "특징",
    "방법",
    "활용",
    "이용해",
    "이용한",
    "이용",
}
INTRO_SIGNALS = (
    "이 주제를 배우면",
    "낱말 구름",
    "빙고 놀이",
    "열려라 이야기",
    "외쳐라 빙고",
)


def infer_document_kind(path: Path) -> str:
    lowered = path.name.lower()
    if "진도표" in path.name:
        return "schedule_chart"
    if any(token in path.name for token in ("부도", "익힘", "실험관찰")):
        return "supplement"
    if lowered.endswith(".pdf"):
        return "textbook"
    return "unknown"


def build_document_inventory(documents: list[dict], project_root: Path | None = None) -> dict:
    entries = []
    seen_ids = set()
    for index, item in enumerate(documents, start=1):
        raw_path = Path(item["path"])
        normalized_path = raw_path if raw_path.is_absolute() else ((project_root / raw_path) if project_root else raw_path)
        normalized_path = normalized_path.resolve()
        document_id = item.get("document_id") or contracts.sanitize_name(normalized_path.stem) or f"document_{index:03d}"
        while document_id in seen_ids:
            document_id = f"{document_id}_{index:03d}"
        seen_ids.add(document_id)
        entries.append(
            {
                "document_id": document_id,
                "path": str(normalized_path),
                "kind": item.get("kind") or infer_document_kind(normalized_path),
                "exists": normalized_path.exists(),
                "label": item.get("label") or normalized_path.stem,
                "notes": item.get("notes", ""),
            }
        )
    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "documents": entries,
    }


def execute_document_inventory(*, documents: list[dict], run_root: Path, run_id: str, project_root: Path | None = None) -> dict:
    agent_name = "document_inventory_agent"
    source_dir = run_root / "source"
    output_path = source_dir / "document_inventory.json"
    status_path = source_dir / "document_inventory.status.json"
    context = {"run_root": str(run_root.resolve())}

    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": agent_name,
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [item["path"] for item in documents],
        "output_refs": [str(output_path), str(status_path)],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path(agent_name)),
        "runtime_driven": True,
    }
    contracts.write_json(status_path, status)

    try:
        missing_required = agent_runtime.find_missing_input_refs(agent_name, context=context, base_dir=PROJECT_ROOT)
        if missing_required:
            raise FileNotFoundError(f"Missing required agent inputs: {missing_required}")

        inventory = build_document_inventory(documents, project_root=project_root or PROJECT_ROOT)
        contracts.write_json(output_path, inventory)
        missing_documents = [entry["path"] for entry in inventory["documents"] if not entry["exists"]]
        if missing_documents:
            status["status"] = "blocked"
            status["errors"].extend([f"Missing document: {path}" for path in missing_documents])
        else:
            status["status"] = "succeeded"
    except Exception as exc:
        status["status"] = "failed"
        status["errors"].append(str(exc))
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        raise

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "document_inventory_path": output_path,
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]) if status["status"] == "blocked" else 0,
    }


def load_document_inventory(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_page_texts(pdf_path: Path, document_id: str) -> dict:
    doc = fitz.open(pdf_path)
    try:
        pages = []
        for page_num in range(1, doc.page_count + 1):
            pages.append(
                {
                    "page": page_num,
                    "text": doc[page_num - 1].get_text("text"),
                }
            )
    finally:
        doc.close()

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "document_id": document_id,
        "page_count": len(pages),
        "pages": pages,
    }


def execute_pdf_extract(*, run_root: Path, run_id: str) -> dict:
    agent_name = "pdf_extract_agent"
    source_dir = run_root / "source"
    inventory_path = source_dir / "document_inventory.json"
    status_path = source_dir / "pdf_extract.status.json"

    inventory = load_document_inventory(inventory_path)
    pdf_documents = [
        document
        for document in inventory.get("documents", [])
        if document.get("exists") and str(document.get("path", "")).lower().endswith(".pdf")
    ]
    output_refs = [str(source_dir / f"{document['document_id']}.page_texts.json") for document in pdf_documents]
    output_refs.append(str(status_path))

    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": agent_name,
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(inventory_path)],
        "output_refs": output_refs,
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path(agent_name)),
        "runtime_driven": True,
    }
    contracts.write_json(status_path, status)

    try:
        missing_required = agent_runtime.find_missing_input_refs(agent_name, base_dir=PROJECT_ROOT)
        if missing_required:
            raise FileNotFoundError(f"Missing required agent inputs: {missing_required}")

        if not pdf_documents:
            status["status"] = "blocked"
            status["errors"].append("No extractable PDF documents were found in document_inventory.json")
        else:
            for document in pdf_documents:
                output_path = source_dir / f"{document['document_id']}.page_texts.json"
                payload = extract_page_texts(Path(document["path"]), document["document_id"])
                contracts.write_json(output_path, payload)
            status["status"] = "succeeded"
    except Exception as exc:
        status["status"] = "failed"
        status["errors"].append(str(exc))
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        raise

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]) if status["status"] == "blocked" else 0,
    }


def load_page_texts(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def tokenize_text(text: str, *, max_tokens: int = 40) -> list[str]:
    seen = set()
    tokens = []
    for match in TOKEN_RE.findall(normalize_text(text)):
        token = match.strip().lower()
        if len(token) < 2 or token in seen:
            continue
        seen.add(token)
        tokens.append(token)
        if len(tokens) >= max_tokens:
            break
    return tokens


def query_focus_terms(query: str) -> list[str]:
    normalized = normalize_text(query)
    normalized = re.sub(r"(알아보기|살펴보기|이해하기|파악하기|탐구하기|표현하기|설명하기|해 보기)$", "", normalized).strip()
    normalized = re.sub(r"(무엇일까요|어떻게[^ ]*|왜[^ ]*|할까요)$", "", normalized).strip()

    parts = [normalized]
    for piece in re.split(r"\s*(?:와|과|및|그리고|,|/)\s*", normalized):
        piece = piece.strip()
        if piece:
            parts.append(piece)

    focused = []
    seen = set()
    for part in parts:
        part = re.sub(
            r"(의 의미|의 특징|의 역할|의 구성과 하는 일|의 구성|하는 일|위치를 표현하는 방법|위치 특징|영토 특징|생활 모습의 차이|생활 문화|과정|필요성|중요성)$",
            "",
            part,
        ).strip()
        for token in tokenize_text(part, max_tokens=8):
            token = token.strip().lower()
            if len(token) < 2 or token in GENERIC_QUERY_TERMS or token in seen:
                continue
            seen.add(token)
            focused.append(token)
    return focused


def phrase_match_score(text: str, phrase: str) -> float:
    compact_text = re.sub(r"\s+", "", text.lower())
    compact_phrase = re.sub(r"\s+", "", phrase.lower())
    if not compact_phrase:
        return 0.0
    if compact_phrase in compact_text:
        return 6.0 + min(4.0, len(compact_phrase) / 8)
    if compact_text in compact_phrase and len(compact_text) >= 4:
        return 2.0
    return 0.0


def heading_candidates(text: str, *, max_candidates: int = 5) -> list[str]:
    candidates = []
    seen = set()
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split()).strip()
        if len(line) < 4 or len(line) > 80:
            continue
        token_count = len(TOKEN_RE.findall(line))
        if token_count < 2 or token_count > 14:
            continue
        if line in seen:
            continue
        seen.add(line)
        candidates.append(line)
        if len(candidates) >= max_candidates:
            break
    return candidates


def build_page_index(page_texts: dict) -> dict:
    pages = []
    for page in page_texts.get("pages", []):
        text = page.get("text", "")
        normalized = normalize_text(text)
        pages.append(
            {
                "page": page["page"],
                "excerpt": normalized[:160],
                "tokens": tokenize_text(text),
                "heading_candidates": heading_candidates(text),
            }
        )
    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "document_id": page_texts["document_id"],
        "pages": pages,
    }


def execute_page_index(*, run_root: Path, run_id: str) -> dict:
    agent_name = "page_index_agent"
    source_dir = run_root / "source"
    status_path = source_dir / "page_index.status.json"
    page_text_paths = sorted(source_dir.glob("*.page_texts.json"))
    output_refs = [str(source_dir / path.name.replace(".page_texts.json", ".page_index.json")) for path in page_text_paths]
    output_refs.append(str(status_path))

    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": agent_name,
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(path) for path in page_text_paths],
        "output_refs": output_refs,
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path(agent_name)),
        "runtime_driven": True,
    }
    contracts.write_json(status_path, status)

    try:
        if not page_text_paths:
            status["status"] = "blocked"
            status["errors"].append("No page_texts artifacts were found")
        else:
            for input_path in page_text_paths:
                page_texts = load_page_texts(input_path)
                output_path = source_dir / input_path.name.replace(".page_texts.json", ".page_index.json")
                contracts.write_json(output_path, build_page_index(page_texts))
            status["status"] = "succeeded"
    except Exception as exc:
        status["status"] = "failed"
        status["errors"].append(str(exc))
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        raise

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]) if status["status"] == "blocked" else 0,
    }


def infer_unit_title(section: dict) -> str:
    title = str(section.get("title", "")).strip()
    if "—" in title:
        return title.split("—", 1)[0].strip()
    return title or section.get("sheet_name", "Untitled Unit")


def build_schedule_structure_from_config(config: dict) -> dict:
    units = []
    current_unit = None
    current_unit_title = None

    for index, section in enumerate(config.get("sections", []), start=1):
        unit_title = infer_unit_title(section)
        if current_unit is None or unit_title != current_unit_title:
            current_unit = {
                "unit_id": f"unit-{len(units) + 1:03d}",
                "title": unit_title,
                "lessons": [],
            }
            units.append(current_unit)
            current_unit_title = unit_title

        current_unit["lessons"].append(
            {
                "lesson_id": f"lesson-{index:03d}",
                "sheet_name": section.get("sheet_name", f"{index}차시"),
                "title": section.get("title", section.get("sheet_name", f"{index}차시")),
                "raw_text": section.get("title", ""),
            }
        )

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "units": units,
    }


def execute_schedule_parse(*, config_path: Path, run_root: Path, run_id: str) -> dict:
    agent_name = "schedule_parse_agent"
    source_dir = run_root / "source"
    inventory_path = source_dir / "document_inventory.json"
    output_path = source_dir / "schedule_structure.json"
    status_path = source_dir / "schedule_parse.status.json"

    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": agent_name,
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(config_path), str(inventory_path)],
        "output_refs": [str(output_path), str(status_path)],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path(agent_name)),
        "runtime_driven": True,
    }
    contracts.write_json(status_path, status)

    try:
        config = textbook.load_config(config_path)
        schedule_structure = build_schedule_structure_from_config(config)
        if not schedule_structure["units"]:
            status["status"] = "blocked"
            status["errors"].append("No units could be derived from config sections")
        else:
            contracts.write_json(output_path, schedule_structure)
            status["status"] = "succeeded"
            if not any(len(unit.get("lessons", [])) for unit in schedule_structure["units"]):
                status["status"] = "blocked"
                status["errors"].append("Derived units did not contain any lessons")
    except Exception as exc:
        status["status"] = "failed"
        status["errors"].append(str(exc))
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        raise

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "schedule_structure_path": output_path,
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]) if status["status"] == "blocked" else 0,
    }


def load_schedule_structure(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def split_display_and_query(title: str) -> tuple[str, str]:
    normalized = normalize_text(title)
    if "—" in normalized:
        left, right = [part.strip() for part in normalized.split("—", 1)]
        if right:
            return normalized, right
    return normalized, normalized


def build_lesson_queries_from_schedule(schedule_structure: dict) -> dict:
    lessons = []
    ordered_lessons = []
    for unit in schedule_structure.get("units", []):
        for lesson in unit.get("lessons", []):
            ordered_lessons.append(lesson)

    for index, lesson in enumerate(ordered_lessons):
        display_title, title_query = split_display_and_query(lesson.get("title", lesson["sheet_name"]))
        next_display_title = None
        if index + 1 < len(ordered_lessons):
            next_display_title, _ = split_display_and_query(ordered_lessons[index + 1].get("title", ordered_lessons[index + 1]["sheet_name"]))
        lessons.append(
            {
                "lesson_id": lesson["lesson_id"],
                "sheet_name": lesson["sheet_name"],
                "display_title": display_title,
                "title_query": title_query,
                "end_before_query": next_display_title,
                "resource_id": "main",
            }
        )

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "lessons": lessons,
    }


def execute_lesson_query(*, run_root: Path, run_id: str) -> dict:
    agent_name = "lesson_query_agent"
    source_dir = run_root / "source"
    schedule_path = source_dir / "schedule_structure.json"
    output_path = source_dir / "lesson_queries.json"
    status_path = source_dir / "lesson_query.status.json"

    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": agent_name,
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(schedule_path)],
        "output_refs": [str(output_path), str(status_path)],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path(agent_name)),
        "runtime_driven": True,
    }
    contracts.write_json(status_path, status)

    try:
        schedule_structure = load_schedule_structure(schedule_path)
        lesson_queries = build_lesson_queries_from_schedule(schedule_structure)
        if not lesson_queries["lessons"]:
            status["status"] = "blocked"
            status["errors"].append("No lessons could be derived from schedule_structure.json")
        else:
            contracts.write_json(output_path, lesson_queries)
            status["status"] = "succeeded"
    except Exception as exc:
        status["status"] = "failed"
        status["errors"].append(str(exc))
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        raise

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "lesson_queries_path": output_path,
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]) if status["status"] == "blocked" else 0,
    }


def load_page_index(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_page_candidate_prompt(lesson: dict, page_index: dict) -> str:
    compact_pages = []
    query = lesson.get("title_query", lesson.get("display_title", ""))
    focus_terms = query_focus_terms(query)
    for page in page_index.get("pages", []):
        heading_text = " ".join(str(item) for item in page.get("heading_candidates", [])[:5])
        excerpt = page.get("excerpt", "")
        haystack = f"{heading_text} {excerpt}".lower()
        if focus_terms and not any(term in haystack for term in focus_terms):
            continue
        compact_pages.append(
            {
                "page": page.get("page"),
                "excerpt": excerpt,
                "heading_candidates": page.get("heading_candidates", [])[:5],
            }
        )
    if not compact_pages:
        compact_pages = [
            {
                "page": page.get("page"),
                "excerpt": page.get("excerpt", ""),
                "heading_candidates": page.get("heading_candidates", [])[:5],
            }
            for page in page_index.get("pages", [])
        ]

    schema = gemini_pipeline.load_schema(PROJECT_ROOT / "schemas" / "page_candidates.schema.json")
    task = (
        "입력된 lesson query와 교과서 page summary를 비교해서 현재 lesson 하나의 candidate_pages를 추려라.\n"
        "규칙:\n"
        "- boundaries 배열이 아니라 lessons 배열에는 반드시 현재 lesson 하나만 넣는다.\n"
        "- candidate_pages는 relevance 기준으로 최대 8페이지까지만 고른다.\n"
        "- 실제 lesson 시작/핵심 활동/정리 페이지를 포함할 수 있다.\n"
        "- 다른 단원 페이지는 피한다.\n"
        "출력은 JSON만 반환하고 schema를 지켜라.\n\n"
        "[current_lesson]\n"
        f"{json.dumps(lesson, ensure_ascii=False, indent=2)}\n\n"
        "[page_index.json]\n"
        f"{json.dumps({'document_id': page_index.get('document_id', 'main'), 'pages': compact_pages}, ensure_ascii=False, indent=2)}\n\n"
        "[schema]\n"
        f"{json.dumps(schema, ensure_ascii=False, indent=2)}"
    )
    return agent_runtime.build_agent_prompt(agent_name="page_candidate_agent", task_prompt=task)


def validate_page_candidates(payload: dict) -> None:
    schema = gemini_pipeline.load_schema(PROJECT_ROOT / "schemas" / "page_candidates.schema.json")
    gemini_pipeline.ensure_required_fields(payload, schema["required"], "page_candidates")
    if not isinstance(payload.get("lessons"), list):
        raise ValueError("page_candidates.lessons must be a list")
    normalized_lessons = []
    for lesson in payload["lessons"]:
        gemini_pipeline.ensure_required_fields(
            lesson,
            schema["properties"]["lessons"]["items"]["required"],
            "page_candidates.lesson",
        )
        pages = []
        seen = set()
        for page in lesson.get("candidate_pages", []):
            try:
                page_num = int(page)
            except (TypeError, ValueError):
                continue
            if page_num < 1 or page_num in seen:
                continue
            seen.add(page_num)
            pages.append(page_num)
        lesson["candidate_pages"] = pages[:8]
        normalized_lessons.append(lesson)
    payload["lessons"] = normalized_lessons


def invoke_page_candidate_for_lesson(
    *,
    source_dir: Path,
    lesson: dict,
    page_index: dict,
    gemini_bin: str,
    gemini_model: str | None,
    gemini_extensions: list[str],
    approval_mode: str,
    debug_artifacts: bool,
    gemini_timeout_sec: int | None,
    gemini_idle_timeout_sec: int | None,
) -> dict:
    prompt = build_page_candidate_prompt(lesson, page_index)
    stem = f"page_candidate_{contracts.sanitize_name(lesson.get('lesson_id', 'lesson'))}"
    payload, _ = gemini_pipeline.invoke_gemini_json(
        prompt,
        source_dir,
        stem,
        gemini_bin=gemini_bin,
        gemini_model=gemini_model,
        gemini_extensions=gemini_extensions,
        approval_mode=approval_mode,
        debug_artifacts=debug_artifacts,
        timeout_sec=gemini_timeout_sec,
        idle_timeout_sec=gemini_idle_timeout_sec,
    )
    validate_page_candidates(payload)
    lessons = payload.get("lessons", [])
    if len(lessons) != 1:
        raise ValueError(f"page_candidate for {lesson.get('lesson_id')} must return exactly 1 lesson")
    return lessons[0]


def build_boundary_decision_prompt(
    lesson: dict,
    *,
    prev_lesson: dict | None,
    next_lesson: dict | None,
    page_index: dict,
) -> str:
    interesting_pages = set()
    for candidate_lesson in [item for item in (prev_lesson, lesson, next_lesson) if item]:
        for page in candidate_lesson.get("candidate_pages", []):
            page_num = int(page)
            for neighbor in range(max(1, page_num - 2), page_num + 3):
                interesting_pages.add(neighbor)

    compact_pages = []
    for page in page_index.get("pages", []):
        page_num = int(page.get("page", 0))
        if page_num not in interesting_pages:
            continue
        compact_pages.append(
            {
                "page": page_num,
                "excerpt": page.get("excerpt", ""),
                "heading_candidates": page.get("heading_candidates", [])[:5],
            }
        )

    schema = gemini_pipeline.load_schema(PROJECT_ROOT / "schemas" / "boundary_decisions.schema.json")
    task = (
        "입력된 후보 페이지와 page summary를 보고 현재 lesson 하나의 start_page/end_page를 결정하라.\n"
        "규칙:\n"
        "- 현재 lesson은 이전 lesson보다 뒤에서 시작해야 한다.\n"
        "- 가능하면 `이 주제를 배우면`, `낱말 구름`, `빙고 놀이` 같은 주제 도입 페이지를 포함한다.\n"
        "- 가능하면 다음 lesson 시작 직전에서 현재 lesson을 끝낸다.\n"
        "- 근거가 약하면 low_confidence, 찾지 못하면 not_found로 둔다.\n"
        "- boundaries 배열에는 반드시 현재 lesson 하나만 넣는다.\n"
        "출력은 JSON만 반환하고 schema를 지켜라.\n\n"
        "[current_lesson]\n"
        f"{json.dumps(lesson, ensure_ascii=False, indent=2)}\n\n"
        "[previous_lesson]\n"
        f"{json.dumps(prev_lesson, ensure_ascii=False, indent=2) if prev_lesson else 'null'}\n\n"
        "[next_lesson]\n"
        f"{json.dumps(next_lesson, ensure_ascii=False, indent=2) if next_lesson else 'null'}\n\n"
        "[page_index_subset.json]\n"
        f"{json.dumps({'document_id': page_index.get('document_id', 'main'), 'pages': compact_pages}, ensure_ascii=False, indent=2)}\n\n"
        "[schema]\n"
        f"{json.dumps(schema, ensure_ascii=False, indent=2)}"
    )
    return agent_runtime.build_agent_prompt(agent_name="boundary_decision_agent", task_prompt=task)


def validate_boundary_decisions(payload: dict) -> None:
    schema = gemini_pipeline.load_schema(PROJECT_ROOT / "schemas" / "boundary_decisions.schema.json")
    gemini_pipeline.ensure_required_fields(payload, schema["required"], "boundary_decisions")
    if not isinstance(payload.get("boundaries"), list):
        raise ValueError("boundary_decisions.boundaries must be a list")
    for item in payload["boundaries"]:
        gemini_pipeline.ensure_required_fields(
            item,
            schema["properties"]["boundaries"]["items"]["required"],
            "boundary_decisions.boundary",
        )
        if item.get("start_page") is not None:
            item["start_page"] = int(item["start_page"])
        if item.get("end_page") is not None:
            item["end_page"] = int(item["end_page"])
        item["confidence"] = float(item.get("confidence", 0.0))
        item["evidence_pages"] = [int(page) for page in item.get("evidence_pages", []) if int(page) > 0]


def invoke_boundary_decision_for_lesson(
    *,
    source_dir: Path,
    lesson: dict,
    prev_lesson: dict | None,
    next_lesson: dict | None,
    page_index: dict,
    gemini_bin: str,
    gemini_model: str | None,
    gemini_extensions: list[str],
    approval_mode: str,
    debug_artifacts: bool,
    gemini_timeout_sec: int | None,
    gemini_idle_timeout_sec: int | None,
) -> dict:
    prompt = build_boundary_decision_prompt(
        lesson,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson,
        page_index=page_index,
    )
    stem = f"boundary_decision_{contracts.sanitize_name(lesson.get('lesson_id', 'lesson'))}"
    payload, _ = gemini_pipeline.invoke_gemini_json(
        prompt,
        source_dir,
        stem,
        gemini_bin=gemini_bin,
        gemini_model=gemini_model,
        gemini_extensions=gemini_extensions,
        approval_mode=approval_mode,
        debug_artifacts=debug_artifacts,
        timeout_sec=gemini_timeout_sec,
        idle_timeout_sec=gemini_idle_timeout_sec,
    )
    validate_boundary_decisions(payload)
    boundaries = payload.get("boundaries", [])
    if len(boundaries) != 1:
        raise ValueError(f"boundary_decision for {lesson.get('lesson_id')} must return exactly 1 boundary")
    return boundaries[0]


def execute_page_candidate(
    *,
    run_root: Path,
    run_id: str,
    gemini_bin: str = "gemini",
    gemini_model: str | None = None,
    gemini_extensions: list[str] | None = None,
    approval_mode: str = "yolo",
    debug_artifacts: bool = False,
    gemini_timeout_sec: int | None = 120,
    gemini_idle_timeout_sec: int | None = None,
) -> dict:
    agent_name = "page_candidate_agent"
    source_dir = run_root / "source"
    lesson_queries_path = source_dir / "lesson_queries.json"
    page_index_path = source_dir / "main.page_index.json"
    output_path = source_dir / "page_candidates.json"
    status_path = source_dir / "page_candidate.status.json"

    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": agent_name,
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(lesson_queries_path), str(page_index_path)],
        "output_refs": [str(output_path), str(status_path)],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path(agent_name)),
        "runtime_driven": True,
    }
    contracts.write_json(status_path, status)

    try:
        lesson_queries = json.loads(lesson_queries_path.read_text(encoding="utf-8"))
        page_index = load_page_index(page_index_path)
        lessons = []
        for lesson in lesson_queries.get("lessons", []):
            candidate_lesson = invoke_page_candidate_for_lesson(
                source_dir=source_dir,
                lesson=lesson,
                page_index=page_index,
                gemini_bin=gemini_bin,
                gemini_model=gemini_model,
                gemini_extensions=gemini_extensions or ["stitch-skills"],
                approval_mode=approval_mode,
                debug_artifacts=debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec,
                gemini_idle_timeout_sec=gemini_idle_timeout_sec,
            )
            lessons.append(candidate_lesson)
        candidates = {
            "schema_version": contracts.SCHEMA_VERSION,
            "lessons": lessons,
        }
        validate_page_candidates(candidates)
        if not candidates["lessons"]:
            status["status"] = "blocked"
            status["errors"].append("No lesson candidates could be derived")
        else:
            empty_candidates = [item["lesson_id"] for item in candidates["lessons"] if not item["candidate_pages"]]
            if empty_candidates:
                status["warnings"].append(f"{len(empty_candidates)} lessons did not produce candidate pages")
            contracts.write_json(output_path, candidates)
            status["status"] = "succeeded_with_warning" if status["warnings"] else "succeeded"
    except Exception as exc:
        status["status"] = "failed"
        status["errors"].append(str(exc))
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        raise

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "page_candidates_path": output_path,
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]) if status["status"] == "blocked" else 0,
    }


def load_page_candidates(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def has_intro_signal(page: dict) -> bool:
    haystacks = [str(page.get("excerpt", ""))] + [str(item) for item in page.get("heading_candidates", [])]
    joined = " ".join(haystacks)
    return any(signal in joined for signal in INTRO_SIGNALS)


def execute_boundary_decision(
    *,
    run_root: Path,
    run_id: str,
    gemini_bin: str = "gemini",
    gemini_model: str | None = None,
    gemini_extensions: list[str] | None = None,
    approval_mode: str = "yolo",
    debug_artifacts: bool = False,
    gemini_timeout_sec: int | None = 120,
    gemini_idle_timeout_sec: int | None = None,
) -> dict:
    agent_name = "boundary_decision_agent"
    source_dir = run_root / "source"
    input_path = source_dir / "page_candidates.json"
    page_index_path = source_dir / "main.page_index.json"
    output_path = source_dir / "boundary_decisions.json"
    status_path = source_dir / "boundary_decision.status.json"

    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": agent_name,
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(input_path), str(page_index_path)],
        "output_refs": [str(output_path), str(status_path)],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path(agent_name)),
        "runtime_driven": True,
    }
    contracts.write_json(status_path, status)

    try:
        page_candidates = load_page_candidates(input_path)
        page_index = load_page_index(page_index_path)
        lessons = page_candidates.get("lessons", [])
        boundaries = []
        for index, lesson in enumerate(lessons):
            prev_lesson = lessons[index - 1] if index > 0 else None
            next_lesson = lessons[index + 1] if index + 1 < len(lessons) else None
            boundary = invoke_boundary_decision_for_lesson(
                source_dir=source_dir,
                lesson=lesson,
                prev_lesson=prev_lesson,
                next_lesson=next_lesson,
                page_index=page_index,
                gemini_bin=gemini_bin,
                gemini_model=gemini_model,
                gemini_extensions=gemini_extensions or ["stitch-skills"],
                approval_mode=approval_mode,
                debug_artifacts=debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec,
                gemini_idle_timeout_sec=gemini_idle_timeout_sec,
            )
            boundaries.append(boundary)
        boundary_decisions = {
            "schema_version": contracts.SCHEMA_VERSION,
            "boundaries": boundaries,
        }
        validate_boundary_decisions(boundary_decisions)
        if not boundary_decisions["boundaries"]:
            status["status"] = "blocked"
            status["errors"].append("No boundary decisions could be derived")
        else:
            unresolved = [item["lesson_id"] for item in boundary_decisions["boundaries"] if item["status"] == "not_found"]
            low_confidence = [item["lesson_id"] for item in boundary_decisions["boundaries"] if item["status"] == "low_confidence"]
            if unresolved:
                status["warnings"].append(f"{len(unresolved)} lessons could not be resolved from candidate pages")
            if low_confidence:
                status["warnings"].append(f"{len(low_confidence)} lessons were marked low_confidence")
            contracts.write_json(output_path, boundary_decisions)
            status["status"] = "succeeded_with_warning" if status["warnings"] else "succeeded"
    except Exception as exc:
        status["status"] = "failed"
        status["errors"].append(str(exc))
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        raise

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "boundary_decisions_path": output_path,
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]) if status["status"] == "blocked" else 0,
    }


def load_boundary_decisions(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_boundary_validation(boundary_decisions: dict) -> dict:
    blocking_issues = []
    warnings = []
    entries = []

    previous_end = None
    for item in boundary_decisions.get("boundaries", []):
        lesson_id = item["lesson_id"]
        status = item.get("status", "unknown")
        start_page = item.get("start_page")
        end_page = item.get("end_page")
        message = ""

        if status == "not_found":
            blocking_issues.append(f"{lesson_id}: boundary was not resolved")
            message = "boundary was not resolved"
        elif start_page is None or end_page is None:
            blocking_issues.append(f"{lesson_id}: boundary pages are incomplete")
            message = "boundary pages are incomplete"
        elif int(end_page) < int(start_page):
            blocking_issues.append(f"{lesson_id}: boundary range is inverted")
            message = "boundary range is inverted"
        else:
            if previous_end is not None and int(start_page) <= int(previous_end):
                warnings.append(f"{lesson_id}: start_page overlaps with previous lesson boundary")
                message = "boundary overlaps with previous lesson"
            if status == "low_confidence":
                warnings.append(f"{lesson_id}: boundary is low_confidence")
                if not message:
                    message = "boundary is low_confidence"
            previous_end = end_page

        entries.append(
            {
                "lesson_id": lesson_id,
                "resource_id": item["resource_id"],
                "status": status,
                "message": message or "ok",
            }
        )

    overall_status = "succeeded"
    if blocking_issues:
        overall_status = "blocked"
    elif warnings:
        overall_status = "succeeded_with_warning"

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "status": overall_status,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "entries": entries,
    }


def execute_boundary_validation(*, run_root: Path, run_id: str) -> dict:
    agent_name = "boundary_validation_agent"
    source_dir = run_root / "source"
    input_path = source_dir / "boundary_decisions.json"
    output_path = source_dir / "boundary_validation.json"
    status_path = source_dir / "boundary_validation.status.json"

    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": agent_name,
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(input_path)],
        "output_refs": [str(output_path), str(status_path)],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path(agent_name)),
        "runtime_driven": True,
    }
    contracts.write_json(status_path, status)

    try:
        boundary_decisions = load_boundary_decisions(input_path)
        validation = build_boundary_validation(boundary_decisions)
        contracts.write_json(output_path, validation)
        status["warnings"].extend(validation.get("warnings", []))
        status["errors"].extend(validation.get("blocking_issues", []))
        status["status"] = validation["status"]
    except Exception as exc:
        status["status"] = "failed"
        status["errors"].append(str(exc))
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        raise

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "boundary_validation_path": output_path,
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]) if status["status"] == "blocked" else 0,
    }
