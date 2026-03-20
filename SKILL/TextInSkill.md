---
name: "TextBookInSkill"
description: "Use when turning a textbook PDF plus a lesson progress chart into an Apple Numbers file with one sheet per lesson, using the repo's HTML screenshot and AppleScript pipeline."
---

# TextBookInSkill

## When To Use
- The user wants to place textbook pages into Apple Numbers.
- The user provides a textbook PDF and a lesson schedule image or a page-range plan.
- The user wants one Numbers sheet per lesson or per class period.

## Required Inputs
- A textbook PDF.
- A Numbers template file to clone.
- A lesson breakdown:
  - Preferred: JSON config with sheet names and lesson titles.
  - Acceptable: progress chart image that can be converted into a draft config with the OCR helper.

## Core Rule
- Ignore progress-chart page numbers entirely.
- Always analyze the textbook PDF first.
- Build each sheet from the page where that lesson title appears through the page just before the next lesson title appears.
- For the last lesson, stop at the next unit heading or another explicit boundary such as `end_before_query`.

## Repo Workflow
1. Work inside the project root that contains `PROCESS.md`.
2. Analyze the textbook PDF first and identify where each lesson title actually appears in the book.
3. If the user only gave a progress chart image, create a draft config:

```bash
python3 scripts/draft_config_from_progress_chart.py \
  --image <chart.png> \
  --project-root . \
  --pdf-path "<textbook.pdf>" \
  --output-file "output/draft.numbers" \
  --config-output "configs/draft.json" \
  --footer "<footer>" \
  --start-after "<unit heading>" \
  --stop-before "<next heading>" \
  --end-before-query "<next unit title>"
```

4. Review the draft config and fix any OCR mistakes in lesson titles.
5. Convert the lesson plan into a final JSON config under `configs/` if needed.
6. Run the generic generator:
```bash
python3 scripts/generate_numbers_lesson.py --config configs/<name>.json
```

7. Verify the generated `.numbers` file contains the expected sheet names.
8. Unless debugging is needed, let the generator clean temporary assets.

## Config Format
```json
{
  "project_root": "/absolute/path/to/project",
  "pdf_path": "[사회]6_1_교과서.pdf",
  "template_path": "빈 넘버스 파일.numbers",
  "output_file": "output/result.numbers",
  "footer": "사회 6-1 · 2단원 · 민주주의와 선거",
  "textbook_page_offset": 2,
  "end_before_query": "국가기관이 하는 일",
  "sections": [
    {
      "sheet_name": "2차시",
      "card_file": "democracy_election_2차시",
      "title": "선거란 무엇일까요?",
      "badge": "2차시",
      "accent": ["#6366f1", "#818cf8"]
    }
  ]
}
```

## Page Mapping Rule
- `textbook_page_offset` converts PDF page numbers into printed textbook page labels.
- Example: if printed page 26 appears on PDF page 28, offset is `2`.
- Do not trust or reuse page numbers from the progress chart.
- The generator searches the PDF text for each lesson title and infers the page span from the next lesson title.
- For the last lesson, provide either `end_before_query` or `unit_end_page`.

## Validation Checklist
- Output `.numbers` file exists.
- Sheet names match the config order exactly.
- The original PDF and original Numbers template remain unchanged.

## Debugging
- Keep intermediate assets when needed:

```bash
python3 scripts/generate_numbers_lesson.py --config configs/<name>.json --keep-assets
```

- Skip Numbers insertion to debug HTML/card generation only:

```bash
python3 scripts/generate_numbers_lesson.py --config configs/<name>.json --skip-numbers --keep-assets
```

## OCR Notes
- OCR uses macOS Vision via [ocr_progress_chart.swift](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/ocr_progress_chart.swift).
- Use `--start-after` and `--stop-before` to isolate the target unit when the chart image contains multiple units.
- OCR should extract lesson names only. Ignore chart page numbers even if they are visible.
- Always review the draft config before generation.

## Notes
- Numbers automation requires macOS with the Numbers app installed.
