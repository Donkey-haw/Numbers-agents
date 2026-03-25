import argparse
import asyncio
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


TEXT_CACHE_KEY = "_pdf_text_cache"
NORMALIZED_TEXT_CACHE_KEY = "_pdf_normalized_text_cache"
ROLE_META = {
    "textbook": {"icon": "📖", "asset_type": "textbook_card", "label_suffix": "교과서"},
    "supplement": {"icon": "📚", "asset_type": "supplement_card", "label_suffix": "추가자료"},
    "reference": {"icon": "📎", "asset_type": "supplement_card", "label_suffix": "참고자료"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to JSON config file")
    parser.add_argument("--keep-assets", action="store_true", help="Keep generated page/card assets")
    parser.add_argument("--skip-numbers", action="store_true", help="Skip AppleScript insertion step")
    return parser.parse_args()


def load_config(config_path: Path) -> dict:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    project_root = Path(data["project_root"])
    data["project_root"] = project_root

    def resolve_project_path(value: str | Path) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return project_root / path

    data["template_path"] = resolve_project_path(data["template_path"])
    data["output_file"] = resolve_project_path(data["output_file"])
    data["pages_dir"] = project_root / "assets" / "pages"
    data["cards_dir"] = project_root / "assets" / "cards"
    data["html_dir"] = project_root / "html"

    resources = data.get("resources")
    if resources:
        normalized_resources = []
        for index, resource in enumerate(resources, start=1):
            normalized = dict(resource)
            resource_id = normalized.get("resource_id")
            if not resource_id:
                raise RuntimeError(f"Resource #{index} is missing resource_id")
            normalized["pdf_path"] = resolve_project_path(normalized["pdf_path"])
            normalized.setdefault("label", resource_id)
            normalized.setdefault("kind", "textbook")
            normalized_resources.append(normalized)
        data["resources"] = normalized_resources
    else:
        data["pdf_path"] = resolve_project_path(data["pdf_path"])
        data["resources"] = [
            {
                "resource_id": "main",
                "label": "교과서",
                "kind": "textbook",
                "pdf_path": data["pdf_path"],
            }
        ]

    resources_by_id = {resource["resource_id"]: resource for resource in data["resources"]}
    data["resources_by_id"] = resources_by_id
    main_resource = next(
        (resource for resource in data["resources"] if resource.get("kind") == "textbook"),
        data["resources"][0],
    )
    data["pdf_path"] = main_resource["pdf_path"]

    for section in data["sections"]:
        sources = section.get("sources")
        if not sources:
            sources = [
                {
                    "resource_id": main_resource["resource_id"],
                    "role": "textbook",
                    "title_query": section.get("title_query", section["title"]),
                }
            ]
        normalized_sources = []
        for source in sources:
            normalized_source = dict(source)
            resource_id = normalized_source["resource_id"]
            if resource_id not in resources_by_id:
                raise RuntimeError(
                    f"Section '{section['sheet_name']}' references unknown resource_id '{resource_id}'"
                )
            normalized_source.setdefault("role", "textbook")
            normalized_source.setdefault("title_query", section.get("title_query", section["title"]))
            if "pdf_pages" not in normalized_source and "pdf_pages" in section:
                normalized_source["pdf_pages"] = list(section["pdf_pages"])
            normalized_sources.append(normalized_source)
        section["sources"] = normalized_sources
    return data


def normalize_text(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", text)


def get_page_text(
    doc: fitz.Document,
    page_num: int,
    text_cache: dict[int, str],
    normalized_cache: dict[int, str] | None = None,
) -> str:
    text = text_cache.get(page_num)
    if text is None:
        text = doc[page_num - 1].get_text("text")
        text_cache[page_num] = text
    if normalized_cache is None:
        return text
    normalized = normalized_cache.get(page_num)
    if normalized is None:
        normalized = normalize_text(text)
        normalized_cache[page_num] = normalized
    return normalized


def find_query_pages(doc: fitz.Document, query: str, start_page: int = 1) -> list[int]:
    text_cache = getattr(doc, TEXT_CACHE_KEY, None)
    if text_cache is None:
        text_cache = {}
        setattr(doc, TEXT_CACHE_KEY, text_cache)
    normalized_cache = getattr(doc, NORMALIZED_TEXT_CACHE_KEY, None)
    if normalized_cache is None:
        normalized_cache = {}
        setattr(doc, NORMALIZED_TEXT_CACHE_KEY, normalized_cache)

    normalized_query = normalize_text(query)
    hits = []
    for page_num in range(start_page, doc.page_count + 1):
        normalized_text = get_page_text(doc, page_num, text_cache, normalized_cache)
        if normalized_query and normalized_query in normalized_text:
            hits.append(page_num)
    return hits


def infer_section_pages(config: dict) -> None:
    sections = config["sections"]
    if all("source_ranges" in section for section in sections):
        return
    if all("pdf_pages" in section for section in sections) and all("sources" not in section or len(section["sources"]) == 1 for section in sections):
        return

    docs = {resource["resource_id"]: fitz.open(resource["pdf_path"]) for resource in config["resources"]}
    resource_search_starts = {
        resource["resource_id"]: int(resource.get("search_start_page", config.get("search_start_page", 1)))
        for resource in config["resources"]
    }

    try:
        for index, section in enumerate(sections):
            source_ranges = []
            for source in section["sources"]:
                resource_id = source["resource_id"]
                doc = docs[resource_id]

                if "pdf_pages" in source:
                    start_page = min(source["pdf_pages"])
                    end_page = max(source["pdf_pages"])
                else:
                    current_search_start = int(source.get("search_start_page", resource_search_starts[resource_id]))
                    query = source.get("title_query") or section.get("title_query") or section["title"]
                    matches = find_query_pages(doc, query, current_search_start)
                    if not matches:
                        if source.get("optional"):
                            continue
                        raise RuntimeError(
                            f"Could not infer start page for section '{section['sheet_name']}'"
                            f" source '{resource_id}' from query '{query}'"
                        )
                    start_page = matches[0]

                    next_query = None
                    for next_section in sections[index + 1 :]:
                        matching_source = next(
                            (candidate for candidate in next_section["sources"] if candidate["resource_id"] == resource_id),
                            None,
                        )
                        if matching_source is not None:
                            next_query = matching_source.get("title_query") or next_section.get("title_query") or next_section["title"]
                            break

                    if next_query:
                        next_matches = find_query_pages(doc, next_query, start_page + 1)
                        if not next_matches:
                            if source.get("optional"):
                                continue
                            raise RuntimeError(
                                f"Could not infer next section start for resource '{resource_id}' from query '{next_query}'"
                            )
                        end_page = next_matches[0] - 1
                    else:
                        end_query = source.get("end_before_query") or config.get("end_before_query")
                        if end_query:
                            end_matches = find_query_pages(doc, end_query, start_page + 1)
                            if not end_matches:
                                if source.get("optional"):
                                    continue
                                raise RuntimeError(
                                    f"Could not infer end_before_query for resource '{resource_id}' from '{end_query}'"
                                )
                            end_page = end_matches[0] - 1
                        elif source.get("unit_end_page") or config.get("unit_end_page"):
                            end_page = int(source.get("unit_end_page") or config["unit_end_page"])
                        else:
                            raise RuntimeError(
                                f"Last section '{section['sheet_name']}' source '{resource_id}' needs"
                                " end_before_query or unit_end_page"
                            )

                if end_page < start_page:
                    raise RuntimeError(
                        f"Inferred invalid page range for '{section['sheet_name']}' source '{resource_id}':"
                        f" {start_page}..{end_page}"
                    )

                source["pdf_pages"] = list(range(start_page, end_page + 1))
                resource_search_starts[resource_id] = end_page + 1
                source_ranges.append(
                    {
                        "resource_id": resource_id,
                        "role": source.get("role", "textbook"),
                        "pdf_pages": source["pdf_pages"],
                    }
                )

            section["source_ranges"] = source_ranges
            primary_source = next(
                (item for item in source_ranges if item["role"] == "textbook"),
                source_ranges[0],
            )
            section["pdf_pages"] = primary_source["pdf_pages"]
    finally:
        for doc in docs.values():
            doc.close()


def ensure_dirs(config: dict) -> None:
    for key in ("pages_dir", "cards_dir", "html_dir", "output_file"):
        path = config[key]
        if key == "output_file":
            path.parent.mkdir(parents=True, exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)


def copy_template(config: dict) -> None:
    source = config["template_path"]
    target = config["output_file"]
    if target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)


def extract_pages(config: dict) -> list[Path]:
    generated = []
    docs: dict[str, fitz.Document] = {}
    try:
        for section in config["sections"]:
            for source_card in section_source_cards(section, config):
                resource_id = source_card["resource_id"]
                if resource_id not in docs:
                    docs[resource_id] = fitz.open(config["resources_by_id"][resource_id]["pdf_path"])
                doc = docs[resource_id]
                for page_num in source_card["pdf_pages"]:
                    output_path = page_image_path(config, resource_id, page_num)
                    if output_path.exists():
                        generated.append(output_path)
                        continue
                    page = doc[page_num - 1]
                    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
                    pix.save(output_path)
                    generated.append(output_path)
    finally:
        for doc in docs.values():
            doc.close()
    return generated


def page_image_path(config: dict, resource_id: str, page_num: int) -> Path:
    return config["pages_dir"] / f"{resource_id}_p{page_num}.png"


def build_page_markup(source_card: dict, config: dict) -> str:
    items = []
    for page_num in source_card["pdf_pages"]:
        img_src = page_image_path(config, source_card["resource_id"], page_num).as_posix()
        items.append(
            f"""
        <div class="page-wrapper">
          <img src="{html.escape(img_src)}" alt="p.{page_num}">
        </div>""".rstrip()
        )
    return "\n".join(items)


def section_source_cards(section: dict, config: dict) -> list[dict]:
    cards = []
    for index, source in enumerate(section.get("source_ranges", []), start=1):
        resource = config["resources_by_id"][source["resource_id"]]
        role = source.get("role", "textbook")
        meta = ROLE_META.get(role, ROLE_META["supplement"])
        stem = section["card_file"] if role == "textbook" else f"{section['card_file']}__{source['resource_id']}"
        label = resource.get("label", source["resource_id"])
        cards.append(
            {
                "asset_id": stem,
                "card_stem": stem,
                "sheet_name": section["sheet_name"],
                "resource_id": source["resource_id"],
                "resource_label": label,
                "role": role,
                "asset_type": meta["asset_type"],
                "icon": meta["icon"],
                "label_suffix": meta["label_suffix"],
                "title": section["title"],
                "badge": section["badge"],
                "accent": section["accent"],
                "pdf_pages": source["pdf_pages"],
                "insert_order": 1 if role == "textbook" else 10 + index,
            }
        )
    if not cards:
        raise RuntimeError(f"Section '{section['sheet_name']}' has no source_ranges to render")
    return cards


def render_html(source_card: dict, config: dict) -> str:
    accent_start, accent_end = source_card["accent"]
    grid_columns = 1 if len(source_card["pdf_pages"]) == 1 else 2
    title = html.escape(source_card["title"])
    badge = html.escape(source_card["badge"])
    footer = html.escape(config["footer"])
    pages = build_page_markup(source_card, config)
    resource_chip = html.escape(f"{source_card['resource_label']} · {source_card['label_suffix']}")
    icon = source_card["icon"]
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Noto Sans KR', sans-serif; width: 1600px; background: transparent; }}
.card {{ width: 1600px; background: linear-gradient(145deg, #ffffff 0%, #f8faff 100%); border-radius: 32px; border: 1px solid #e2e8f0; box-shadow: 0 20px 60px -15px rgba(0, 0, 0, 0.08); overflow: hidden; }}
.card-top {{ background: linear-gradient(135deg, {accent_start} 0%, {accent_end} 100%); padding: 28px 40px; display: flex; align-items: center; justify-content: space-between; gap: 16px; }}
.heading {{ display: flex; flex-direction: column; gap: 10px; }}
.card-top h1 {{ color: #fff; font-size: 28px; font-weight: 900; letter-spacing: -0.5px; }}
.resource-chip {{ display: inline-flex; align-items: center; gap: 8px; width: fit-content; background: rgba(255, 255, 255, 0.16); color: #fff; font-size: 13px; font-weight: 700; padding: 6px 12px; border-radius: 999px; }}
.badge {{ flex-shrink: 0; background: rgba(255, 255, 255, 0.2); color: #fff; font-size: 15px; font-weight: 700; padding: 6px 18px; border-radius: 999px; }}
.grid {{ display: grid; grid-template-columns: repeat({grid_columns}, minmax(0, 1fr)); gap: 16px; padding: 24px; }}
.page-wrapper {{ position: relative; }}
.page-wrapper img {{ width: 100%; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06); }}
.card-bottom {{ padding: 18px 40px; background: #faf5ff; border-top: 1px solid #ede9fe; color: #7c3aed; font-size: 14px; font-weight: 600; }}
</style>
</head>
<body>
  <div class="card">
    <div class="card-top">
      <div class="heading">
        <h1>{icon} {title}</h1>
        <div class="resource-chip">{resource_chip}</div>
      </div>
      <div class="badge">{badge}</div>
    </div>
    <div class="grid">
{pages}
    </div>
    <div class="card-bottom">• {footer}</div>
  </div>
</body>
</html>
"""


async def capture_cards(config: dict) -> list[dict]:
    generated: list[dict] = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        for section in config["sections"]:
            for source_card in section_source_cards(section, config):
                html_path = config["html_dir"] / f"{source_card['card_stem']}.html"
                card_path = config["cards_dir"] / f"{source_card['card_stem']}.png"
                html_path.write_text(render_html(source_card, config), encoding="utf-8")
                page = await browser.new_page(viewport={"width": 1700, "height": 2600}, device_scale_factor=2)
                await page.goto(html_path.as_uri(), wait_until="domcontentloaded")
                await wait_for_render_ready(page, ".card")
                capture = await screenshot_capture_root(page, card_path, [".card"])
                await page.close()
                generated.append(
                    {
                        "asset_id": source_card["asset_id"],
                        "card_stem": source_card["card_stem"],
                        "sheet_name": source_card["sheet_name"],
                        "asset_type": source_card["asset_type"],
                        "resource_id": source_card["resource_id"],
                        "insert_order": source_card["insert_order"],
                        "html_path": html_path,
                        "image_path": card_path,
                        "capture_size": capture,
                    }
                )
        await browser.close()
    return generated


async def wait_for_render_ready(page, root_selector: str) -> None:
    try:
        await page.wait_for_selector(root_selector, state="visible", timeout=5000)
    except PlaywrightTimeoutError:
        await page.wait_for_selector("body", state="visible")
        await page.wait_for_function(
            """() => {
                const body = document.body;
                return body && body.children && body.children.length > 0;
            }""",
            timeout=5000,
        )
    try:
        await page.wait_for_load_state("networkidle", timeout=5000)
    except PlaywrightTimeoutError:
        pass
    try:
        await page.evaluate(
            """async () => {
                if (document.fonts && document.fonts.ready) {
                    await document.fonts.ready;
                }
            }"""
        )
    except Exception:
        pass


async def screenshot_capture_root(page, output_path: Path, selectors: list[str]) -> dict[str, int]:
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            count = await page.locator(selector).count()
        except Exception:
            count = 0
        if count < 1:
            continue
        try:
            await locator.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pass
        box = await locator.bounding_box()
        await locator.screenshot(path=str(output_path))
        if not box:
            raise RuntimeError(f"Could not measure capture root for selector: {selector}")
        return {
            "width": max(1, round(box["width"])),
            "height": max(1, round(box["height"])),
        }
    raise RuntimeError(f"Could not find capture root from selectors: {selectors}")


def generated_html_paths(config: dict) -> list[Path]:
    paths = []
    for section in config["sections"]:
        for source_card in section_source_cards(section, config):
            paths.append(config["html_dir"] / f"{source_card['card_stem']}.html")
    return paths


def scaled_height(capture_size: dict[str, int], target_width: int) -> int:
    width = capture_size["width"]
    height = capture_size["height"]
    if width <= 0:
        raise RuntimeError(f"Invalid capture width: {width}")
    return max(1, round((target_width / width) * height))


def build_applescript(config: dict, card_assets: list[dict]) -> str:
    output_file = config["output_file"].as_posix()
    assets_by_stem = {asset["card_stem"]: asset for asset in card_assets}
    textbook_width = 980
    supplement_width = 980
    textbook_gap = 24
    supplement_gap = 24
    blocks = []
    for index, section in enumerate(config["sections"], start=1):
        section_cards = section_source_cards(section, config)
        textbook_cards = [card for card in section_cards if card["asset_type"] == "textbook_card"]
        supplement_cards = [card for card in section_cards if card["asset_type"] == "supplement_card"]
        open_sheet_block = f"""
\t\tif {index} is 1 then
\t\t\ttell sheet 1 of myDoc
\t\t\t\tset name to "{section["sheet_name"]}"
\t\t\tend tell
\t\t\tset targetSheet to sheet 1 of myDoc
\t\telse
\t\t\ttell myDoc
\t\t\t\tset targetSheet to make new sheet with properties {{name:"{section["sheet_name"]}"}}
\t\t\tend tell
\t\tend if
\t\ttell targetSheet
\t\t\ttry
\t\t\t\tdelete every table
\t\t\tend try
\t\t\ttry
\t\t\t\tdelete every image
\t\t\tend try
\t\t\ttry
\t\t\t\tdelete every text item
\t\t\tend try
\t\t\ttry
\t\t\t\tdelete every shape
\t\t\tend try
"""
        asset_lines = []
        textbook_x = 20
        textbook_bottom = 20
        textbook_positions: list[int] = []
        for card in textbook_cards:
            image_path = (config["cards_dir"] / f"{card['card_stem']}.png").as_posix()
            capture_asset = assets_by_stem[card["card_stem"]]
            image_height = scaled_height(capture_asset["capture_size"], textbook_width)
            asset_lines.append(
                f"""\t\t\tset cardImage to make new image with properties {{file:POSIX file "{image_path}"}}\n"""
                f"""\t\t\tset position of cardImage to {{{textbook_x}, 20}}\n"""
                f"""\t\t\tset width of cardImage to {textbook_width}\n"""
            )
            textbook_positions.append(textbook_x)
            textbook_x += textbook_width + textbook_gap
            textbook_bottom = max(textbook_bottom, 20 + image_height)
        supplement_y = textbook_bottom + 24
        fallback_supplement_x = 20
        for supplement_index, card in enumerate(supplement_cards):
            image_path = (config["cards_dir"] / f"{card['card_stem']}.png").as_posix()
            if textbook_positions:
                supplement_x = textbook_positions[min(supplement_index, len(textbook_positions) - 1)]
            else:
                supplement_x = fallback_supplement_x
            asset_lines.append(
                f"""\t\t\tset supplementImage to make new image with properties {{file:POSIX file "{image_path}"}}\n"""
                f"""\t\t\tset position of supplementImage to {{{supplement_x}, {supplement_y}}}\n"""
                f"""\t\t\tset width of supplementImage to {supplement_width}\n"""
            )
            if not textbook_positions:
                fallback_supplement_x += supplement_width + supplement_gap
        close_sheet_block = "\t\tend tell\n"
        blocks.append(open_sheet_block + "".join(asset_lines) + close_sheet_block)

    return f"""set sourceFile to POSIX file "{output_file}"

tell application "Numbers"
\tactivate
\tset myDoc to open sourceFile
\tdelay 2
\ttry
\t\trepeat while (count of sheets of myDoc) > 1
\t\t\tdelete last sheet of myDoc
\t\tend repeat
\tend try
{''.join(blocks)}
\tsave myDoc
\tset sheetInfo to {{}}
\trepeat with s in sheets of myDoc
\t\tcopy (name of s) to end of sheetInfo
\tend repeat
\tclose myDoc
\treturn sheetInfo
end tell
"""


def parse_sheet_info(stdout: str) -> list[str]:
    return [item.strip() for item in stdout.strip().split(",") if item.strip()]


def insert_into_numbers(config: dict, card_assets: list[dict]) -> list[str]:
    script = build_applescript(config, card_assets)
    with tempfile.NamedTemporaryFile("w", suffix=".scpt", delete=False, encoding="utf-8") as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        result = subprocess.run(["osascript", str(script_path)], check=True, capture_output=True, text=True)
    finally:
        script_path.unlink(missing_ok=True)
    return parse_sheet_info(result.stdout)


def verify_output(config: dict, actual_sheet_names: list[str] | None = None) -> None:
    if not config["output_file"].exists():
        raise RuntimeError("Output .numbers file was not created")
    expected = [section["sheet_name"] for section in config["sections"]]
    if actual_sheet_names is None:
        script = f"""
tell application "Numbers"
    set myDoc to open POSIX file "{config["output_file"].as_posix()}"
    delay 2
    tell myDoc
        set sheetInfo to {{}}
        repeat with s in sheets
            copy (name of s) to end of sheetInfo
        end repeat
        close saving yes
        return sheetInfo
    end tell
end tell
"""
        result = subprocess.run(["osascript", "-e", script], check=True, capture_output=True, text=True)
        actual = parse_sheet_info(result.stdout)
    else:
        actual = actual_sheet_names
    if actual != expected:
        raise RuntimeError(f"Sheet verification failed: expected {expected}, got {actual}")


def cleanup(paths: list[Path]) -> None:
    for path in paths:
        if path.exists():
            path.unlink()


def main(cli_args: argparse.Namespace | None = None) -> int:
    args = cli_args or parse_args()
    config = load_config(Path(args.config))
    ensure_dirs(config)
    infer_section_pages(config)
    copy_template(config)
    page_assets = extract_pages(config)
    card_assets = asyncio.run(capture_cards(config))
    html_assets = generated_html_paths(config)
    try:
        if not args.skip_numbers:
            inserted_sheets = insert_into_numbers(config, card_assets)
            verify_output(config, inserted_sheets)
    finally:
        if not args.keep_assets:
            cleanup(page_assets + [asset["image_path"] for asset in card_assets] + html_assets)
    print(config["output_file"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
