Generate one `lesson_analysis` JSON object for the section below.

Section:
{section_json}

Baseline lesson analysis:
{baseline_json}

Schedule draft:
{schedule_json}

Textbook context:
{context_json}

Target schema:
{schema_json}

Requirements:
- Preserve `sheet_name`, `lesson_id`, `lesson_title`, and `pdf_pages`.
- Improve `essential_question`, `learning_goals`, `key_concepts`, `vocabulary`, `misconceptions`, and `content_chunks` if the context supports it.
- `content_chunks` must stay grounded in the supplied `pdf_pages`.
- `source_page_refs` must match the actual section pages.
- Keep the result concise and classroom-usable.
- Output a single JSON object only.
