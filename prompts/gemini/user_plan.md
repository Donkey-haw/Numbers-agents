Generate one `activity_plan` JSON object from the lesson analysis below.

Lesson analysis:
{analysis_json}

Target schema:
{schema_json}

Requirements:
- Return 1 to 3 activities.
- Keep every activity grounded in the lesson analysis.
- Set `lesson_id` to match the lesson analysis.
- Use `activity_type: "freeform_html"` unless there is a strong reason not to.
- Put the full standalone HTML document for the card in `html_content`.
- The HTML must be self-contained and ready for screenshot capture.
- Follow `NumbersDesign.md` principles:
  - strong badge system
  - light section background
  - bold black writing-area borders
  - large iPad writing zones
  - clear typography and spacing
- Keep the outer page background transparent or white. Do not add a gray canvas behind the card.
- Increase vertical writing space so students can handwrite with Apple Pencil comfortably.
- Prefer card heights that feel roomy, not compact.
- If you generate a note-style card, treat it as a place to organize what students heard during class.
- For note-style cards, prefer labels such as `수업시간에 들은 내용 정리`, `오늘 수업 핵심 정리`, `설명 들으며 메모한 내용`.
- Keep prompts short enough to fit an iPad worksheet.
- `student_writing_zones` may be an empty array when `html_content` already defines the full layout.
- Output a single JSON object only.
