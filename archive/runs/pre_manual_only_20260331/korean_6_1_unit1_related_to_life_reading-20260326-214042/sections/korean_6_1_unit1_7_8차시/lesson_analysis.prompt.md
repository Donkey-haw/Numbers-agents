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
  "sheet_name": "7-8차시",
  "card_file": "korean_6_1_unit1_7_8차시",
  "title": "인물이 추구하는 가치를 자신의 삶과 관련짓기",
  "badge": "7-8차시",
  "accent": [
    "#134e4a",
    "#0d9488"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
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
      ],
      "title_query": "인물이 추구하는 가치를 자신의 삶과 관련짓기"
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
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
  ],
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

Baseline lesson analysis:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T12:40:42.649778+00:00",
  "lesson_id": "7-8차시",
  "sheet_name": "7-8차시",
  "lesson_title": "인물이 추구하는 가치를 자신의 삶과 관련짓기",
  "lesson_type": "core",
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
  ],
  "essential_question": "인물이 추구하는 가치를 자신의 삶과 관련짓기",
  "learning_goals": [
    "인물이 추구하는 가치를 자신의 삶과 관련짓기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "인물",
    "추구하",
    "가치",
    "자신",
    "삶과"
  ],
  "vocabulary": [
    "인물",
    "추구하",
    "가치"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "7-8차시-chunk-1",
      "label": "학습 덩어리 1",
      "content_type": "mixed",
      "knowledge_type": "cause-effect",
      "summary": "10 주말이 멀었는데 언니가 집에 왔다.",
      "source_pages": [
        27,
        28,
        29,
        30,
        31,
        32
      ],
      "suggested_activity_types": [
        "see_think_wonder",
        "learning_note",
        "worksheet"
      ]
    },
    {
      "chunk_id": "7-8차시-chunk-2",
      "label": "학습 덩어리 2",
      "content_type": "mixed",
      "knowledge_type": "concept",
      "summary": "5 10 “나루야, 넌 나랑 달라.",
      "source_pages": [
        33,
        34,
        35,
        36,
        37,
        38
      ],
      "suggested_activity_types": [
        "learning_note",
        "worksheet"
      ]
    }
  ],
  "source_page_refs": [
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
  "generated_at": "2026-03-26T12:41:09.967930+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/국어/[국어]6_1_교과서.pdf",
  "current_section": {
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
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/korean_6_1_unit1_related_to_life_reading-20260326-214042/source/local_baseline/korean_6_1_unit1_7_8차시.lesson_analysis.json",
    "extracted_text": "10\n주말이 멀었는데 언니가 집에 왔다. 아무래도 엄마가 호출한 모양이\n라고 나루는 생각했다.\n“나루야, 나가자.”\n버들이가 나루를 데리고 밖으로 나갔다. 오후 여섯 시가 넘었는데도 \n날이 밝았다. 두 사람은 아파트 자전거 보관대에서 자전거를 찾았다. \n버들이와 나루의 자전거 모두 안장에 뽀얗게 먼지가 쌓여 있었다. 나루\n는 바퀴를 손가락으로 꾹꾹 눌러 보았다. 바퀴는 탄력을 잃고 축 처져 \n있었다. 버들이가 경비실에서 공기 펌프를 빌려 왔다.\n15\n \n인물이 처한 상황을 생각하며 「다이빙대 위에서」를 읽어 봅시다.\n1.\n다이빙대 위에서\n글: 은소홀, 그림: 노인경　 \n인물이 추구하는 가치를 자신의 삶과 관련짓기\n인물이 추구하는 가치를 자신과 관련지으며 \n독서 감상문 쓰기\n2\n5\n앞 \n이야기\n나루와 버들이는 자매이다. 나루는 언니 버들이와 함께 어려서부터 수영을 \n했다. 둘은 큰 시합에서 나란히 메달을 따기도 했다. 이후 버들이는 체육 중학\n교에 진학했고, 6학년이 된 나루는 한강초 수영부 대표 선수가 되었다. 그런\n데 지난겨울, 버들이가 갑자기 수영을 그만두고 다이빙을 하겠다고 선언했다. \n나루는 버들이가 더 이상 수영을 하지 않는다는 사실을 받아들이기 어려웠고, \n버들이에게 그 이유도 묻지 못했다. 그러던 중 1등만 하던 나루가 요즘 라이\n벌 김초희에게 자꾸 시합에서 진다. 자신보다 빠른 김초희 때문에 힘들어하는 \n나루에게 엄마는 수영을 그만두어도 괜찮다고 말했지만, 나루의 마음은 복잡\n하기만 하다. \n60\n\n자전거 바퀴에 바람을 과하게 채우면 작은 돌멩이에도 통통 튀어 쓸\n데없이 핸들을 꽉 잡아야 한다. 그렇다고 바람을 부족하게 채우면 바\n퀴가 땅바닥을 제대로 밀어 주지 못해 속도가 나지 않는다. 그럴 때에\n는 작은 언덕조차 힘이 든다. 무엇이든지 ‘적당히’가 중요하다. 하지만 \n그 적당히라는 것이 언제나 제일 어렵다. 얼마큼의 바람이 적당한 것\n인지 알려면 자기 손으로 직접 바람을 넣고 달려 보기를 여러 번 해 \n보는 수밖에 없다. 감각은 대체로 그렇게 몸에 익는다. \n5\n10\n“오랜만에 태워 줄까?”\n버들이가 자전거 짐받이를 두드리며 말했다. 예전에는 거기가 나루 \n자리였다. 엉덩이가 아프다는 나루의 말에 버들이가 짐받이 위로 도톰\n한 택배 상자를 겹쳐서 만든 쿠션이 아직도 달려 있었다. 키가 부쩍 크\n고 나서부터는 나루도 자전거를 갖게 되었다. 나루는 버들이가 중학교\n에 가기 전까지 늘 자전거를 타고 언니의 뒤를 따라 학교에 다녔다.\n61\n1\n\n“괜찮아. 내가 뭐 애야?”\n“아프면 다 애야.”\n버들이가 앞장서 달렸다. 제일 먼저 향한 곳은 한강초등학교였다. 두 \n사람 다 가장 자신 있게 갈 수 있는 길이다. 학교 운동장에는 아이들 \n몇몇이 나와 축구를 하고 있었다. 운동장을 크게 돌아 체육관 앞에서 \n잠시 멈추었다. 수영장에는 불이 꺼져 있다.\n“나루야, 너 무슨 일 있어?” \n나루는 아무 말도 할 수가 없었다. 무슨 대답이든 거짓말이 될 것이\n다. 나루가 아무 말이 없자 버들이는 다시 땅에서 발을 뗐다. 나루도 \n따라 페달을 굴렸다. 속도를 내자 머리카락 사이로 시원한 바람이 지\n나갔다. 나루는 앞에 가는 언니의 반듯한 등을 보았다. 버들이는 걸을 \n5\n10\n각\n기\n생\n읽\n며\n인물은 어떤 \n상황에 놓여 있고, \n어떤 감정을 느끼고 \n있을까요?\n62\n\n때에도 자전거를 탈 때에도 등이 구부정하지 않고 곧았다. 언니처럼 \n해 보려고 자전거를 탈 때마다 허리에 힘을 줘 보았지만 그렇게 하면 \n영 속도가 나지 않아 그만두곤 했다.\n집 앞 공원을 가로질렀다. 공원 한편에서는 아이들이 분수대에서 한\n껏 물놀이를 즐기고 있었다. 버들이와 나루의 자전거가 잠시 멈춘 물\n줄기 사이를 지났다. 굴러가는 바퀴를 따라 물 자국이 생겼다.\n버들이는 공원을 한 바퀴 크게 돌아 광장에 자전거를 세웠다.\n“언니, 뭐 하나 물어봐도 돼?”\n버들이가 나루 옆에 다리를 쭉 펴고 앉아 고개를 끄덕였다.\n“왜 수영 그만뒀어?”\n나루는 드디어 용기를 내어 물었다. 오랜 시간 묵혀 둔 덕분에 섭섭\n함이 많이 바랬다.\n“빨리도 물어본다.” \n버들이의 핀잔에 나루가 멋쩍게 웃었다.\n“다이빙하려고 그만뒀지, 뭐.”\n버들이는 대수롭지 않다는 듯이 대답을 던졌다. 나루는 그런 언니를 \n보니 뱃속 깊은 곳에서 열이 나기 시작했다. 이제는 어떤 이야기를 들\n어도 괜찮을 거라 생각했는데 아직 아니었나 보다. 나루는 다시 꾹 참\n고 물었다.\n“그럼 수영은? 수영은 이제 안 해?”\n버들이가 말이 없어졌다. 저 멀리 분수대에서 아이들 웃음소리가 들\n려왔다.\n“수영은…… 그만해도 될 것 같았어. 아니, 그만하고 싶더라.”\n‘아니야, 그건 아니지. 언니도 엄마도 그만둔다는 말을 어떻게 그렇\n게 쉽게 할 수 있어?’ \n결국 나루는 누르고 있던 화를 내고 말았다.\n“그만하고 싶다고 그만둘 거였으면 진작 그러지. 7년 넘게 잘해 놓\n고 기록 좀 안 나온다고 바로 포기하는 게 어디 있어? 다이빙은? 다\n이빙도 힘들면 또 그만두겠네!”\n5\n10\n15\n20\n25\n각\n기\n생\n읽\n며\n인물이 그렇게 \n말하거나 행동한 \n까닭은 무엇 \n일까요?\n63\n1\n\n5\n10\n15\n버들이는 갑작스레 화를 내는 나루를 보고 눈이 동그래졌다. 그러다 \n이내 팔짱을 끼고 나루를 향해 고쳐 앉았다.\n“야! 너 지금 덤비는 거야? 나 강버들이야. 강나루 언니, 강버들.”\n하지만 나루는 기다렸다는 듯이 더 쏟아부었다.\n“그래, 덤빈다! 그래서, 뭐! 어쩔 건데! 내가 틀린 말 했어? 언니는 \n수영한 시간이 아깝지도 않아? 난 수영 그만두면 하늘이 무너져 버\n릴 것 같은데 언니는 어떻게 그래?” \n나루는 얼굴이 발개져서는 화를 내는 건지 우는 건지 알 수 없는 소\n리를 냈다. 버들이가 고개를 비스듬히 한 채로 나루를 빤히 보았다. 그\n러다 팔을 풀고 바닥에 드러누워 버렸다.\n“그래, 화내라, 화내. 다른 사람은 몰라도 넌 화낼 수 있지. 넌 내가 \n아는 사람들 중에 제일 열심히 하는 애니까.”\n실컷 화낸 사람 무안하게 버들이는 도리어 칭찬을 했다. 나루는 아\n무 말도 않고 콧구멍에서 바람만 씩씩 뿜었다.\n“근데 나루야, 수영 그만둬도 하늘 안 무너져. 하늘 무너질까 봐 수\n영하는 거면 알아 두라고.”\n“난 심각한데 언니는 지금 장난해?” \n64\n\n5\n10\n“나도 심각하게 얘기하는 거야.”\n나루는 무릎 사이로 고개를 파묻어 버렸다. 언니에게 이 눈물을 들\n키고 싶지 않았다.\n“있잖아, 나루야. 나는 진짜 옛날에는 내가 국가대표 할 줄 알았다. \n근데 중학교 가니까 이게 아닌데 싶더라고. 너도 알지? 나 평영 못\n하는 거. 배울 때 엄청 고생했는데. 지금도 느려. 근데 그런 애들 있\n잖아. 똑같이 배웠는데 훨씬 빨리 몸에 붙는 애들. 체\n◆\n중에는 그런 애\n들만 모여 있어. 걔네들이 게으르기라도 하면 어떻게 좀 해 보겠는\n데 또 죽어라 연습한다? 그럼 난 당할 재간이 없더라고.”\n나루는 자신을 앞질러 가던 김초희의 모습이 떠올랐다. 라이벌이라\n는 건 항상 그렇게 준비할 새도 없이 나타난다. 김초희도 그랬다. 영원\n히 나루의 것일 것만 같았던 메달을 한 번, 두 번 빼앗아 가더니 언제\n부턴가 꽉 잡고 돌려주지 않았다. 그게 너무 화가 났다.\n“나는 진짜 할 만큼 해 봐서 별로 아쉽지가 않아. 그리고 다이빙이 \n은근 재밌더라고.” \n사실 나루도 알고 있었다. 언니가 다이빙을 정말로 좋아한다는 것을 \n말이다. 다이빙대에 오를 때마다, 다이빙 이야기를 할 때마다, 버들이\n의 얼굴에서는 환하게 빛이 났다. \n“너 10미터 다이빙대에 올라가 본 적 없지? 나중에 한번 해 봐. 해 \n보면 알 거야.”\n버들이는 아주 천천히 한 발씩 땅을 딛고 자리에서 일어났다. 마치 \n다이빙대 끝에 서 있는 것처럼 머리끝부터 발끝까지 바르고 곧았다. \n“날개가 없어도 아주 잠깐 하늘을 날 수 있어. 나는 물속으로 떨어\n지는 게 아니야. 왜냐면 누가 밀쳐서 빠지는 게 아니거든. 내가 뛴 \n거지. 뛰면서 계속 생각해. 최고로 아름다운 비행을 해야지.”\n버들이가 한 발짝 뛰어 나루 앞에 쪼그려 앉았다.\n“근데 정말 무슨 일인지 얘기 안 할 거야?”\n나루가 다시 입을 꾹 다물자 버들이도 더 이상 묻지 않았다.\n15\n20\n25\n◆\n◆체중: ‘체육중학교’의 줄임말.\n이야기를 읽으며 \n떠올린 질문이 \n있나요?\n각\n기\n생\n읽\n며\n떠올린 질문\n●\n●\n65\n1\n\n5\n10\n“나루야, 넌 나랑 달라. 너는 거기서 멋있게 뛰어. 방향이 아래를 \n향하더라도 너 스스로 뛴다면 그건 나는 거야.”\n나루는 버들이에게 수영을 왜 그만두었는지를 물었는데, 버들이는 \n다이빙을 하고 싶었다고 이야기했다. 나루는 그제야 코치님이 수영을 \n왜 하는지 생각해 보라고 했던 말의 의미를 알 것 같았다. 결국 그 물\n음은, 수영을 계속하고 싶은지 생각해 보라는 뜻이었다. \n어제 엄마가 수영을 그만둬도 괜찮다고 했을 때 나루는 정신이 번쩍 \n들었다.\n나루는, 그래도, 수영을 하고 싶었다. 아직은 수영장 물 밖으로 도망\n치고 싶지 않았다. 끝이라고 할 만큼 해 보지 않았고, 지금보다 더 잘\n할 수 있다고 생각했다. \n지금 나루는 10미터 다이빙대에 올라 있다. 뛸 것인가, 떨어질 것인\n가. 결정해야 할 순간이 왔다. \n66\n\n「다이빙대 위에서」를 읽고 물음에 답해 봅시다. \n(1)\u0001\t 나루가 버들이에게 화를 낸 까닭은 무엇인가요? \n(2)\t버들이가 수영을 그만둔 까닭은 무엇인가요?\n(3)\u0001\t코치님이 나루에게 수영을 왜 하는지 생각해 보라고 한 까닭은 무엇\n인가요?\n2.\n「다이빙대 위에서」를 일이 일어난 차례대로 정리해 봅시다.\n3.\n버들이가 수영을 그만두고 \n나루는 버들이가 수영을 그만둔 것을 받아들이기 어려워함.\n나루는 언젠가부터 수영 시합에서 라이벌 김초희에게 \n버들이가 힘들어하는 나루를 보러 찾아옴. 나루는 버들이에게 \n 물음.\n버들이의 말을 듣고, 나루는 수영을 \n 생각함.\n67\n1\n\n「다이빙대 위에서」를 다시 읽고 인물이 추구하는 가치를 파악해 봅시다.\n(1)\u0001\t 「다이빙대 위에서」의 한 장면을 다시 읽고 버들이가 다이빙을 하는 \n까닭을 친구들과 이야기해 보세요. \n4.\n(2)\u0001\t 두 인물이 추구하는 가치가 드러나는 말이나 행동을 찾아 써 보세요. \n상황\n인물\n인물의 말이나 행동\n버들이는 다른 사람과 경쟁해서 이기는 \n것을 행복이라고 생각하지 않았어.\n버들이는 아주 천천히 한 발씩 땅을 딛고 자리에서 일어났다. 마치 다이빙대 끝\n에 서 있는 것처럼 머리끝부터 발끝까지 바르고 곧았다. \n“날개가 없어도 아주 잠깐 하늘을 날 수 있어. 나는 물속으로 떨어지는 게 아니\n야. 왜냐면 누가 밀쳐서 빠지는 게 아니거든. 내가 뛴 거지. 뛰면서 계속 생각해. \n최고로 아름다운 비행을 해야지.”\n버들이는 수영을 그\n만두고 다이빙을 하\n고, 나루는 시합에서 \n김초희에게 계속 지고 \n있는 상황\n버들\n나루\n“근데 나루야, 수영 그만둬도 하늘 안 무너져.”\n68\n\n(3)\t 인물들이 추구하는 가치가 무엇인지 친구들과 이야기해 보세요.\n「다이빙대 위에서」의 인물들이 추구한 가치를 자신의 삶과 관련지어 \n이야기해 봅시다.  \n(1)\u0001\t 평소 자신은 누구와 비슷한 가치를 추구하고 있는지 정리해 보세요.\n5.\n나루가 버들이에게 기록이 잘 나오지 \n않더라도 수영을 포기하지 말았어야 \n한다고 말하는 것을 보면 나루는 끈기 \n있게 도전하는 것을 중요하게 생각해. \n \n나와 비슷한 가치를 추구하는 인물\n그렇게 생각한 까닭\n69\n1\n\n(2)\u0001\t「다이빙대 위에서」를 읽고 나서 생각이 달라진 점이나 새롭게 안 \n점을 보기를 참고해 친구들과 이야기해 보세요.\n●\u0007 인물의 말이나 행동을 보면서 자신이 추구하는 가치나 삶을 다시 생각한 점이 \n있나요?\n●\u0007 자신이 추구하는 가치와 다른 가치를 추구하는 인물을 보고 생각이 달라졌거\n나 새롭게 안 점이 있나요? \n보기\n5에서 생각한 내용을 바탕으로 「다이빙대 위에서」에 나온 인물에게 편지를 \n써 봅시다. \n(1)\t 누구에게 편지를 쓸지 정하고 하고 싶은 말을 써 보세요.\n6.\n \n친구들과 축구를 하다가 지면 기분이 \n정말 나빴는데, 내가 너무 승부에 \n집착한 것은 아닌지 생각해 봤어.\n편지를 받을 인물\n인물에게 하고 싶은 말\n이야기를 읽고 난 뒤 생각하거나 \n깊이 느낀 점, 전과 다르게 생각한 점을 \n구체적으로  이야기해 봐요.\n70\n\n(2)\u0001\t(1)에서 정한 인물에게 편지를 써 보세요.\n인물의 말과 행동을 보고 \n생각이 달라졌다면 그 점이 잘 \n드러나도록 편지를 써 봐요.\n인물이 소중하게 여긴 \n가치가 무엇인지 \n생각하며 편지를 써 봐요.\n71\n1"
  },
  "neighbor_sections": [
    {
      "relation": "previous",
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
      ]
    },
    {
      "relation": "next",
      "sheet_name": "9-11차시",
      "lesson_title": "작품을 읽고 독서 감상문 쓰기",
      "title_query": "작품을 읽고 독서 감상문 쓰기",
      "pdf_pages": [
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48
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
