# 4-1 교안 노트북 — 목차 (v1, 2026-09-28)

> 2026-10-18: 실습 노트북에서 "AI에게 물어보기" 절을 뺐다(`dev/AGENTS.md`). 아래의 물어보기 항목은 지난 설계 기록이고 빌드에 쓰이지 않는다.

- **권 제목**: Harness Engineering 핵심 원칙 (PDF 제목 "4-1 Harness Engineering 핵심 원칙")
- **원본 슬라이드**: `course/Chapter02/slides/day02/4-1-harness-engineering-core-principles.pdf` (22쪽. 표지 p1, 목차 p2, 장 표지 p3·p7·p11·p16, 정리 p21, 코드 소개 p22)
- **원본 코드**: `course/Chapter02/code/raw/04-harness/`
  - `agent.py` (TODO 1개, 55–56행. 배포 상태대로 정답 줄 57–66행이 채워져 있다)
  - `skills/samsung-ds-report/SKILL.md` (Agent가 읽는 스킬 문서. raw·solution 동일)
  - `skills.md` (역할·행동 규칙 문서. raw·solution 동일. **agent.py가 읽지 않는다**)
  - solution에만 `ai_agent_trends_report.md` (DS 양식 보고서 산출물, 102줄. 만든 방법은 기록이 없다)
- **input() 대화 루프**: **없다.** 이름은 "대화형 실행"이지만 `test_cases` 두 건(보고서 요청, 퀵소트 요청)을 차례로 돌리고 끝난다. 노트북 셀로 그대로 실행할 수 있다.
- **커리큘럼**: 4일차 4.1 "Harness Engineering 핵심 원칙" 2.0H. 이 목차는 **LEC 40분 + LAB 75분**(쉬는 시간 여유 5분)을 가정한다. 슬라이드 본문이 17쪽이고, 코드는 한 파일이지만 "SKILL.md를 고쳐 다시 실행"을 여러 번 돌리는 것이 이 권의 핵심이라 LAB을 길게 잡았다.
- **산출물**: `course/Chapter02/notebooks/4-1_harness_LEC.ipynb`, `course/Chapter02/notebooks/4-1_harness_LAB.ipynb` (`build_lab.py`의 UNITS에 `"04-harness": ("4-1", "harness")`가 이미 있다. `dev/builders/labs/Chapter02/`의 spec은 아직 없다)
- **실행 검증**: 이 목차 단계에서는 실행하지 않았다. `dev/docs/VALIDATION.md`의 사외 실행 표에 하네스가 따로 적혀 있지 않다("solution 실행 스크립트 38개"에 들어갔는지 확인 필요). 호출 수·시간은 코드 구조로 추정한 값이다.
- **과정 목표와의 관계**: 루트 AGENTS.md 2절 목표 3(하네스·루프 엔지니어링)과 직접 이어진다. 그래서 LAB의 중심을 "SKILL.md를 고친다 → 다시 실행한다 → 결과를 규칙과 대조한다"는 루프에 둔다.

## 1. LEC 목차

슬라이드 PDF.js + C 수준 설명(슬라이드 요약, 내용 있는 곳만 "왜 배우나") + 4지선다 퀴즈. 코드 셀 없음(p22의 코드는 슬라이드 그림으로만 보여 준다).

