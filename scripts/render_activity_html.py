import argparse
import html
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--activity-plan", required=True, help="Path to activity_plan json")
    parser.add_argument("--output-dir", required=True, help="Directory to write rendered html files")
    parser.add_argument("--include-status", nargs="*", default=["approved"], help="review_status values to render")
    return parser.parse_args()


def load_activity_plan(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def level_label(level: str) -> str:
    mapping = {
        "core": "기초",
        "on-level": "기본",
        "extension": "심화",
    }
    return mapping.get(level, level)


def render_learning_note(activity: dict) -> str:
    summary_label = activity["student_writing_zones"][0]["label"] if activity["student_writing_zones"] else "오늘 내용 요약"
    question_label = activity["student_writing_zones"][1]["label"] if len(activity["student_writing_zones"]) > 1 else "질문 / 메모"
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{esc(activity['activity_id'])}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Noto Sans KR', sans-serif; width: 1600px; background: transparent; }}
.sheet {{ background: #FFF8E7; border-radius: 24px; padding: 32px; }}
.badge {{ display: inline-flex; align-items: center; gap: 8px; background: #F5C842; color: #fff; font-size: 15px; font-weight: 700; padding: 8px 20px; border-radius: 999px; margin-bottom: 20px; }}
.header {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 16px; gap: 24px; }}
.title {{ font-size: 28px; font-weight: 900; color: #333; }}
.meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px; }}
.meta-box {{ background: #fff; border: 2px solid #333; border-radius: 10px; min-height: 54px; padding: 12px; font-size: 14px; color: #444; }}
.prompt {{ font-size: 16px; color: #444; margin-bottom: 16px; line-height: 1.6; }}
.lined-area {{ background: #fff; border: 2px solid #333; border-radius: 12px; min-height: 520px; padding: 20px 24px; background-image: repeating-linear-gradient(transparent, transparent 31px, #D5D0C8 31px, #D5D0C8 32px); background-position: 0 20px; }}
.footer {{ display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; margin-top: 18px; }}
.section-title {{ font-size: 14px; font-weight: 700; color: #555; margin-bottom: 6px; }}
.box {{ background: #fff; border: 2px solid #333; border-radius: 10px; min-height: 110px; padding: 12px; }}
</style>
</head>
<body>
  <div class="sheet">
    <div class="badge">📝 노트 정리 · {esc(level_label(activity['level']))}</div>
    <div class="header">
      <div class="title">배움 노트</div>
      <div style="font-size:14px;color:#666;">{esc(activity['learning_goal'])}</div>
    </div>
    <div class="meta">
      <div class="meta-box">활동 목표: {esc(activity['learning_goal'])}</div>
      <div class="meta-box">출처 쪽: {', '.join(map(str, activity['source_refs']))}</div>
    </div>
    <div class="prompt">{esc(activity['prompt_text'])}</div>
    <div class="lined-area"></div>
    <div class="footer">
      <div>
        <div class="section-title">{esc(summary_label)}</div>
        <div class="box"></div>
      </div>
      <div>
        <div class="section-title">{esc(question_label)}</div>
        <div class="box"></div>
      </div>
    </div>
  </div>
</body>
</html>
"""


def render_see_think_wonder(activity: dict) -> str:
    labels = [zone["label"] for zone in activity["student_writing_zones"]]
    while len(labels) < 3:
        labels.append(["무엇이 보이나요?", "어떤 생각이 드나요?", "무엇이 궁금한가요?"][len(labels)])
    colors = ["purple", "pink", "green"]
    cards = []
    for label, color in zip(labels[:3], colors):
        cards.append(
            f"""<div class="card"><div class="label {color}">{esc(label)}</div><div class="writing"></div></div>"""
        )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{esc(activity['activity_id'])}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Noto Sans KR', sans-serif; width: 1600px; background: transparent; }}
.sheet {{ background: #FFE4E8; border-radius: 24px; padding: 32px; }}
.badge-row {{ display: flex; gap: 10px; margin-bottom: 16px; }}
.badge {{ display: inline-flex; align-items: center; gap: 8px; color: #fff; font-size: 15px; font-weight: 700; padding: 8px 20px; border-radius: 999px; }}
.badge-think {{ background: #FF6B8A; }}
.badge-app {{ background: #4CAF50; }}
.instruction {{ font-size: 16px; color: #444; margin-bottom: 16px; line-height: 1.6; }}
.reference {{ background: #fff; border: 2px solid #333; border-radius: 16px; min-height: 230px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 14px; }}
.grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
.card {{ background: #fff; border: 2px solid #333; border-radius: 12px; overflow: hidden; }}
.label {{ color: #fff; text-align: center; font-size: 16px; font-weight: 700; padding: 10px 16px; }}
.purple {{ background: #C5B3E6; }}
.pink {{ background: #F4A5B8; }}
.green {{ background: #A8E6A3; }}
.writing {{ min-height: 340px; padding: 16px; }}
</style>
</head>
<body>
  <div class="sheet">
    <div class="badge-row">
      <div class="badge badge-think">💡 생각 톡톡 · {esc(level_label(activity['level']))}</div>
      <div class="badge badge-app">📊 Numbers 앱 활동</div>
    </div>
    <div class="instruction">{esc(activity['prompt_text'])}</div>
    <div class="reference">자료 / 이미지 / 영상 썸네일 영역</div>
    <div class="grid">{''.join(cards)}</div>
  </div>
</body>
</html>
"""


def render_worksheet(activity: dict) -> str:
    zones = activity["student_writing_zones"]
    short_labels = [zone["label"] for zone in zones if zone["min_height"] <= 90][:2]
    while len(short_labels) < 2:
        short_labels.append(f"질문 {len(short_labels) + 1}")
    extended_label = next((zone["label"] for zone in zones if zone["min_height"] > 90), "생각 쓰기")
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{esc(activity['activity_id'])}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Noto Sans KR', sans-serif; width: 1600px; background: transparent; }}
.sheet {{ background: #E3F2FD; border-radius: 24px; padding: 32px; }}
.badge {{ display: inline-flex; align-items: center; gap: 8px; background: #42A5F5; color: #fff; font-size: 15px; font-weight: 700; padding: 8px 20px; border-radius: 999px; margin-bottom: 18px; }}
.paper {{ background: #FFFDE7; border: 2px solid #333; border-radius: 16px; overflow: hidden; }}
.paper-header {{ padding: 20px 24px; border-bottom: 2px solid #333; background: linear-gradient(135deg, #FFF9C4, #FFF59D); }}
.paper-title {{ font-size: 20px; font-weight: 900; color: #333; text-align: center; margin: 6px 0; }}
.paper-meta {{ display: flex; justify-content: space-between; font-size: 13px; color: #666; gap: 20px; }}
.questions {{ padding: 20px 24px; display: flex; flex-direction: column; gap: 18px; }}
.question {{ display: flex; flex-direction: column; gap: 8px; }}
.q-text {{ font-size: 14px; color: #333; line-height: 1.6; }}
.answer-line {{ border-bottom: 1.5px solid #333; min-width: 60px; display: inline-block; }}
.answer-box {{ background: #fff; border: 2px solid #333; border-radius: 10px; min-height: 120px; padding: 12px; }}
.short-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
.short-item {{ background: #fff; border: 2px solid #333; border-radius: 10px; min-height: 72px; padding: 12px; }}
</style>
</head>
<body>
  <div class="sheet">
    <div class="badge">📋 활동지 · {esc(level_label(activity['level']))}</div>
    <div class="paper">
      <div class="paper-header">
        <div class="paper-meta">
          <span>출처 쪽: {', '.join(map(str, activity['source_refs']))}</span>
          <span>예상 시간: {activity['estimated_minutes']}분</span>
        </div>
        <div class="paper-title">{esc(activity['learning_goal'])}</div>
      </div>
      <div class="questions">
        <div class="question">
          <div class="q-text">1. {esc(activity['prompt_text'])}</div>
        </div>
        <div class="question">
          <div class="q-text">2. 아래 질문에 답해 봅시다.</div>
          <div class="short-grid">
            <div class="short-item">{esc(short_labels[0])}</div>
            <div class="short-item">{esc(short_labels[1])}</div>
          </div>
        </div>
        <div class="question">
          <div class="q-text">3. {esc(extended_label)}</div>
          <div class="answer-box"></div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""


RENDERERS = {
    "learning_note": render_learning_note,
    "see_think_wonder": render_see_think_wonder,
    "worksheet": render_worksheet,
}


def main() -> int:
    args = parse_args()
    plan_path = Path(args.activity_plan)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plan = load_activity_plan(plan_path)
    rendered = 0

    for activity in plan["activities"]:
        if activity["review_status"] not in args.include_status:
            continue
        renderer = RENDERERS.get(activity["activity_type"])
        if renderer is None:
            continue
        html_text = renderer(activity)
        out_path = output_dir / f"{activity['activity_id']}.html"
        out_path.write_text(html_text, encoding="utf-8")
        print(out_path)
        rendered += 1

    if rendered == 0:
        raise SystemExit("No activities were rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
