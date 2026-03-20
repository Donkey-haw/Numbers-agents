import argparse
import asyncio
import json
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

Image.MAX_IMAGE_PIXELS = None

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_numbers_lesson as textbook  # noqa: E402
import render_activity_html as activity_html  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to textbook config JSON")
    parser.add_argument(
        "--activity-plan",
        action="append",
        required=True,
        help="Path to activity_plan JSON. Repeat to include multiple lesson plans.",
    )
    parser.add_argument("--manifest-output", help="Optional render manifest output path")
    parser.add_argument("--keep-assets", action="store_true", help="Keep generated html/png assets")
    parser.add_argument(
        "--include-status",
        nargs="*",
        default=["approved"],
        help="review_status values to render from activity plan",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def lesson_key(section: dict) -> str:
    return section.get("lesson_id", section["sheet_name"])


def load_activity_plan(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_activity_html_files(
    plans: list[tuple[Path, dict]],
    config: dict,
    include_status: set[str],
) -> list[tuple[dict, Path, Path]]:
    rendered: list[tuple[dict, Path, Path]] = []
    for plan_path, plan in plans:
        for activity in plan["activities"]:
            if activity["review_status"] not in include_status:
                continue
            renderer = activity_html.RENDERERS.get(activity["activity_type"])
            if renderer is None:
                continue
            html_text = renderer(activity)
            html_path = config["html_dir"] / f"activity_{activity['activity_id']}.html"
            html_path.write_text(html_text, encoding="utf-8")
            rendered.append((activity, html_path, plan_path))
    if not rendered:
        raise RuntimeError(f"No activities were rendered for statuses: {sorted(include_status)}")
    return rendered


async def capture_html_files(
    html_pairs: list[tuple[dict, Path, Path]],
    config: dict,
) -> list[tuple[dict, Path, Path, Path]]:
    captured: list[tuple[dict, Path, Path, Path]] = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        for activity, html_path, plan_path in html_pairs:
            image_path = config["cards_dir"] / f"activity_{activity['activity_id']}.png"
            page = await browser.new_page(viewport={"width": 1700, "height": 2600}, device_scale_factor=2)
            await page.goto(html_path.as_uri())
            await page.wait_for_timeout(1200)
            await page.screenshot(path=str(image_path), full_page=True)
            await page.close()
            captured.append((activity, html_path, image_path, plan_path))
        await browser.close()
    return captured


def compute_scaled_height(image_path: Path, target_width: int) -> int:
    with Image.open(image_path) as image:
        width, height = image.size
    return round(height * (target_width / width))


def build_manifest(
    config: dict,
    textbook_html_paths: list[Path],
    textbook_card_paths: list[Path],
    activity_assets: list[tuple[dict, Path, Path, Path]],
) -> dict:
    html_by_name = {path.stem: path for path in textbook_html_paths}
    assets = []
    order_by_sheet = defaultdict(int)

    for section in config["sections"]:
        order_by_sheet[section["sheet_name"]] += 1
        card_name = f"{section['card_file']}.png"
        image_path = next(path for path in textbook_card_paths if path.name == card_name)
        html_path = html_by_name[section["card_file"]]
        assets.append(
            {
                "asset_id": section["card_file"],
                "asset_type": "textbook_card",
                "sheet_name": section["sheet_name"],
                "insert_order": order_by_sheet[section["sheet_name"]],
                "html_path": str(html_path),
                "image_path": str(image_path),
                "dimensions": {"width": 980, "height": compute_scaled_height(image_path, 980)},
            }
        )

    section_by_key = {lesson_key(section): section["sheet_name"] for section in config["sections"]}
    for activity, html_path, image_path, plan_path in activity_assets:
        sheet_name = section_by_key.get(activity["lesson_id"])
        if sheet_name is None:
            raise RuntimeError(f"Activity lesson_id '{activity['lesson_id']}' does not match any section")
        order_by_sheet[sheet_name] += 1
        assets.append(
            {
                "asset_id": activity["activity_id"],
                "asset_type": "activity_sheet",
                "sheet_name": sheet_name,
                "insert_order": order_by_sheet[sheet_name],
                "html_path": str(html_path),
                "image_path": str(image_path),
                "source_json": str(plan_path.resolve()),
                "dimensions": {"width": 980, "height": compute_scaled_height(image_path, 980)},
            }
        )

    assets.sort(key=lambda item: (item["sheet_name"], item["insert_order"]))
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "output_file": str(config["output_file"]),
        "assets": assets,
    }


def build_applescript(config: dict, manifest: dict) -> str:
    sheet_names = [section["sheet_name"] for section in config["sections"]]
    assets_by_sheet: dict[str, list[dict]] = defaultdict(list)
    for asset in manifest["assets"]:
        assets_by_sheet[asset["sheet_name"]].append(asset)

    blocks = []
    for index, sheet_name in enumerate(sheet_names, start=1):
        assets = assets_by_sheet[sheet_name]
        open_sheet_block = f"""
\t\tif {index} is 1 then
\t\t\ttell sheet 1 of myDoc
\t\t\t\tset name to "{sheet_name}"
\t\t\tend tell
\t\t\tset targetSheet to sheet 1 of myDoc
\t\telse
\t\t\ttell myDoc
\t\t\t\tset targetSheet to make new sheet with properties {{name:"{sheet_name}"}}
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
\t\t\tset currentY to 20
"""
        asset_lines = []
        for asset in assets:
            image_path = asset["image_path"]
            height = asset["dimensions"]["height"]
            asset_lines.append(
                f"""\t\t\tset nextImage to make new image with properties {{file:POSIX file "{image_path}"}}\n"""
                f"""\t\t\tset position of nextImage to {{20, currentY}}\n"""
                f"""\t\t\tset width of nextImage to 980\n"""
                f"""\t\t\tset currentY to currentY + {height} + 24\n"""
            )
        close_sheet_block = "\t\tend tell\n"
        blocks.append(open_sheet_block + "".join(asset_lines) + close_sheet_block)

    return f"""set sourceFile to POSIX file "{config["output_file"].as_posix()}"

tell application "Numbers"
\tactivate
\tset myDoc to open sourceFile
\tdelay 2
{''.join(blocks)}
\tsave myDoc
\tclose myDoc
end tell
"""


def insert_manifest_into_numbers(config: dict, manifest: dict) -> None:
    import subprocess

    script = build_applescript(config, manifest)
    with tempfile.NamedTemporaryFile("w", suffix=".scpt", delete=False, encoding="utf-8") as handle:
        handle.write(script)
        script_path = Path(handle.name)
    try:
        subprocess.run(["osascript", str(script_path)], check=True)
    finally:
        script_path.unlink(missing_ok=True)


def verify_manifest_output(config: dict) -> None:
    textbook.verify_output(config)


def cleanup(paths: list[Path]) -> None:
    for path in paths:
        if path.exists():
            path.unlink()


def default_manifest_output(config: dict) -> Path:
    return config["output_file"].with_suffix(".manifest.json")


def main(cli_args: argparse.Namespace | None = None) -> int:
    args = cli_args or parse_args()
    config = textbook.load_config(Path(args.config))
    textbook.ensure_dirs(config)
    textbook.infer_section_pages(config)
    textbook.copy_template(config)

    page_assets = textbook.extract_pages(config)
    textbook_card_paths = asyncio.run(textbook.capture_cards(config))
    textbook_html_paths = textbook.generated_html_paths(config)

    activity_plan_paths = [Path(path) for path in args.activity_plan]
    plans = [(path, load_activity_plan(path)) for path in activity_plan_paths]
    activity_html_pairs = render_activity_html_files(plans, config, set(args.include_status))
    activity_assets = asyncio.run(capture_html_files(activity_html_pairs, config))

    manifest = build_manifest(config, textbook_html_paths, textbook_card_paths, activity_assets)
    manifest_output = Path(args.manifest_output) if args.manifest_output else default_manifest_output(config)
    manifest_output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    insert_manifest_into_numbers(config, manifest)
    verify_manifest_output(config)

    if not args.keep_assets:
        cleanup(
            page_assets
            + textbook_card_paths
            + textbook_html_paths
            + [html_path for _, html_path, _ in activity_html_pairs]
            + [image_path for _, _, image_path, _ in activity_assets]
        )

    print(config["output_file"])
    print(manifest_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