| # | 절 제목 | 슬라이드 | 핵심 메시지 (근거 쪽) | 왜 배우나 | 퀴즈 (4지선다) |
|---|---|---|---|---|---|
| 1 | 도입 | p1–2 | 네 장: 등장 배경 → 하네스란? → Building Effective Agents → SKILL.md 작성 원칙 (p2) | — | — |
| 2 | 모델 성능 중심 접근의 한계 | p3–4 | 초기에는 더 좋은 모델·프롬프트가 경쟁력이었고, 이어 컨텍스트 엔지니어링이 중요해졌다. 모델이 충분히 강해진 뒤 병목은 모델 자체에서 **모델을 운영하는 구조**로 옮겨 갔다 (p4) | — | 모델이 충분히 강해진 뒤 병목이 옮겨 간 곳은? (정답: 모델을 운영하는 구조) |
| 3 | 장시간 자율 실행의 요구 | p5 | 코드 작성·리서치·분석·문서화는 한 번의 답변보다 긴 실행 흐름이 필요하다: 중간 상태 기억, 적절한 시점의 도구 호출, 검증과 재시도, 지시 없이 이어지는 흐름. 문제가 "질문을 잘 쓰기"에서 "AI가 일하는 시스템 설계"로 이동했다 (p5) | 3일차의 MCP(도구)·A2A(위임)·LangGraph 심화(상태·메모리)가 모두 이 목록의 한 조각이다. 이 권은 그것들을 한 실행 환경으로 묶는 관점이다 (CURRICULUM 3.2–3.4) | 긴 실행 흐름에 필요한 것으로 슬라이드에 **없는** 것은? (오답 후보: 더 긴 프롬프트) |
| 4 | 세 가지 엔지니어링의 초점 | p6 | Prompt = 질문 설계, Context = 정보 설계, Harness = 운영 구조 설계(목표 수행·검증·상태 유지를 위한 실행 환경) (p6) | 1일차에 배운 프롬프트·역할 분리(1.2)와 RAG(컨텍스트)가 앞 두 단계다 | 설명과 이름 짝짓기: "AI가 목표를 수행하고 검증하며 상태를 이어가도록 실행 환경을 만든다"는? |
| 5 | AI가 일하는 환경을 설계하는 관점 | p7–8 | 모델·도구·메모리·역할·작업 흐름·검증 규칙을 조율한다. 더 긴 지시문이 아니라 **일이 끝나는 조건**을 준다. 좋은 하네스는 AI를 답변기에서 실행 주체로 바꾼다 (p8) | — | 하네스가 모델에게 주는 것으로 알맞은 것은? (정답: 일이 끝나는 조건) |
| 6 | 위임을 위한 제어 구조 | p9 | 하네스는 무제한 자동화 장치가 아니라 안정적 위임 구조다. 목표·제약, 허용 도구와 금지 행동, 검증 기준, 실패 시 멈춤/재시도/사람에게 묻기를 정한다 (p9) | 이 권 LAB의 `system_prompt`(범위 이탈 거절)가 "금지 행동"의 예다 | 하네스의 역할이 **아닌** 것은? (오답 후보: 사람의 확인 없이 모든 작업을 무제한 자동화) |
| 7 | 하네스 설계의 기본 순서 | p10 | 목표 정의 → 작업 분해 → 도구 연결 → 검증 설계 → 예외 처리 (p10) | — | 다섯 단계의 올바른 순서는? (보기 4개가 순서만 다름) |
| 8 | 단순하게 시작하라 | p11–12 | 먼저 단순한 프롬프트·검색·단일 도구 호출로 되는지 본다. 복잡한 구조는 명확한 성능 개선이 있을 때만 더한다. 하네스는 복잡해야 좋은 것이 아니라 충분해야 좋다 (p12) | 2-2(Multi-Agent)의 "단일 Agent를 먼저 고려" 기준과 같은 이야기다 | 복잡한 구조를 추가해도 되는 때는? (정답: 명확한 성능 개선이 있을 때) |
| 9 | Workflow vs Agent | p13–15 | Workflow = 개발자가 단계·분기·도구 순서를 미리 설계, 예측·테스트 쉬움. Agent = 모델이 관찰 결과로 다음 행동을 고름. 순서가 명확하고 재현성이 중요하면 Workflow, 다음 행동을 미리 알기 어렵고 계획을 바꿔야 하면 Agent (p13–15) | 캡스톤 스켈레톤(Supervisor → Researcher → 승인 → Writer)은 정해진 흐름 안에 판단하는 Agent를 넣은 구조다. 어느 부분을 고정하고 어느 부분을 맡길지 고르는 기준이 된다 (CURRICULUM 4.3) | 상황 문제: "표준 템플릿 기반 산출물 작성"에 알맞은 쪽은? / "원인을 알 수 없는 오류 디버깅"은? (한 문항, 짝짓기 보기) |
| 10 | Skill의 역할 | p16–17 | SKILL.md는 특정 작업의 절차 문서다. **언제** 쓰는지와 **어떻게** 하는지 알려 준다. 모든 지침을 프롬프트에 넣지 않고 작업별로 분리한다. Agent가 필요한 Skill을 골라 따른다 (p17) | 이 권 LAB에서 코드와 모델을 그대로 두고 SKILL.md만 고쳐 동작을 바꿔 본다. 캡스톤에서도 Researcher/Writer에 SKILL.md를 붙인다 (CURRICULUM 4.3) | SKILL.md를 쓰는 이유로 알맞은 것은? (정답: 작업별 지침을 프롬프트에서 분리) |
| 11 | SKILL.md의 기본 구조 | p18 | 상단 정보(Description·When to use·Constraints), 수행 정보(Workflow·Examples·Verification) (p18) | — | "품질 기준과 확인 방법"이 들어가는 항목은? (정답: Verification) |
| 12 | 좋은 SKILL.md 작성 기준과 순서 | p19–20 | 적용 조건을 모호하게 쓰지 않는다, 실제 행동 순서대로, 파일·도구·명령·출력 위치를 명확히, 성공 조건·검증 방법, 실패 시 대처. 작성 순서: 목적 → 조건 → 절차 → 도구 → 검증 (p19–20) | LAB 마지막 장에서 이 기준으로 받은 SKILL.md의 빠진 곳을 찾는다 | 좋은 SKILL.md 기준이 **아닌** 것은? (오답 후보: 적용 조건을 넓게 두어 어디서나 쓰이게 한다) |
| 13 | 정리 | p21 | 운영 구조 설계, 단순하게 시작해 실패 지점을 관찰하며 확장, Workflow/Agent 선택, SKILL.md는 재현·검증 가능한 실천 도구 (p21) | "실패 지점을 관찰"하는 도구가 다음 권(4-2 Langfuse)이다 (CURRICULUM 4.2) | — |
| 14 | create_deep_agent 소개 | p22 | 모델·도구·시스템 프롬프트·체크포인터·파일 시스템 백엔드를 한 실행 환경으로 묶고, `skills=["skills/"]`로 SKILL.md 폴더를 연결한다 (p22) | LAB의 과제가 바로 이 함수 호출이다 | `skills=["skills/"]`가 하는 일은? (정답: SKILL.md가 든 폴더를 연결) |
| 15 | 정리 퀴즈 | — | 네 장의 핵심 | — | 3문항: ① Prompt/Context/Harness 구분 ② Workflow·Agent 상황 판단 ③ SKILL.md 구조 항목 |

