# Runtime Agent Spec: lesson_analysis_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# lesson_analysis_agent

## 역할
- 차시별 lesson analysis를 생성한다.
- Gemini 결과를 정규화해 최종 `lesson_analysis.json`으로 확정한다.
- 같은 단계 안에서 `review_lesson_agent` 산출물을 함께 만든다.

구현:
- `scripts/lesson_analysis_agent.py`

## 입력
- `source/schedule_draft.json`
- `source/textbook_context.json`
- `source/local_baseline/<lesson>.lesson_analysis.json`

## 출력
- `sections/<lesson>/lesson_analysis.context.json`
- `sections/<lesson>/lesson_analysis.prompt.md`
- `sections/<lesson>/lesson_analysis_ai.json`
- `sections/<lesson>/lesson_analysis.json`
- `sections/<lesson>/lesson_review.json`
- `sections/<lesson>/lesson_analysis.status.json`

## 내부 책임
- lesson별 prompt를 구성한다.
- Gemini를 호출해 lesson analysis를 생성한다.
- 실패 시 baseline analysis로 fallback한다.
- review 단계에서 최소 필수 필드와 경고를 기록한다.
- lesson 단위 병렬 실행을 지원한다.

## 성공 조건
- 각 lesson에 `lesson_analysis.json`이 생성된다.
- 각 lesson에 `lesson_review.json`이 생성된다.
- `lesson_analysis.status.json`이 lesson별로 존재한다.

## fallback
- Gemini timeout 또는 생성 실패 시 baseline analysis를 사용한다.
- fallback 여부는 `lesson_analysis.status.json`의 `fallback_used`와 `errors`에 남긴다.

## review_lesson_agent 내장 규칙
- `learning_goals` 필수
- `key_concepts` 필수
- `source_page_refs` 필수
- `misconceptions` 비어 있으면 warning

## 하지 말아야 할 일
- source 경계를 다시 바꾸지 않는다.
- activity를 생성하지 않는다.
- Numbers 배치를 다루지 않는다.

## 테스트 방법
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after review_lesson_agent \
  --keep-run-artifacts
