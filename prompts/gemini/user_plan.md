Generate one `activity_plan` JSON object from the lesson analysis below.

Lesson analysis:
{analysis_json}

Target schema:
{schema_json}

Shape example:
{example_json}

Requirements:
- Return 1 to 3 activities.
- Keep every activity grounded in the lesson analysis.
- Set `lesson_id` to match the lesson analysis.
- Set `object_role` on every activity:
  - `learning_note`
  - `activity_area`
  - `reference_material`
  - `worksheet`
  - `ai_courseware`
- Set `lesson_flow_stage` on every activity:
  - `before`
  - `during`
  - `after`
- Use `activity_type: "freeform_html"` unless there is a strong reason not to.
- Put the full standalone HTML document for the card in `html_content`.
- The HTML must be self-contained and ready for screenshot capture.
- Each activity must clearly act as `보완`, `심화`, or `확장`.
- Avoid simply copying the textbook's own question structure or swapping a few words from the textbook prompt.
- The card should open a different path toward the same learning goal.
- Use `NumbersDesign.md` this way:
  - treat it as a constraint and composition guide
  - do not merely restate one known template pattern
  - decide the card's object role first
  - decide whether it belongs to before-class, during-class, or after-class flow
  - design the structure around what students should actually do on the card
- Keep the outer page background transparent or white. Do not add a gray canvas behind the card.
- Increase vertical writing space so students can handwrite with Apple Pencil comfortably.
- Prefer card heights that feel roomy, not compact.
- When a card expects sustained handwriting, make at least one main writing region visibly large, usually `420px+`.
- Use object roles from `ACTIVITY_RULE.md` implicitly:
  - learning note
  - activity area
  - reference material
  - worksheet
  - AI-linked reflection or follow-up
- Use learning functions from `ACTIVITY_RULE.md` implicitly:
  - creative expression
  - reasoning / problem solving
  - foundational practice
- If you generate a note-style card, treat it as a place to organize what students heard during class.
- For note-style cards, prefer labels such as `수업시간에 들은 내용 정리`, `오늘 수업 핵심 정리`, `설명 들으며 메모한 내용`.
- If you generate a creative card, provide a light scaffold or example cue.
- If you generate a reasoning card, make the thinking steps writable.
- If you generate a practice card, provide enough repeated writing space.
- Keep prompts short enough to fit an iPad worksheet.
- Even when `html_content` defines the full layout, include `student_writing_zones` that describe the real writable regions.
- Make the intended student action obvious without relying on long explanation text.
- Avoid making all cards look like the same repeated badge + intro + three-box pattern.
- Good directions include:
  - applying the idea to a new real-life case
  - making a claim and supporting it with evidence
  - comparing two choices, media messages, systems, or viewpoints
  - redesigning, planning, or proposing a better action
  - connecting the lesson to the student's own experience or decision
- Weak directions include:
  - rewriting textbook definitions
  - copying textbook diagrams into empty boxes
  - asking for an answer that is already directly printed on the textbook page
- The example above is only a shape contract.
- Do not copy its topic, wording, colors, or exact structure.
- Output a single JSON object only.