- 퀴즈는 모두 4지선다, 정답은 슬라이드 문구에서만 만든다. 수강생 글에는 쪽 표시를 넣지 않는다.
- p22는 코드가 든 슬라이드다. LEC에 코드 셀을 두지 않는 규칙대로 슬라이드로만 보여 준다. 슬라이드 코드는 `root_dir="."`이고 원본 코드는 `root_dir=str(HARNESS_DIR)`이다(4절 참고).

## 2. LAB 목차

첫 구획(접힌 준비 셀) → 보이는 코드 셀. `agent.py`는 `# ──` 구분선으로 준비 / 도구 정의 / Agent 생성 / 대화형 실행 네 구획으로 나뉜다.

### 2.0 skills 폴더를 어디에 두고 어떻게 읽히나 (제안)

원본은 `HARNESS_DIR = Path(__file__).parent`와 `FilesystemBackend(root_dir=str(HARNESS_DIR), virtual_mode=True)`, `skills=['skills/']`에 의존한다. 노트북에는 `__file__`이 없어 그대로 두면 `NameError`가 난다.

| 안 | 방법 | 장점 | 단점 |
|---|---|---|---|
| **A (제안)** | 노트북 폴더 아래 전용 작업 폴더 `harness/`를 Agent의 작업 공간으로 쓴다. spec `patch`로 `HARNESS_DIR = Path('harness')`. SKILL.md는 노트북 셀에서 `%%writefile harness/skills/samsung-ds-report/SKILL.md`로 쓴다. `%%writefile`은 폴더를 만들지 않으므로 준비 셀에서 `HARNESS_DIR.joinpath('skills/samsung-ds-report').mkdir(parents=True, exist_ok=True)`를 먼저 한다 | 수강생이 SKILL.md 내용을 노트북 안에서 보고, 고치고, 다시 쓸 수 있다(수강생은 노트북만 받는다). Agent의 파일 도구가 노트북 폴더 전체가 아니라 `harness/`만 건드린다 | 준비 셀에 한 줄이 더 들어간다. 빌더에 .md 파일 writefile 지원을 더해야 한다(4절) |
| B | `root_dir`을 `../code/raw/04-harness`로 둔다 | 코드 변경이 가장 적다 | 수강생은 `.py`·경로를 보지 않는다는 규칙과 어긋난다. Agent의 `write_file`·`edit_file`이 원본 코드 폴더에 파일을 쓴다. SKILL.md를 고치려면 노트북 밖 파일을 열어야 한다 |
| C | 슬라이드처럼 `root_dir="."`(노트북 폴더) | 슬라이드와 같다 | Agent가 노트북 폴더의 파일(노트북 자체 포함)을 읽고 쓸 수 있다 |