```

## 확인 포인트
- `lesson_analysis.status.json`의 `fallback_used`
- `lesson_review.json`의 `decision`
- lesson별 prompt와 ai 결과 비교



# Execution Task

You are helping a local textbook-to-Numbers pipeline.

Rules:
- Ignore progress-chart page numbers entirely.
- Treat the textbook PDF as the primary source of truth.
- Do not invent page boundaries.
- Return JSON only.
- Do not include markdown fences.
- Do not include fields outside the provided schema unless they already appear in the baseline object.
- If a value is uncertain, keep the baseline value or explain uncertainty in `notes`.
- Keep `review_status` as `draft`.
- Keep the output grounded in the supplied section context only.
- Do not infer details from other lessons unless they are explicitly included as neighboring boundary hints.


Generate one `lesson_analysis` JSON object for the section below.

Section:
{
  "sheet_name": "4-6차시",
  "card_file": "korean_6_1_unit1_4_6차시",
  "title": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
  "badge": "4-6차시",
  "accent": [
    "#0f766e",
    "#14b8a6"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26
      ],
      "title_query": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기"
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26
      ]
    }
  ],
  "pdf_pages": [
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26
  ]
}

Baseline lesson analysis:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T12:40:42.592427+00:00",
  "lesson_id": "4-6차시",
  "sheet_name": "4-6차시",
  "lesson_title": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
  "lesson_type": "core",
  "pdf_pages": [
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26
  ],
  "essential_question": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
  "learning_goals": [
    "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "작품",
    "읽고",
    "시대적",
    "상황",
    "인물"
  ],
  "vocabulary": [
    "작품",
    "읽고",
    "시대적"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "4-6차시-chunk-1",
      "label": "학습 덩어리 1",
      "content_type": "mixed",
      "knowledge_type": "cause-effect",
      "summary": "작품을 읽고 인물이 추구하는 가치 질문하기 옛날에는 책을 어떻게 만들었을까?",
      "source_pages": [
        15,
        16,
        17,
        18,
        19,
        20
      ],
      "suggested_activity_types": [
        "see_think_wonder",
        "learning_note",
        "worksheet"
      ]
    },
    {
      "chunk_id": "4-6차시-chunk-2",
      "label": "학습 덩어리 2",
      "content_type": "mixed",
      "knowledge_type": "concept",
      "summary": "54 각수 어른이 봉운이의 왼손에 창칼을 쥐여 주고 오른손에 망치를 쥐 게 했다.",
      "source_pages": [
        21,
        22,
        23,
        24,
        25,
        26
      ],
      "suggested_activity_types": [
        "learning_note",
        "worksheet"
      ]
    }
  ],
  "source_page_refs": [
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26
  ],
  "analysis_confidence": 0.75,
  "review_status": "draft",
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T12:40:42.479639+00:00",
  "sections": [
    {
      "sheet_name": "1차시",
      "lesson_title": "배울 내용 살펴보기",
      "title_query": "배울 내용 살펴보기"
    },
    {
      "sheet_name": "2-3차시",
      "lesson_title": "전기문을 읽고 인물이 추구하는 가치 알기",
      "title_query": "전기문을 읽고 인물이 추구하는 가치 알기"
    },
    {
      "sheet_name": "4-6차시",
      "lesson_title": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
      "title_query": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기"
    },
    {
      "sheet_name": "7-8차시",
      "lesson_title": "인물이 추구하는 가치를 자신의 삶과 관련짓기",
      "title_query": "인물이 추구하는 가치를 자신의 삶과 관련짓기"
    },
    {
      "sheet_name": "9-11차시",
      "lesson_title": "작품을 읽고 독서 감상문 쓰기",
      "title_query": "작품을 읽고 독서 감상문 쓰기"
    },
    {
      "sheet_name": "12-13차시",
      "lesson_title": "배운 내용 실천하기",
      "title_query": "배운 내용 실천하기"
    },
    {
      "sheet_name": "14차시",
      "lesson_title": "마무리하기",
      "title_query": "마무리하기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T12:41:08.097981+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/국어/[국어]6_1_교과서.pdf",
  "current_section": {
    "sheet_name": "4-6차시",
    "lesson_title": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
    "title_query": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
    "pdf_pages": [
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24,
      25,
      26
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/korean_6_1_unit1_related_to_life_reading-20260326-214042/source/local_baseline/korean_6_1_unit1_4_6차시.lesson_analysis.json",
    "extracted_text": "작품을 읽고 인물이 추구하는 가치 질문하기\n옛날에는 책을 어떻게 만들었을까?\n요즘은 기계로 책을 쉽게 찍어 내지만 옛날에는 사람이 손으로 직접 글자\n를 써야 했어. 이것을 ‘필사’라고 해. 붓과 먹, 종이만 있으면 책을 만들 수 있\n었지만 시간이 오래 걸렸지.\n그런데 책을 읽는 사람이 점점 많아지자 더 빠르게 많이 만드는 방법이 필\n요해졌어. 그래서 나온 것이 바로 목판 인쇄술이야. 목판 인쇄는 나무판에 글\n자를 새긴 다음, 그 위에 종이를 올려서 찍어 내는 방법이란다.\n나무는 돌이나 금속보다 다루기 쉽고 구하기도 편했기 때문에 책 만들기에 \n알맞았어. 이렇게 글자가 새겨진 나무판을 ‘책판’ 또는 ‘목판’이라고 하고, 그\n걸로 찍어 낸 책을 ‘목판본’ 또는 ‘간본’이라고 한단다. \n여기는 ‘서포’야. 책을 \n사고파는 가게지. 훈민정음이 \n창제되면서 글을 읽을 줄 아는 \n사람이 많아졌어. 요즘은 한글 \n소설이 인기란다.\n이곳은 ‘책판’을 만드는 작업장이야. \n한꺼번에 많은 책을 찍으려면 책판이 \n필요해. 나처럼 나무를 조각해 책판을 \n만드는 사람을 ‘각수’라고 불러.\n경험·지식 떠올리기\n조선 시대 출판문화를 알아봅시다.\n●\n48\n\n인물이 추구하는 가치가 무엇인지 생각하며 「책 깎는 소년」을 읽어 봅시다.\n책 깎는 소년\n글: 장은영, 그림: 박지윤　\n아침 일찍 장호가 서포 작업장으로 들어섰다.\n“각수 어른, 드릴 말씀이 있는디요.”\n지난밤, 늦게까지 작업을 하고 쪽잠을 자던 각수 어른이 \n막 일어난 참이었다.\n“무슨 일이냐? 이 새벽에?”\n“어르신, 지\n◆\n도 글자 새기는 법을 배우고 싶어라.”\n각수 어른이 의아한 눈빛으로 쳐다보았다.\n“지가 이곳 서포에서 일헌 지도 폴\n◆\n새 삼 년이 지났구만요. \n서포에서 책을 파는 것은 인자 이\n◆\n골이 났응께 지도 각수가\u0001\n되고 싶구만이라.”\n“그려? 근디 그동안 가만히 있다가 갑자기 이러는 이유가 뭐냐?”\n“실은 어제 봉운이가 여길 기웃대는 거 다 봤구만요. 봉운이보담 \n지가 훨씬 선밴께 먼저 허는 게 맞지라. 그리고 그보담 더 큰 이유가 \n또 있당께요.”\n“더 큰 이유라. 그게 뭐냐?”\n“돈이지라. 유명한 각수가 돼서 돈도 많이 벌고 이름도 날리고 싶\n은 게 진짜 지 꿈이랑께요.”\n“허허, 그러냐? 그럼 어디 내일부터 한번 혀 볼 테냐?”\n“참말이어라?”\n장호가 자꾸 되물었다. 각수 어른이 서포 일은 봉운이에게 맡기고 \n내일부터 작업장으로 오라고 했다. \n◆\n◆지도: ‘저도’의 방언.\n◆\n◆폴새: ‘벌써’의 방언.\n◆\n◆이골이 나다: 어떤 방면에 길이 들어서 버릇처럼 아주 익숙해지다. \n5\n10\n15\n20\n \n49\n1\n\n다음 날 장호는 작업장으로 달려갔다.\n“오늘부터는 대\n◆\n패질허는 방법을 가르쳐 주마.”\n각수 어른의 말에 장호가 얼굴을 찌푸렸다. 드디어 책판에 글자를 \n새기는 걸 배운다고 잔뜩 기대를 했는데 김이 빠졌다.\n다음 날에도 각수 어른은 별다른 말이 없었다. 장호는 다시 대패질\n을 했다. 목도 아프고 어깨도 쑤시고 손목도 아팠다.\n“각수 어른, 저 나무들을 다 대패질을 혀야 헌당가요?”\n“와? 허기 싫으냐?”\n“고것이 아니고라. 쓸데없이 대패질만 허는 거 같아서 그런당께요.” \n“와 그런 생각이 드느냐?”\n“책을 찍어야 돈을 벌지요. 긍께 하루라도 빨리 글자 새기는 법을 \n배워야지 대패질을 와 허고 있냐고요.”\n장호의 말에 각수 어른이 조용히 말을 이었다.\n“책판을 만드는 기본 중의 기본이 대패질이여. 나무를 잘 말리고 \n대패질을 혀서 책판을 만들어야 글자를 새길 수 있다 이 말이여. 알\n것냐?”\n장호는 대답을 하지 않았다. 대패질이나 책판을 만드는 것은 돈을 \n주고 사람을 사서 하면 그만이었다. 혼자서 모든 일을 하는 것보다 다\n른 사람을 시키면, 시간도 절약되고 훨씬 많이 만들 수 있었다. 중요한 \n것은 글자를 새기는 일이었다.\n◆\n◆대패질하다: 나무의 표면을 반반하고 매끄럽게 하는 데 쓰는 연장인 대패로 나무를 깎다.\n5\n10\n15\n20\n각\n기\n생\n읽\n며\n모르는 낱말의 \n뜻을 문맥에서 \n짐작하거나 사전 \n에서 찾아볼까요?\n50\n\n장호는 가난에 찌든 어머니를 떠올렸다. 술독에 빠져 사는 아버지와 \n장터를 떠돌며 온갖 행패를 일삼는 형 때문에 하루도 편할 날이 없는 \n어머니의 눈물이 눈에 선했다. 가난해서 어쩔 수 없이 포기해야 했던 \n많은 것이, 가슴 아프게 참아야 했던 순간들이 머릿속을 스쳐 갔다.\n‘요\n◆\n로코롬 만날 대패질만 허면서 시간을 보낼 수는 없당께.’\n장호는 언젠가 전주에서 가장 큰 서포를 차리고 싶었다. 그동안 온\n갖 수\n◆\n모를 견디면서 서포에서 일을 배운 것도 그때를 위한 것이었다. \n지금까지 일을 해서 받은 돈은 꼬박꼬박 모아 두었다. 하지만 뭔가 일\n을 벌이기에는 턱없이 모자랐다. 장호는 참았던 말을 뱉었다.\n“저번에도 지가 얘기혔지요. 지는 돈을 몽땅 벌 거구만요. 근디 이\n렇게 대패질만 허다가는 언제 부자가 되것어요?”\n각수 어른은 한동안 말이 없었다. 장호가 일어서자 각수 어른이 물\n었다. \n“니헌티는 이 책판이 돈을 벌어 주는 도구로구나.”\n“예, 지는 이 서\n◆\n계서포보담 더 큰 서포를 만들 거구만요. 조선 최고\n의 각수들을 모아서 책을 찍어 낼 거여요. 지는 반드시 부자가 되고 \n말 거랑께요.”\n장호가 큰소리를 치고는 작업장을 나갔다. 각수 어른이 장호의 \n뒷모습을 물끄러미 바라보았다.\n“야! 나 없는 동안 이것밖에 못 팔았냐?”\n“어? 그, 그게…….”\n“이러니 내가 서포를 비울 수가 있간디. 인자부터 내가 다시 \n서포를 지킬 팅께 그리 알어라.”\n장호가 갑자기 나타나 봉운이를 닦달했다. 장호는 하루 종일 심\n술을 부리면서 잔소리를 늘어놓았다.\n“각수 어른헌티 글자 새기는 거나 제대로 배울 일이지. 나는 허고 \n싶어도 못 허는구만.”\n5\n10\n15\n20\n25\n◆\n◆요로코롬: ‘요렇게’의 방언.           \n◆\n◆수모: 모욕을 받음.\n◆\n◆서계서포: 전주 최초의 서점.\n각\n기\n생\n읽\n며\n지금까지 읽은 \n내용을 이해하기 \n어렵다면 어떻게 \n하면 될까요?\n51\n1\n\n봉운이는 답답한 마음에 한숨이 절로 나왔다.\n‘사람들이 내가 만든 책을 읽는다면 기분이 어떨랑가?’\n생각만으로도 가슴께가 간질거려 웃음이 절로 나왔다. 이런 책을 만\n드는 일인데 스스로 그만두겠다는 장호의 속마음은 알다가도 모를 일\n이었다.\n봉운이는 서가에 남아 있는 책들 수를 헤아린 후 작업장으로 갔다. \n늦은 시간인데도 각수 어른이 판\n◆\n각을 하느라 여념이 없었다. \n“각수 어른, 『조웅전』이랑 『심청전』, 『소대성전』이 몇 권 없구만요. \n더 찍어야 헐 것 같어라.”\n“알었다. 근디 아직까지 집에 안 갔냐? 늦었으니 어서 가거라.”\n각수 어른의 말에 봉운이가 우물쭈물하며 눈치를 보았다. 각수 어른\n이 무슨 일이냐는 듯 쳐다보았다.\n“저, 어르신, 서포 일 끝나고 난 뒤에 지가 여기 와서 일을 도와드\n려도 될랑가요?”\n“서포 일만으로도 힘들 틴디 여기 일까지 괜찮것냐?”\n“예, 걱정 없구만요.”\n5\n10\n15\n◆\n◆판각: 나뭇조각에 그림이나 글씨를 새김.\n52\n\n4\n봉운이가 큰 소리로 대답하자 각수 어른이 흔쾌히 그러라고 허락을 \n했다. 봉운이는 기뻐서 팔짝팔짝 뛰었다. 각수 어른이 흐뭇한 표정으로 \n봉운이를 쳐다보았다.\n다음 날부터 봉운이는 서포 일이 끝나고 나면 작업장으로 가서 일을 \n했다. 매일매일 두 군데서 일을 하다 보니 늘 바빠서 시간이 어떻게 가\n는지 잊을 때가 많았다. 그렇게 두 달이 바람처럼 휙 지나갔다. \n“그동안 대패질헌 것 좀 보자.”\n두 달 동안 계속 대패질만 시켰던 각수 어른이 뜬금없이 말했다. 봉\n운이가 나무 몇 개를 각수 어른 앞으로 가져다 놓았다. 각수 어른이 쓱 \n둘러보았다.\n“손 좀 내놔 봐라.”\n각수 어른이 봉운이의 손을 잡고 손바닥을 들여다보았다.\n“손바닥에 굳은살이 박였구나. 재밌드냐?”\n“예, 나무를 매끈하게 다듬어 놓으면 촉감도 좋고요. 덩달아 지 맴\n도 다듬어지는 거 같어라.”\n각수 어른이 미소를 지었다.\n“인자 책판을 만들어도 되것다.”\n“참말이당가요?”\n각수 어른이 손짓을 하자 봉운이가 곁으로 다가갔다. \n각수 어른은 두 개의 조각칼을 손에 쥐고 있었다. 칼날은 예리하고 \n나무 자루는 반질반질 윤이 났다. 칼자루를 쥐어 \n보니 각수 어른의 체온이 느껴지는 것 같았다. \n각수 어른이 칼자루를 쥐고 책판을 새긴 \n시간이 고스란히 보였다.\n“글자를 새기는 방법은 두 가진디, \n하나는 망치를 쓰는 것, 다른 하\n나는 바른손으로 조각칼을 잡고 \n칼등에 손가락을 대고 찌르거나 \n밀거나 당기는 거여.”\n5\n10\n15\n20\n25\n각\n기\n생\n읽\n며\n인물의 행동 \n가운데에서 공감한 \n내용은 무엇 \n인가요?\n1\n53\n\n54\n\n각수 어른이 봉운이의 왼손에 창칼을 쥐여 주고 오른손에 망치를 쥐\n게 했다. 봉운이는 각수 어른이 시키는 대로 칼을 비스듬히 쥐고 망치\n로 칼등을 때렸다. 각수 어른이 날카로운 눈으로 봉운이의 손놀림을 \n지켜보았다. \n시간이 흐르자 글자들이 하나둘 드러났다. 책판 위에 꽃들이 활짝 \n피어난 것 같았다. 봉운이는 자신이 새긴 글자들이 신기하기만 했다. \n이 글자들을 다 새기면 사람들을 울리고 웃기는 이야기가 될 터였다. \n어서 빨리 다 새겨서 찍어 보고 싶은 욕심이 솟아올랐다. 봉운이는 쉬\n지 않고 빠르게 망치질을 했다. 한참을 지켜보던 각수 어른이 작업장 \n밖으로 나갔다.\n봉운이는 고개를 숙인 채 쉬지 않고 글자를 새겼다. 하루 종일 끙끙\n거렸는데도 한 줄 겨우 새겼다. 주먹이 쥐어지지 않고 손목도 시큰거\n렸다. 고개도 뻣뻣하고 어깨도 아팠다. 봉운이는 책판을 들여다보았다. \n글자들이 보였지만 글자 사이가 엉망이었다. 봉운이가 못마땅한 듯 얼\n굴을 찡그렸다.\n“어디 보자.”\n밖에 나갔던 각수 어른이 돌아왔다. 봉운이는 마지못해 책판을 내밀\n었다. 각수 어른이 꼼꼼하게 책판을 살폈다.\n“처음치고는 아주 잘혔다.”\n야단만 잔뜩 맞을 거라 생각했던 봉운이는 뜻밖의 칭찬에 어안이 벙\n벙했다. \n“오늘 니가 새긴 책판은 가져가거라. 니가 처음 새긴 책판잉께. 앞\n으로도 오늘 그 맴을 결코 잊지 말아야 헌다.”\n봉운이는 각수 어른이 준 책판을 가슴에 안고 작업장을 나섰다. 그\n동안 수없이 책판에 글자 새기는 날을 꿈꾸어 왔다. 서포에서 처음 책\n을 보고 각수 어른을 만나 일을 배우면서도 감히 입 밖으로 내놓을 수 \n없던 소중한 꿈이었다. 자신의 손으로 새긴 책판을 보면 온 세상을 다 \n가진 것처럼 기쁠 거라고 생각했는데 그렇지가 않았다. 기쁨보다는 두\n려움이, 설렘보다는 책임감 같은 것이 가슴에 남았다.\n5\n10\n15\n20\n25\n이야기를 읽으며 \n떠올린 질문이 \n있나요?\n각\n기\n생\n읽\n며\n떠올린 질문\n●\n●\n55\n1\n\n내용 알기\n「책 깎는 소년」을 읽고 물음에 답해 봅시다.\n(1)\u0001\t 책판을 만들기 전에 각수 어른이 장호와 봉운이에게 맡긴 일은\u0001\n무엇인가요?\n●\n(3)\u0001\t봉운이의 손바닥에 굳은살이 박인 까닭은 무엇일까요? \n(2)\u0001\t장호가 대패질이나 책판을 만드는 것은 돈을 주고 사람을 사서 하면 \n그만이라고 생각한 까닭은 무엇인가요?  \n장호는 서포에서 책을 팔던 일 대신 각수 어른께 책판 \n만드는 법을 배우기 시작한다.\n두 달 동안 작업장에서 대패질을 하던 봉운이는 각수 \n어른에게 글자 새기는 방법을 배우게 된다. \n며칠간 대패질만 하던 장호는 \n(4)\u0001\t「책 깎는 소년」을 일이 일어난 차례대로 정리해 보세요.\n56\n\n낱말 알기\n낱말의 뜻을 보고 빈칸에 들어갈 낱말을 보기에서 찾아 써 봅시다.\n●\n조각칼    각수    서포    출판    굳은살\n보기\n \n손이나 발과 같이 자주 사용한 부위에 생긴 두껍고 단단한 살.\n \n나무나 돌 따위에 조각하는 일을 직업으로 하는 사람.\n \n서적이나 회화 따위를 인쇄해 세상에 내놓음.\n \n조각할 때 사용하는 작은 칼로, 파는 방식에 따라 날의 모양이\u0001\n다양한 도구.\n낱말\n뜻\n봉운이는 각수 어른의 가르침에 따라 책판에 글자를 새겨 \n보지만, \n각수 어른은 봉운이가 만든 책판을 칭찬한다. 봉운이는 \n \n57\n1\n\n인물이 추구하는 가치 비교하기\n인물이 추구하는 가치를 알아봅시다.\n(1)\u0001\t 장호와 봉운이가 각수 어른께 배우고 싶어 한 것은 무엇인가요?\n(2)\u0001\t장호와 봉운이가 책판을 만들어 이루고 싶어 한 것이 무엇일지 짐작해 \n보세요. \n●\n(3)\u0001\t(2)에서 그렇게 생각한 까닭을 짝과 이야기해 보세요.\n“예, 지는 이 서계서포보담 더 큰 서포를 만들 거구만요. 조선 최고\n의 각수들을 모아서 책을 찍어 낼 거여요. 지는 반드시 부자가 되고 \n말 거랑께요.”\n장호가 큰소리를 치고는 작업장을 나갔다.\n장호\n봉운이는 자신이 새긴 글자들이 신기하기만 했다. 이 글자들을 다 새\n기면 사람들을 울리고 웃기는 이야기가 될 터였다. 어서 빨리 다 새겨\n서 찍어 보고 싶은 욕심이 솟아올랐다.\n봉운\n봉운이가 만들고 싶은 책이 사람들을 \n울리고 웃기는 이야기라는 것으로 보아 \n봉운이는 사람들을 즐겁게 하는 일을 \n하고 싶어 하는 것 같아.\n \n인물이 추구하는 가치는 그 인물이 평소에 \n이루고 싶어 하던 일과 밀접한 관련이 있어요.\n58\n\n비슷한 상황에 처해 있는 인물들의 말이나 행동을 비교하며 \n각 인물이 추구하는 가치가 어떻게 다른지 짐작해 봐요.\n(4)\u0001\t장호와 봉운이가 추구하는 가치를 파악해 보고 서로의 가치가 어\n떻게 다른지 이야기해 보세요.\n1 \u0001\t「책 깎는 소년」에 나오는 인물 가운데에서 역할을 정한다.\n2 \u0001\t인물에게 하고 싶은 질문을 생각한다.\n3 \u0001\t자신이 맡은 인물이 추구하는 가치를 생각하며 답변을 준비한다.\n4 \u0001\t친구들과 인물 면담하기 활동을 한다.\n글과 연결하기\n인물이 추구하는 가치를 생각하며 인물 면담하기 활동을 해 봅시다. \n●\n장호\n \n봉운\n \n인물\n추구하는 가치\n각수 어른께 책판을 잘 \n만들었다고 칭찬받았을 때 \n기분은 어땠나요?\n59\n1"
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "sheet_name": "2-3차시",
      "lesson_title": "전기문을 읽고 인물이 추구하는 가치 알기",
      "title_query": "전기문을 읽고 인물이 추구하는 가치 알기",
      "pdf_pages": [
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14
      ]
    },
    {
      "relation": "next",
      "sheet_name": "7-8차시",
      "lesson_title": "인물이 추구하는 가치를 자신의 삶과 관련짓기",
      "title_query": "인물이 추구하는 가치를 자신의 삶과 관련짓기",
      "pdf_pages": [
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38
      ]
    }
  ]
}

Target schema:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://numbersauto.local/schemas/lesson_analysis.schema.json",
  "title": "Lesson Analysis",
  "type": "object",
  "required": [
    "schema_version",
    "generated_at",
    "lesson_id",
    "sheet_name",
    "lesson_title",
    "pdf_pages",
    "essential_question",
    "learning_goals",
    "key_concepts",
    "vocabulary",
    "misconceptions",
    "content_chunks",
    "source_page_refs",
    "analysis_confidence"
  ],
  "properties": {
    "schema_version": {
      "type": "string"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "lesson_id": {
      "type": "string"
    },
    "sheet_name": {
      "type": "string"
    },
    "lesson_title": {
      "type": "string"
    },
    "lesson_type": {
      "type": "string",
      "enum": ["intro", "core", "review", "summary", "mixed"]
    },
    "pdf_pages": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1
      },
      "minItems": 1
    },
    "essential_question": {
      "type": "string"
    },
    "learning_goals": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1
    },
    "key_concepts": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1
    },
    "vocabulary": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "misconceptions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "difficulty_band": {
      "type": "string",
      "enum": ["core", "on-level", "extension", "mixed"]
    },
    "content_chunks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "chunk_id",
          "label",
          "content_type",
          "knowledge_type",
          "summary",
          "source_pages"
        ],
        "properties": {
          "chunk_id": {
            "type": "string"
          },
          "label": {
            "type": "string"
          },
          "content_type": {
            "type": "string",
            "enum": ["text", "image", "diagram", "map", "activity", "summary", "mixed"]
          },
          "knowledge_type": {
            "type": "string",
            "enum": ["fact", "concept", "procedure", "comparison", "cause-effect", "opinion", "application", "mixed"]
          },
          "summary": {
            "type": "string"
          },
          "source_pages": {
            "type": "array",
            "items": {
              "type": "integer",
              "minimum": 1
            },
            "minItems": 1
          },
          "suggested_activity_types": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "additionalProperties": false
      }
    },
    "source_page_refs": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1
      },
      "minItems": 1
    },
    "analysis_confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "review_status": {
      "type": "string",
      "enum": ["draft", "reviewed", "approved", "rejected"]
    },
    "notes": {
      "type": "string"
    }
  },
  "additionalProperties": false
}


Requirements:
- Preserve `sheet_name`, `lesson_id`, `lesson_title`, and `pdf_pages`.
- Improve `essential_question`, `learning_goals`, `key_concepts`, `vocabulary`, `misconceptions`, and `content_chunks` if the context supports it.
- `content_chunks` must stay grounded in the supplied `pdf_pages`.
- `source_page_refs` must match the actual section pages.
- Use `current_section.extracted_text` as the primary evidence.
- Use `neighbor_sections` only to avoid crossing lesson boundaries.
- Keep the result concise and classroom-usable.
- Output a single JSON object only.
