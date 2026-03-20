Generate one `activity_plan` JSON object from the lesson analysis below.

Lesson analysis:
{analysis_json}

Target schema:
{schema_json}

Requirements:
- Return 1 to 3 activities.
- Keep every activity grounded in the lesson analysis.
- Use only these activity types unless the schema allows another supported value:
  - `learning_note`
  - `see_think_wonder`
  - `worksheet`
- Set `lesson_id` to match the lesson analysis.
- Include practical `student_writing_zones`.
- Keep prompts short enough to fit an iPad worksheet.
- Output a single JSON object only.