- A안에서 `harness/`는 원본 `04-harness/` 폴더 구조를 그대로 옮긴 것이므로 가상 경로 `/skills/samsung-ds-report/SKILL.md`가 원본과 같다.
- `skills.md`(루트 문서)는 코드가 읽지 않으므로 A안에서도 쓰지 않는다(5절 질문 2).

### 2.1 장 구성

| 장 | 원본 | 구분 | CHANGE_HERE 후보 / WRITE_HERE로 바꿀 TODO | 성공 기준 초안 | 실행 제약 |
|---|---|---|---|---|---|
| 1 | (환경 확인) | — | — | — | 공통 셀. `deepagents` 불러오기 확인 |
| 2 | `SKILL.md` (Agent가 읽을 스킬 쓰기) | **예제** + AI에게 물어보기 | 바꾸지 않고 그대로 쓴다(원본 상태). `%%writefile` 셀 1개<br>물어보기: SKILL.md를 붙여 넣고 "윗부분(name·description)과 아랫부분(양식·작성 규칙)이 각각 Agent에게 무엇을 알려 주는지" 설명받기 | 🟢 셀 출력에 `Writing harness/skills/samsung-ds-report/SKILL.md`가 보인다<br>🟢 (물어보기) description은 "언제 쓰는지", 본문은 "어떻게 쓰는지"라고 구분했다<br>⛔ `No such file or directory` → 준비 셀(폴더 만들기)을 먼저 실행 | LLM 호출 없음 |
| 3 | `agent.py` | 도구 정의 = 예제, Agent 생성 = **과제**, 실행 = 예제 | **과제 1곳**: 55–56행<br>`# TODO: LLM, 사용가능한 도구, 백엔드, 스킬, 시스템 프롬프트를 이용해 Deep Agent를 정의해주세요.`<br>`# 이때, 시스템 프롬프트룰 이용해 범위를 벗어나지 않도록 해주세요.`<br>→ 빈칸 57–66행(`model=` ~ `checkpointer=MemorySaver(),`, 사이 주석 포함)<br>52행 `backend = FilesystemBackend(...)`는 빈칸 밖에 두어 보여 준다 | 🟢 사례 1 출력 단계에 `[ToolMessage]`로 SKILL.md 앞부분(`name: samsung-ds-report` 등)이 보인다 = Agent가 스킬을 읽었다<br>🟢 사례 1 마지막 `[AIMessage]`가 `[DS-AI-RPT v2.1]`로 시작한다<br>🟢 사례 2(퀵소트)는 코드 없이 정중히 거절한다<br>⛔ 마지막 답이 DS 양식이 아니고 SKILL.md를 읽은 단계도 없다 → `skills`·`backend` 인자 확인<br>⛔ 사례 2에서 퀵소트 코드가 나온다 → `system_prompt` 확인<br>⛔ `GraphRecursionError` → 셀 다시 실행, 반복되면 강사에게 | 사례 1: LLM 약 3~8회(파일 목록·SKILL.md 읽기·검색·작성, 추정), 사례 2: 1회. 합쳐 1~3분 추정. `recursion_limit` 40. 실행 셀 하나가 두 사례를 모두 돈다 |
| 4 | `SKILL.md` 고쳐 동작 바꾸기 (핵심) | **예제** (루프) | 2장의 SKILL.md를 CHANGE_HERE 한 줄만 바꾼 두 번째 `%%writefile` 셀로 다시 쓰고, 3장의 **Agent 생성 셀과 실행 셀을 다시 실행**한다(4절 "스킬 캐시")<br>CHANGE_HERE 후보(한 가지를 고른다, 5절 질문 1):<br>(가) frontmatter `description:` 줄 — YAML 주석이라 `# ✍️ CHANGE_HERE:` 표시가 문서를 해치지 않는다. 예: 발동 조건 문구("보고서", "리포트", "DS 양식")를 지워 본다<br>(나) 양식의 `보안등급: INTERNAL  \|  배포범위: AI연구소 내부` 줄 — 바뀐 값이 결과 첫 80자 안에 보여 눈으로 확인이 쉽다. 단 표시 주석 처리 방식이 필요하다 | (가) 🟢 SKILL.md를 읽는 `[ToolMessage]` 단계가 사라지거나, 결과가 DS 양식이 아니게 된다 (LLM 판단이라 매번 같지 않음)<br>(나) 🟢 결과 셋째 줄 보안등급이 바꾼 값으로 나온다<br>공통 ⛔ 결과가 바꾸기 전과 똑같다 → Agent 생성 셀부터 다시 실행했는지 확인 | 한 번 돌 때 3장과 같음(1~3분). 수강생이 2~3번 바꿔 보면 10분 안팎 |
| 5 | 산출물 리뷰와 SKILL.md 보강 | **AI에게 물어보기** (코드 빈칸 없음) | ① 4장 결과(또는 3장 결과)를 SKILL.md의 "작성 규칙" 5개와 대조받기<br>② SKILL.md를 슬라이드의 기본 구조(Description·When to use·Constraints·Workflow·Examples·Verification)와 비교해 빠진 항목을 찾고, 한 항목을 보강해 2장 셀로 다시 쓴 뒤 3장 실행 셀을 다시 돌리기 | 🟢 ① 규칙마다 지켰다/안 지켰다를 결과 줄을 짚어 판정받았다<br>🟢 ② "언제 쓰지 않는지", "Workflow(작업 순서)", "Verification"이 SKILL.md에 없다는 점을 짚었다<br>⛔ AI가 SKILL.md를 통째로 새로 써 원래 양식이 사라졌다 → 한 항목만 더하도록 다시 지시 | ②를 다시 실행하면 3장과 같은 비용 |
| 6 | 정리 | — | — | — | — |

