# 캡스톤: 리서치 자동화 멀티 에이전트 시스템

주제를 넣으면 Agent가 자료를 모으고, 사람이 결과를 확인해 승인하면 보고서를 쓰고, 마지막에 보고서 품질을 점수로 매기는 프로그램을 만듭니다.
이 폴더의 `starter.py`에 남은 `TODO`를 AI와 함께 채워 완성합니다. 단계별 힌트와 확인 기준은 **4-3 캡스톤 LAB** 노트북에 있습니다. 정답 코드는 수업이 끝난 뒤 공개합니다. 아래 단계 번호(6.1~6.7)는 그 노트북 6장의 번호와 같습니다.

## 1. 전체 흐름

1. 사용자가 주제를 입력합니다.
2. Supervisor가 Researcher 실행을 결정합니다.
3. Researcher가 웹 검색, RAGaaS, MCP 문서 검색으로 자료를 모읍니다.
4. 사용자가 리서치 결과를 확인하고 보고서 작성을 승인합니다.
5. Writer가 보고서 초안을 작성합니다.
6. 최종 보고서를 평가하고 결과를 출력합니다.

## 2. 폴더 구성

| 파일 | 하는 일 | 고치나 |
|---|---|---|
| `starter.py` | 전체 프로그램의 뼈대입니다. `TODO` 자리를 채웁니다. | 고칩니다 |
| `mcp_server.py` | `data/`의 문서를 도구 3개(`list_docs`, `read_doc`, `search_docs`)로 내주는 MCP 서버입니다. | 그대로 씁니다 |
| `skills/researcher/research/SKILL.md` | Researcher가 따르는 규칙입니다(도구 쓰는 순서, 리서치 결과 형식). | 자유 주제일 때만 |
| `skills/writer/sds-report-writer/SKILL.md` | Writer가 따르는 규칙입니다(`[SDS-AI-RPT v2.1]` 보고서 양식). | 자유 주제일 때만 |
| `data/ai_trends.md`, `data/llm_market.md` | MCP 서버가 Researcher에게 보여 주는 문서입니다. | 자유 주제일 때만 |

## 3. 실행 방법

`starter.py`는 아래 5장 체크리스트의 6.1~6.7을 모두 채운 뒤 실행합니다. 6.6까지만 채우면 보고서까지 나오고 점수는 나오지 않습니다. 채우기 전에 실행하면 오류 없이 `⚠️ 실행 코드(6.6)가 아직 비어 있어 여기서 끝납니다.`가 나오고 끝납니다.

VS Code에서 터미널을 두 개 엽니다(메뉴 **터미널 → 새 터미널**). 두 터미널 모두 저장소 맨 위 폴더에서 실행합니다.

**터미널 A — MCP 서버 켜기** (먼저)

```
uv run python course/Chapter02/capstone/mcp_server.py
```

`Uvicorn running on http://127.0.0.1:8001`이 나오고 명령이 끝나지 않고 기다리면 켜진 것입니다. 이 터미널은 닫지 않습니다.

**터미널 B — 프로그램 실행**

```
uv run python course/Chapter02/capstone/starter.py
```

1. `MCP 도구 로드: [...]`가 나오고 리서치가 시작됩니다.
2. 리서치 결과가 나온 뒤 `보고서 작성을 시작할까요? (y/n):`에서 멈춥니다.
3. 영문 입력 상태에서 `y`를 입력하고 Enter를 누르면 보고서 작성과 평가가 이어집니다. `n`이면 `취소됐습니다.`로 끝납니다. 한글 입력 상태의 `ㅛ`나 빈 Enter도 취소로 처리됩니다. `y`와 `n`의 결과를 둘 다 보려면 한 번 더 실행합니다.
4. 마지막에 네 항목 점수와 `종합 점수`가 나옵니다. 같은 점수는 Langfuse 대시보드에도 남습니다.

한 번 실행에 1분 안팎이 걸립니다. 터미널 B의 프로그램은 점수를 출력하면 저절로 끝납니다. 다 쓴 뒤에는 터미널 A에서 **Ctrl+C**로 서버를 끕니다.

## 4. RAGaaS 연결

- `.env`의 `COURSE_ENV=samsung`(사내망)이면 사내 RAGaaS를 실제로 호출합니다. `.env`에 `index_name`과 RAGaaS 키가 있어야 합니다.
- `COURSE_ENV=out`(사내망 밖)이면 네트워크 없이 모의 응답을 돌려줍니다. 결과에 `[MOCK RAGaaS]`가 붙어 있으면 정상입니다.

## 5. 단계별 체크리스트

| 단계 | 할 일 | 🟢 되어야 하는 것 |
|---|---|---|
| 준비 | MCP 서버 켜기 | 터미널 A에 `Uvicorn running on http://127.0.0.1:8001`이 나오고 끝나지 않고 기다린다 |
| 6.1 도구 | `search_web`, `rag_search` 채우기 | Langfuse의 Researcher trace에서 `rag_search` 결과가 `null`이 아닌 글로 보인다 |
| 6.2 State | 노드끼리 주고받을 값 추가 | 실행 중 `KeyError`가 나지 않는다 |
| 6.3 MCP 연결과 두 Agent | MCP 도구 받아 오기, Researcher·Writer 만들기 | `MCP 도구 로드: [...]`에 도구 3개가 보인다 |
| 6.4 노드 | Supervisor·Researcher·Writer 노드 | `🔍 Researcher 실행 중...`, `✍️  Writer 실행 중...`이 한 번씩 나온다 |
| 6.5 그래프와 승인 | 노드 연결, Writer 앞에서 멈추기 | 리서치 결과 뒤 `(y/n)`에서 멈춘다 |
| 6.6 실행과 재개 | 리서치까지 실행 → 승인 → 이어서 실행 | `y` 뒤 `[SDS-AI-RPT v2.1]` 양식 보고서가 나온다 |
| 6.7 평가 | LLM Judge 채점, Langfuse에 점수 기록 | 네 항목 점수와 `종합 점수`가 나온다 |

## 6. 평가 기준

1. **체크리스트 일곱 단계(6.1~6.7)를 모두 통과**합니다.
2. **LLM Judge 네 항목**으로 보고서를 평가합니다. 각 항목 0.0~1.0 점수와 채점 근거, 평균 점수가 나오고 Langfuse Score로 기록됩니다.
   - Relevance(관련성): 주제와 관련 있는가
   - Faithfulness(근거충실도): 리서치 근거에 충실한가
   - Completeness(완성도): 보고서 구성이 완성되어 있는가
   - Clarity(명확성): 문장과 구조가 명확한가

일찍 끝났다면(선택): 터미널의 `y/n` 승인을 Streamlit 화면의 버튼으로 바꿔 봅니다.

## 7. 자주 막히는 곳

- `error while attempting to bind on address` 오류(맥 `address already in use`, Windows `[Errno 10048]`): 8001 포트를 다른 서버(3일차 A2A 서버, 앞서 켠 캡스톤 서버 등)가 쓰고 있습니다. 그 서버를 띄운 터미널에서 **Ctrl+C**로 끄고 다시 켭니다.
- 연결 오류(`ConnectError` 등)로 시작하자마자 멈춤: 터미널 A의 MCP 서버를 먼저 켭니다.
- 점수는 나오는데 Langfuse에 없음: `.env`의 `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`을 확인합니다. 저장소 맨 위에서 `uv run python -m config.check --langfuse`로 점검합니다.
