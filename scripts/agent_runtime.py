import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


AGENTS_ROOT = PROJECT_ROOT / "agents"
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
SUB_BULLET_RE = re.compile(r"^\s{2,}-\s+(.*\S)\s*$")
TOP_BULLET_RE = re.compile(r"^-\s+([^:]+):\s*$")
PLACEHOLDER_RE = re.compile(r"<([a-zA-Z0-9_]+)>")


def agent_doc_path(agent_name: str) -> Path:
    path = AGENTS_ROOT / agent_name / "AGENT.md"
    if not path.exists():
        raise FileNotFoundError(f"Agent document not found: {path}")
    return path


def load_agent_doc(agent_name: str) -> str:
    return agent_doc_path(agent_name).read_text(encoding="utf-8")


def _normalize_section_key(title: str) -> str:
    return title.strip().lower().replace(" ", "_")


def parse_agent_doc(agent_name: str) -> dict:
    text = load_agent_doc(agent_name)
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"Invalid AGENT.md title for {agent_name}")

    spec = {
        "agent_name": lines[0][2:].strip(),
        "path": str(agent_doc_path(agent_name)),
        "raw_text": text,
        "sections": {},
    }

    current_key = None
    current_title = None
    current_lines = []

    def flush_section() -> None:
        nonlocal current_key, current_title, current_lines
        if current_key is None or current_title is None:
            return
        spec["sections"][current_key] = {
            "title": current_title,
            "raw": "\n".join(current_lines).strip(),
            "parsed": parse_section_lines(current_lines),
        }
        current_key = None
        current_title = None
        current_lines = []

    for line in lines[1:]:
        match = SECTION_RE.match(line)
        if match:
            flush_section()
            current_title = match.group(1).strip()
            current_key = _normalize_section_key(current_title)
            current_lines = []
            continue
        if current_key is not None:
            current_lines.append(line)

    flush_section()
    return spec


def parse_section_lines(lines: list[str]) -> dict:
    text_lines = []
    groups = {}
    current_group = None

    for line in lines:
        stripped = line.rstrip()
        top_match = TOP_BULLET_RE.match(stripped)
        if top_match:
            current_group = top_match.group(1).strip()
            groups[current_group] = []
            continue

        sub_match = SUB_BULLET_RE.match(line)
        if sub_match and current_group:
            groups[current_group].append(sub_match.group(1).strip())
            continue

        if stripped.startswith("- "):
            text_lines.append(stripped[2:].strip())
            current_group = None
            continue

        if stripped:
            text_lines.append(stripped.strip())

    return {
        "items": text_lines,
        "groups": groups,
    }


def load_agent_spec(agent_name: str) -> dict:
    return parse_agent_doc(agent_name)


def summarize_agent_spec(agent_name: str) -> dict:
    spec = load_agent_spec(agent_name)
    sections = spec["sections"]
    return {
        "agent_name": spec["agent_name"],
        "path": spec["path"],
        "identity": sections.get("identity", {}).get("parsed", {}),
        "responsibility": sections.get("responsibility", {}).get("parsed", {}),
        "inputs": sections.get("inputs", {}).get("parsed", {}),
        "outputs": sections.get("outputs", {}).get("parsed", {}),
        "allowed_tools": sections.get("allowed_tools", {}).get("parsed", {}),
        "allowed_actions": sections.get("allowed_actions", {}).get("parsed", {}),
        "forbidden_actions": sections.get("forbidden_actions", {}).get("parsed", {}),
        "rules": sections.get("rules", {}).get("parsed", {}),
        "hook_contract": sections.get("hook_contract", {}).get("parsed", {}),
        "success_criteria": sections.get("success_criteria", {}).get("parsed", {}),
        "failure_modes": sections.get("failure_modes", {}).get("parsed", {}),
    }


def _strip_ticks(value: str) -> str:
    return value.strip().strip("`")


def render_artifact_ref(ref: str, context: dict | None = None) -> str:
    context = context or {}

    def replace(match: re.Match) -> str:
        key = match.group(1)
        return str(context.get(key, match.group(0)))

    return PLACEHOLDER_RE.sub(replace, _strip_ticks(ref))


def list_group(spec: dict, section_name: str, group_name: str) -> list[str]:
    section = spec.get(section_name, {})
    groups = section.get("groups", {}) if isinstance(section, dict) else {}
    return list(groups.get(group_name, []))


def list_items(spec: dict, section_name: str) -> list[str]:
    section = spec.get(section_name, {})
    return list(section.get("items", [])) if isinstance(section, dict) else []


def required_input_refs(agent_name: str, context: dict | None = None) -> list[str]:
    spec = summarize_agent_spec(agent_name)
    return [render_artifact_ref(item, context) for item in list_group(spec, "inputs", "required")]


def output_refs(agent_name: str, context: dict | None = None) -> list[str]:
    spec = summarize_agent_spec(agent_name)
    items = list_items(spec, "outputs")
    return [render_artifact_ref(item, context) for item in items]


def hook_trigger_refs(agent_name: str, context: dict | None = None) -> list[str]:
    spec = summarize_agent_spec(agent_name)
    return [render_artifact_ref(item, context) for item in list_group(spec, "hook_contract", "trigger_if_missing")]


def hook_unlocks(agent_name: str) -> list[str]:
    spec = summarize_agent_spec(agent_name)
    return [_strip_ticks(item) for item in list_group(spec, "hook_contract", "unlocks")]


def find_missing_input_refs(agent_name: str, *, context: dict | None = None, base_dir: Path | None = None) -> list[str]:
    missing = []
    for ref in required_input_refs(agent_name, context):
        if "*" in ref or "<" in ref or ">" in ref:
            continue
        if "/" not in ref and "\\" not in ref and "." not in Path(ref).name:
            continue
        candidate = Path(ref)
        if not candidate.is_absolute() and base_dir is not None:
            candidate = (base_dir / candidate).resolve()
        if not candidate.exists():
            missing.append(ref)
    return missing


def should_trigger_agent(agent_name: str, *, context: dict | None = None, base_dir: Path | None = None) -> bool:
    trigger_refs = hook_trigger_refs(agent_name, context)
    if not trigger_refs:
        return False
    for ref in trigger_refs:
        if "*" in ref or "<" in ref or ">" in ref:
            continue
        if "/" not in ref and "\\" not in ref and "." not in Path(ref).name:
            continue
        candidate = Path(ref)
        if not candidate.is_absolute() and base_dir is not None:
            candidate = (base_dir / candidate).resolve()
        if not candidate.exists():
            return True
    return False


def build_agent_prompt(*, agent_name: str, task_prompt: str) -> str:
    agent_doc = load_agent_doc(agent_name)
    return (
        f"# Runtime Agent Spec: {agent_name}\n\n"
        "아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.\n"
        "문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.\n"
        "출력 형식 요구가 있으면 반드시 지켜라.\n\n"
        f"{agent_doc}\n\n"
        "# Execution Task\n\n"
        f"{task_prompt}"
    )