- 예제/과제 기준: `create_deep_agent`의 인자는 이 권 LEC 14절(p22)에서 그대로 보여 준다. 인자 가운데 모델(`get_llm`)·도구(`@tool`)·체크포인터(`MemorySaver`)는 M1에서 배웠다. 그래서 Agent 생성은 **과제**로 둔다. `FilesystemBackend`는 이 권에서 처음 나오므로 빈칸 밖(보이는 코드)에 두고, 코드 지도 설명에서 짚는다.
- 프롬프트 힌트 초안(과제, 3문장 이내): "과제 셀 전체와 SKILL.md 폴더 위치를 AI에게 보여 주고, 모델·도구·백엔드·스킬 폴더·범위를 지키는 시스템 프롬프트·체크포인터를 넣어 `create_deep_agent`를 완성해 달라고 합니다. 시스템 프롬프트에는 어떤 요청을 거절해야 하는지 구체적으로 적으라고 덧붙입니다."
- 4장이 이 권의 중심이다. 코드와 모델은 그대로 두고 문서 한 줄로 동작이 바뀌는 것을 본다. 5장은 과정 목표 4(AI 산출물을 검토하고 다시 지시)를 SKILL.md에 적용한 루프다.
- 합계: LAB 본문 4장(과제 1곳, CHANGE_HERE 1곳, 물어보기 2개 + 리뷰 1개).

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽 | 이유 |
|---|---|---|---|
| `agent.py` 55–66행 (Agent 생성) | ① TODO 2줄은 raw에만 있다(오타 "프롬프트룰")<br>② 도구 줄 주석: raw `# @tool 데코레이터로 도구 처리된 함수들 리스트로 추가` + `# + mcp_tools` / solution은 정의되지 않은 `MCP_CONFIG`·`await`가 든 주석 3줄<br>③ 시스템 프롬프트 설명 주석: raw 3줄(이전 강사 말투, "평소와 같아...") / solution 1줄 `# 범위 이탈 거절은 system_prompt로 강제 (skills의 description만으로는 부족)`<br>④ `system_prompt`: raw `…보고서 작성과 무관한 요청은…` / solution `…보고서·리서치 범위를 벗어난 요청은…`<br>⑤ solution에 `# middleware` 한 줄 | **raw 뼈대 + 정답은 solution 쪽 주석·프롬프트** (spec `answer`) | 빈칸 과제에 TODO가 필요하다(오타는 WRITE_HERE로 바꿀 때 고친다). 정답 보기는 solution 주석이 짧고 이유가 분명하다. MCP 주석과 `# middleware`는 쓰이지 않는 코드라 뺀다 |
| `agent.py` 74행 `recursion_limit` | raw 40 / solution 35 | raw | 여유가 더 크다. 설명 주석(기본값 25)은 같다 |
| `agent.py` 85행 출력 길이 | raw `content[:80]` / solution `content[:200]` | **solution** | 80자면 SKILL.md를 읽는 단계와 보고서 머리가 잘 안 보인다. 4장 (가)안의 확인에도 200자가 낫다 |
| `agent.py` 1–10행 docstring | raw·solution 모두 `skills/research-writing/SKILL.md`라고 적혀 있다. 실제 스킬은 `samsung-ds-report`다 | patch로 고친다 | 준비 셀에 들어가 수강생에게 거의 보이지 않지만 틀린 설명이다 |
| `SKILL.md`, `skills.md` | 차이 없음 | raw | — |
| `ai_agent_trends_report.md` | solution에만 있다. `[DS-1.0]`~`[DS-7.0]` 7개 절로 템플릿(3개 절)과 다르고, 작성 규칙 4번의 "DS 영향도(상/중/하)" 표가 없다. 검색 도구가 준 적 없는 참고 자료(Gartner·McKinsey)와 사람 이름("검토: 김연구 \| 승인: 이소장")이 들어 있다 | LAB에 넣지 않음 (5절 질문 3) | 어떤 요청으로 만든 것인지 기록이 없다. 5장 리뷰 예시로 쓸 수는 있다 |

