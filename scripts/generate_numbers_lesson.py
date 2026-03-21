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
    data["pdf_path"] = project_root / data["pdf_path"]
    data["template_path"] = project_root / data["template_path"]
    data["output_file"] = project_root / data["output_file"]
    data["pages_dir"] = project_root / "assets" / "pages"
    data["cards_dir"] = project_root / "assets" / "cards"
    data["html_dir"] = project_root / "html"
    return data


def normalize_text(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", text)


def find_query_pages(doc: fitz.Document, query: str, start_page: int = 1) -> list[int]:
    normalized_query = normalize_text(query)
    hits = []
    for page_num in range(start_page, doc.page_count + 1):
        text = doc[page_num - 1].get_text("text")
        if normalized_query and normalized_query in normalize_text(text):
            hits.append(page_num)
    return hits


def infer_section_pages(config: dict) -> None:
    sections = config["sections"]
    if all("pdf_pages" in section for section in sections):
        return

    doc = fitz.open(config["pdf_path"])
    current_search_start = int(config.get("search_start_page", 1))

    for index, section in enumerate(sections):
        if "pdf_pages" in section:
            current_search_start = max(section["pdf_pages"]) + 1
            continue

        query = section.get("title_query") or section["title"]
        matches = find_query_pages(doc, query, current_search_start)
        if not matches:
            raise RuntimeError(f"Could not infer start page for section '{section['sheet_name']}' from query '{query}'")
        start_page = matches[0]

        if index + 1 < len(sections):
            next_section = sections[index + 1]
            next_query = next_section.get("title_query") or next_section["title"]
            next_matches = find_query_pages(doc, next_query, start_page + 1)
            if not next_matches:
                raise RuntimeError(f"Could not infer next section start for '{next_section['sheet_name']}' from query '{next_query}'")
            end_page = next_matches[0] - 1
        else:
            end_query = config.get("end_before_query")
            if end_query:
                end_matches = find_query_pages(doc, end_query, start_page + 1)
                if not end_matches:
                    raise RuntimeError(f"Could not infer end_before_query page from '{end_query}'")
                end_page = end_matches[0] - 1
            elif config.get("unit_end_page"):
                end_page = int(config["unit_end_page"])
            else:
                raise RuntimeError(
                    f"Last section '{section['sheet_name']}' needs either 'unit_end_page' or 'end_before_query' in config"
                )

        if end_page < start_page:
            raise RuntimeError(f"Inferred invalid page range for '{section['sheet_name']}': {start_page}..{end_page}")

        section["pdf_pages"] = list(range(start_page, end_page + 1))
        current_search_start = end_page + 1


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
    doc = fitz.open(config["pdf_path"])
    generated = []
    target_pages = sorted({page for section in config["sections"] for page in section["pdf_pages"]})
    for page_num in target_pages:
        output_path = config["pages_dir"] / f"p{page_num}.png"
        page = doc[page_num - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
        pix.save(output_path)
        generated.append(output_path)
    return generated


def build_page_markup(section: dict, config: dict) -> str:
    items = []
    for page_num in section["pdf_pages"]:
        img_src = (config["pages_dir"] / f"p{page_num}.png").as_posix()
        items.append(
            f"""
        <div class="page-wrapper">
          <img src="{html.escape(img_src)}" alt="p.{page_num}">
        </div>""".rstrip()
        )
    return "\n".join(items)


def render_html(section: dict, config: dict) -> str:
    accent_start, accent_end = section["accent"]
    grid_columns = 1 if len(section["pdf_pages"]) == 1 else 2
    title = html.escape(section["title"])
    badge = html.escape(section["badge"])
    footer = html.escape(config["footer"])
    pages = build_page_markup(section, config)
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
.card-top h1 {{ color: #fff; font-size: 28px; font-weight: 900; letter-spacing: -0.5px; }}
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
      <h1>📖 {title}</h1>
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


async def capture_cards(config: dict) -> list[Path]:
    generated = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        for section in config["sections"]:
            html_path = config["html_dir"] / f"{section['card_file']}.html"
            card_path = config["cards_dir"] / f"{section['card_file']}.png"
            html_path.write_text(render_html(section, config), encoding="utf-8")
            page = await browser.new_page(viewport={"width": 1700, "height": 2600}, device_scale_factor=2)
            await page.goto(html_path.as_uri(), wait_until="domcontentloaded")
            await wait_for_render_ready(page, ".card")
            await page.screenshot(path=str(card_path), full_page=True)
            await page.close()
            generated.append(card_path)
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


def generated_html_paths(config: dict) -> list[Path]:
    return [config["html_dir"] / f"{section['card_file']}.html" for section in config["sections"]]


def build_applescript(config: dict) -> str:
    sheet_names = ", ".join(f'"{section["sheet_name"]}"' for section in config["sections"])
    image_names = ", ".join(f'"{section["card_file"]}.png"' for section in config["sections"])
    project_path = config["project_root"].as_posix()
    output_file = config["output_file"].as_posix()
    return f"""set projectPath to "{project_path}"
set sourceFile to POSIX file "{output_file}"

set sheetNames to {{{sheet_names}}}
set imageNames to {{{image_names}}}

tell application "Numbers"
\tactivate
\tset myDoc to open sourceFile
\tdelay 2
\trepeat with i from 1 to count of sheetNames
\t\tset targetSheetName to item i of sheetNames
\t\tset imagePath to projectPath & "/assets/cards/" & item i of imageNames
\t\tif i is 1 then
\t\t\ttell sheet 1 of myDoc
\t\t\t\tset name to targetSheetName
\t\t\tend tell
\t\t\tset targetSheet to sheet 1 of myDoc
\t\telse
\t\t\ttell myDoc
\t\t\t\tset targetSheet to make new sheet with properties {{name:targetSheetName}}
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
\t\t\tset cardImage to make new image with properties {{file:POSIX file imagePath}}
\t\t\tset position of cardImage to {{20, 20}}
\t\t\tset width of cardImage to 980
\t\tend tell
\tend repeat
\tsave myDoc
\tclose myDoc
end tell
"""


def insert_into_numbers(config: dict) -> None:
    script = build_applescript(config)
    with tempfile.NamedTemporaryFile("w", suffix=".scpt", delete=False, encoding="utf-8") as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        subprocess.run(["osascript", str(script_path)], check=True)
    finally:
        script_path.unlink(missing_ok=True)


def verify_output(config: dict) -> None:
    if not config["output_file"].exists():
        raise RuntimeError("Output .numbers file was not created")
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
    actual = [item.strip() for item in result.stdout.strip().split(",") if item.strip()]
    expected = [section["sheet_name"] for section in config["sections"]]
    if actual != expected:
        raise RuntimeError(f"Sheet verification failed: expected {expected}, got {actual}")


def cleanup(paths: list[Path]) -> None:
    for path in paths:
        if path.exists():
            path.unlink()


def main() -> int:
    args = parse_args()
    config = load_config(Path(args.config))
    ensure_dirs(config)
    infer_section_pages(config)
    copy_template(config)
    page_assets = extract_pages(config)
    card_assets = asyncio.run(capture_cards(config))
    html_assets = generated_html_paths(config)
    if not args.skip_numbers:
        insert_into_numbers(config)
        verify_output(config)
    if not args.keep_assets:
        cleanup(page_assets + card_assets + html_assets)
    print(config["output_file"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