## 4. 실행 제약·위험과 처리 제안

| 항목 | 내용 | 노트북 처리 제안 |
|---|---|---|
| `__file__` 없음 | 노트북에서 `Path(__file__)`은 `NameError` | spec `patch`: `HARNESS_DIR = Path('harness')` (2.0 A안) |
| `sys.stdout.reconfigure` | Jupyter 출력 객체(`ipykernel` OutStream)에는 `reconfigure`가 없어 준비 셀에서 `AttributeError`가 난다(확인함: `hasattr(OutStream, 'reconfigure')` = False) | spec `patch`로 이 줄을 뺀다 |
| 스킬 캐시 | deepagents 0.7.18의 SkillsMiddleware는 스킬 목록(name·description)을 **스레드마다 한 번** 읽어 상태에 저장한다. 같은 체크포인터·같은 `session_id`로 다시 부르면 고친 description이 반영되지 않는다(`middleware/skills.py` 설명). 같은 스레드에는 이전 대화도 남아 있다 | 4장 안내: "SKILL.md를 고친 뒤 **Agent 생성 셀부터** 다시 실행한다"(새 `MemorySaver`로 새로 시작). 4장 ⛔ 기준에도 적는다 |
| Agent의 파일 쓰기 | deepagents는 `ls`·`read_file`·`write_file`·`edit_file`·`glob`·`grep` 도구를 기본으로 붙인다. `virtual_mode=True`는 `root_dir` 밖 경로를 막지만 샌드박스는 아니다 | A안처럼 `root_dir`을 전용 `harness/` 폴더로 좁힌다. Agent가 보고서를 파일로 저장하면 `harness/` 안에 생긴다 |
| 빌더 지원 | `build_lab.py`의 `writefile`은 (1) 파일을 ruff로 정돈하고 (2) `run`이 terminal이 아니면 Streamlit 실행 셀을 자동으로 붙이며 (3) 폴더를 만들지 않는다. SKILL.md(.md)를 쓰는 셀에는 맞지 않는다 | .md는 정돈하지 않고, 실행 셀 없이 안내 글만 두는 선택지(예: `run: "none"`)를 빌더에 더한다. 폴더 만들기는 준비 셀 patch로 한다 |
| CHANGE_HERE 표시와 마크다운 | `# ✍️ CHANGE_HERE:` 줄이 SKILL.md 본문에 들어가면 Agent가 읽는 제목(`#`)이 되고, 양식 코드 블록 안이면 보고서에 그대로 베껴질 수 있다. frontmatter 안에서는 YAML 주석이라 안전하다. QC는 `# ✍️` 접두어를 요구한다 | 4장 CHANGE_HERE는 frontmatter의 `description:`(가안)에 둔다. 본문(나안)을 쓰려면 표시 방식을 따로 정한다(5절 질문 1) |
| 사내 게이트웨이 도구 호출 | deepagents는 모든 단계가 도구 호출(`bind_tools`)이다. 사내 게이트웨이의 도구 호출은 **미검증** | 강의장 사전 확인 목록 1순위. 안 되면 LAB 전체가 멈춘다. 대안은 강사 화면 시연(강사 메모) |
| 사외 실행 | VALIDATION.md 표에 하네스 결과가 따로 없다 | 제작 단계에서 `COURSE_ENV=out`으로 실측해 호출 수·시간을 강사 메모에 적는다 |
| LLM 판단의 흔들림 | 스킬을 쓸지는 모델이 description을 보고 정한다. 4장 (가)안 결과는 매번 같지 않을 수 있다 | 성공 기준을 "달라졌는지"로 적고, "같다면 한 번 더 실행" 안내 |
| `chat()` 반환값 | `response = ''`를 채우지 않아 늘 빈 문자열을 돌려준다. 반환값을 쓰는 곳이 없어 화면에는 영향이 없다 | 그대로 둔다(고치면 원본과 달라짐). 5장 물어보기 소재로 쓰지 않는다 |
| 긴 출력·가독성 | 단계마다 한 줄씩 출력하고 최종 보고서 전문은 출력하지 않는다 | 볼 지점을 "`[ToolMessage]`에 SKILL.md가 보이는 줄"과 "마지막 `[AIMessage]` 첫 줄" 두 곳으로 안내 |
| input()·메일 발송·서버 | 없음 | — |

## 5. 확인이 필요한 질문

1. **4장 CHANGE_HERE를 어디에 둘까요?** (가) frontmatter `description:` 줄 — QC 표시 규칙과 맞고 "스킬이 언제 쓰이나"를 보여 주지만 결과가 흔들립니다. (나) 양식 본문의 보안등급 줄 — 결과가 분명하지만 `# ✍️ CHANGE_HERE:` 표시가 SKILL.md 안에 들어가 Agent가 읽게 됩니다(표시 방식 예외 필요). 제안은 (가)입니다.
2. **`skills.md`(코드가 읽지 않는 역할·규칙 문서)를 어떻게 할까요?** 제안: LAB에서 뺍니다. 필요하면 5장 물어보기에서 "한 문서에 다 넣은 규칙 vs 작업별 SKILL.md" 비교 자료로만 씁니다.
3. **solution의 `ai_agent_trends_report.md`를 5장 리뷰 예시로 넣을까요?** 규칙 위반(영향도 표 없음, 절 수 다름)과 도구에 없던 출처·이름이 있어 리뷰 소재로 좋지만, 만든 요청이 기록에 없습니다. 제안: 넣지 않고 수강생 본인 실행 결과로 리뷰합니다.
