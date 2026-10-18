# 2-3 교안 노트북 — 1단계 목차 (v1, 2026-09-28)

> 2026-10-18: 실습 노트북에서 "AI에게 물어보기" 절을 뺐다(`dev/AGENTS.md`). 아래의 물어보기 항목은 지난 설계 기록이고 빌드에 쓰이지 않는다.

- **권 제목**: Streamlit을 활용한 RAG 배포 (PDF 1쪽 제목)
- **원본**: PDF `docs/raw/Chapter01/day02/2-3-streamlit-rag.pdf`(13쪽), 코드 `src/raw/Chapter01/06-rag-streamlit/` — `app.py`, `test.py`, `data/meritz_pet_insurance.pdf`(28쪽, 원본·솔루션 동일)
- **커리큘럼 시간**: 2.3 블록 "Multi-Agent 협업 입문 / Streamlit 기반 RAG 서비스화" 2.0H를 2-2와 나눠 쓴다. 블록 안 시간 배분은 커리큘럼에 없다.
- **노트북**: `lessons/Chapter01/2-3_rag_streamlit_LEC.ipynb`, `lessons/Chapter01/2-3_rag_streamlit_LAB.ipynb`(빌더 spec `lessons/drafts/labs/06-rag-streamlit.json`, 현재 뼈대 상태)
- **환경**: 사외 준비는 `LLM_PROVIDER=openai`, `EMBED_PROVIDER=openai`. 이 권에는 사내 RAGaaS 같은 사내 전용 기능이 없다. 임베딩과 LLM만 쓰므로 사내·사외 모두 실행할 수 있다.

## 1. LEC 목차

C 수준: 슬라이드 요약, 내용이 있는 곳에만 "왜 배우나", 4지선다 퀴즈. 코드 셀은 두지 않는다(슬라이드 셀만).

| # | 절 제목 | 슬라이드 | 핵심 메시지 (근거 쪽) | 퀴즈 (한 줄 질문) |
|---|---|---|---|---|
| 1 | 학습 목차 | p1–2 | Streamlit → 앱 기본 구성(title·caption, cache_resource) → 채팅 인터페이스(session_state, chat_message·chat_input, write_stream) (p2) | — |
| 2 | Streamlit 소개 | p3–4 | Python만으로 웹 화면을 만든다. HTML·CSS·JS를 쓰지 않는다. 쓰는 이유: 콘솔 결과를 보기 쉬운 화면으로, 입력창·답변 영역을 간단히, 스트리밍으로 생성 과정을 보여 주고, 앞에서 만든 RAG Chain을 서비스 형태로 확인한다 (p4). **왜**: 앞 권의 RAG 체인을 사람이 쓰는 화면에 붙이는 마지막 단계 | Streamlit을 LLM 실습에 쓰는 이유가 **아닌** 것은? |
| 3 | Python 코드 기반 웹 UI | p5 | 스크립트가 위에서 아래로 실행되며 화면을 그린다. 입력이 생기면 **전체 스크립트가 다시 실행**된다. 유지할 값은 `st.session_state`, 무거운 초기화는 cache (p5). **왜**: 이 재실행 구조가 뒤의 cache_resource·session_state가 필요한 이유다 | 버튼을 누르면 Streamlit에서 무슨 일이 일어나는가? |
| 4 | title과 caption | p6–8 | `st.title`은 가장 큰 제목, `st.caption`은 제목 아래 짧은 보조 설명(어떤 데이터로 답하는지) (p7, p8) | (퀴즈 없음. 내용이 가벼움) |
| 5 | cache_resource | p9 | 모델·벡터스토어·DB 연결처럼 만드는 데 오래 걸리는 것을 한 번만 만들고 재실행 때 재사용한다. 실습에서는 `load_rag_chain()`에 붙인다 (p9). **왜**: 없으면 질문할 때마다 PDF를 다시 읽고 임베딩을 다시 만든다 | `@st.cache_resource`를 붙이기에 알맞은 것은? (RAG 체인 / 대화 기록 / 제목 글자 / 입력창) |
| 6 | session_state | p10–11 | 일반 변수는 재실행 때 사라진다. 대화 기록은 `session_state`에 저장하고, 매번 저장된 메시지를 다시 출력한다 (p11). **왜**: 원본 코드 주석대로 이 기록은 **화면 표시용**이다. 이 기록으로 LLM이 이전 대화를 기억하지는 않는다 | 대화 기록을 일반 변수(리스트)에만 담으면 두 번째 질문 때 어떻게 되는가? |
| 7 | chat_message와 chat_input | p12 | `chat_message`는 역할(user·assistant)별 말풍선, `chat_input`은 하단 입력창이고 Enter를 누르면 문자열을 돌려준다. 입력을 받으면 먼저 저장하고 말풍선으로 보여 준다 (p12) | `st.chat_input`이 값을 돌려주는 때는? |
| 8 | write_stream | p13 | 생성되는 글자를 차례로 보여 준다. 체감 대기 시간이 준다. 다 받은 답(`response`)을 assistant 메시지로 저장한다 (p13). **왜**: 1-2에서 본 스트리밍을 화면에 연결하는 곳 | `write_stream`이 끝난 뒤 session_state에 저장하는 값은? |
| 9 | 정리 퀴즈 | — | 재실행 · cache_resource · session_state · write_stream | 4지선다 3문항: ① 재실행 때 유지되는 것 ② cache_resource와 session_state의 쓰임 구분 ③ 한 번의 질문에서 일어나는 순서(저장 → user 말풍선 → 체인 호출 → 스트리밍 → 저장) |

강사용 메모(수강생 글에는 넣지 않음)
- p9 슬라이드 코드는 요약본이다. 실제 코드와 다르다: 상대 경로 `"./data/..."`, 텍스트 분할 없음, `create_rag_chain()` 함수. 실제 코드는 `Path(__file__)` 경로, `RecursiveCharacterTextSplitter(500, 75)`, `k=3` 검색, LCEL 체인이다.
- 원본 주석 "앱 시작 시 한 번만 실행"과 달리, `load_rag_chain()`은 **첫 질문 때** 처음 실행된다. 그래서 첫 답변만 느리다.

## 2. LAB 목차

Streamlit 앱은 노트북 커널에서 바로 돌릴 수 없다. 파일마다 `%%writefile <이름>.py` 한 셀로 파일을 쓰고 `!streamlit run <이름>.py` 셀로 띄운다(빌더 spec `"writefile"`). 그래서 파일 하나가 코드 셀 하나다. 제안 순서는 test → app이다(물어볼 것 2).

| 장 | 파일 | 구분 | CHANGE_HERE 후보 / WRITE_HERE로 쓸 TODO (원본 줄) | 성공 기준 초안 | 실행 제약 |
|---|---|---|---|---|---|
| 2 | test.py (재실행 확인) | 예제 + AI에게 물어보기 | CHANGE_HERE: `st.session_state.clicks +=1`(늘어나는 값) 또는 `st.button(' 클릭 ')`(버튼 글자). TODO는 없다 | 🟢 누를 때마다 숫자가 늘고 풍선이 뜬다. 🟢 바꾼 값만큼 숫자가 늘어난다. ⛔ 숫자가 1에서 더 오르지 않는다 | 서버가 떠 있는 동안 커널이 멈춘다. ■로 멈춘 뒤 다음 셀로 간다 |
| 2 | (AI에게 물어보기) | — | 힌트: "`clicks`를 session_state 대신 일반 변수로 두면 버튼을 여러 번 눌렀을 때 숫자가 어떻게 되는지, 이유와 함께 물어봅니다." 솔루션본 `test.py`가 바로 이 일반 변수 버전이라 비교 자료로 쓸 수 있다 | 🟢 "매번 0으로 다시 시작해 1에 머문다"와 그 이유(전체 재실행)를 설명한다. ⛔ "숫자가 계속 늘어난다"고 답한다 | — |
| 3 | app.py (보험 약관 QA 챗봇) | 과제 3 + 예제 1 | **과제** (LEC 6~8절에서 배움) | | 첫 질문 때 PDF 읽기·임베딩(약 50조각)·LLM 호출. 사내·사외 모두 가능 |
| | | 과제 ① | `# TODO: 사용자 메시지를 session_state에 저장해 주세요.` → 빈칸 `st.session_state.messages.append({'role': 'user', 'content': prompt})` | 🟢 두 번째 질문을 해도 첫 질문 말풍선이 남아 있다. ⛔ 새 질문을 하면 앞 질문이 사라진다 | |
| | | 과제 ② | `# TODO: RAG 체인의 stream() 결과를 Streamlit에 출력해 주세요.` → 빈칸 `response = st.write_stream(rag_chain.stream(prompt))` | 🟢 답변이 글자가 이어지며 나타나고 약관 내용을 근거로 답한다. ⛔ 답변 말풍선이 비어 있거나 `<generator object ...>`처럼 이상한 글자가 보인다 | 빈칸 상태에서도 오류 없이 빈 말풍선만 뜬다(아래 5절) |
| | | 과제 ③ | `# TODO: AI 응답을 session_state에 저장해 주세요.` → 빈칸 `st.session_state.messages.append({'role': 'assistant', 'content': response})` | 🟢 다음 질문 때 이전 AI 답변도 남아 있다. ⛔ 이전 답변이 사라지거나 `None`이 보인다 | |
| | | 예제 | CHANGE_HERE: `st.caption('메리츠 펫보험 약관을 기반으로 답변합니다.')` 또는 `st.title('보험 약관 QA 챗봇')`(LEC 4절) | 🟢 파일을 다시 쓰고 앱 화면에서 Rerun하면 바뀐 글자가 보인다. ⛔ 바뀌지 않는다(파일 쓰기 셀을 다시 실행하지 않음) | 파일을 다시 쓰면 앱이 "Source file changed"를 띄운다 |

- `search_kwargs={'k': 3}`나 `chunk_size=500`은 CHANGE_HERE로 쓰지 않는 것을 제안한다. `@st.cache_resource` 때문에 파일을 고쳐도 서버를 다시 띄우거나 캐시를 지워야 반영된다. 수강생이 "바꿨는데 그대로"를 겪는다. 쓴다면 이것을 LEC 5절의 확인 소재로 삼고 ⛔ 기준에 "서버를 다시 띄우지 않으면 그대로다"를 적어야 한다.
- 과제의 프롬프트 힌트 초안(각 3문장 이내)
  - ①: "질문 문자열 `prompt`를 역할 user와 함께 `st.session_state.messages`에 추가하는 한 줄을 요청합니다. 저장 형식은 위쪽 이전 대화 표시 코드가 읽는 모양(`role`, `content`)에 맞추라고 알려 줍니다."
  - ②: "`rag_chain.stream(prompt)`로 받은 조각을 Streamlit 화면에 차례로 그리고, 완성된 답을 변수 `response`에 담으라고 요청합니다."
  - ③: "②에서 받은 `response`를 역할 assistant로 `st.session_state.messages`에 추가하라고 요청합니다. ①과 같은 모양으로 저장하라고 알려 줍니다."

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽과 이유 |
|---|---|---|
| app.py | 코드는 같다. raw에만 TODO 3줄과 강사 말투 주석 7줄이 있다("결국 가우스 모델을 호출할건데 -> 함수 실행 결과에 불과 하겠죠", "한개의 runnable을 받았다", "runnable을 실행하는 방법 -> invoke, stream", "이 message를 토대로 LLM이 이전 대화를 기억한다거나 그런건 X" 등). 들여쓰기가 어긋난 주석은 ruff 정돈으로 맞춰진다 | **raw**. 과제 표시(TODO)가 raw에만 있다. 주석 처리는 물어볼 것 3 |
| test.py | raw는 `st.session_state.clicks`로 센다(누를수록 늘어남). 솔루션은 일반 변수 `clicks = 0`이다(재실행 때마다 0으로 돌아가 1에 머묾). `if` 줄은 주석 처리돼 있다 | **raw**. 제대로 동작하고 p5·p11 설명과 맞는다. 솔루션 쪽은 "일반 변수면 사라진다"(p11)를 보여 주는 대조 자료로 AI에게 물어보기의 정답 비교에 쓴다 |
| data/ | 같다 | — |

## 4. 실행 제약·위험과 처리 제안

1. **PDF 경로가 깨진다 (반드시 처리)**: `PDF_PATH = Path(__file__).parent / 'data' / 'meritz_pet_insurance.pdf'`. `%%writefile app.py`로 노트북 폴더에 쓰면 `lessons/Chapter01/data/meritz_pet_insurance.pdf`를 찾는데 그 파일이 없다. 첫 질문 때 채팅 화면에 파일 없음 오류가 난다(조용히 틀리지는 않음). 처리 방법은 물어볼 것 1.
2. **`config` import는 동작한다(확인함)**: `pyproject.toml`이 `src/config`를 패키지로 설치한다. `lessons/Chapter01`에서 `.venv` 파이썬으로 `import config`가 `src/config/__init__.py`를 찾았다. `load_dotenv()`는 스크립트 폴더에서 위로 올라가며 루트 `.env`를 찾으므로 문제없다(강의장 PC에서 `uv sync` 후 다시 확인).
3. **파일 쓰기 위치**: `lessons/Chapter01/app.py`, `test.py`는 Git 제외 대상이 아니다(`lessons/.gitignore`는 `work/`만 제외). 수강생 PC에서는 상관없지만 강사 저장소에 섞이지 않게 해야 한다. 물어볼 것 1과 함께 정한다.
4. **서버가 커널을 붙잡는다**: `!streamlit run` 셀은 멈출 때까지 끝나지 않는다. 그동안 다른 셀을 실행할 수 없다. test → app으로 넘어갈 때 ■로 멈춘다는 안내를 run_note에 넣는다. 멈추지 않고 두 번째 앱을 띄우면 포트가 8502로 바뀔 수 있다.
5. **`!streamlit` 명령 경로와 첫 실행 질문**: `!streamlit`은 셸 PATH에서 찾는다. 커널이 `.venv`여도 PATH에 없으면 "command not found"가 난다. `!{sys.executable} -m streamlit run app.py`가 안전하다. 강의장 PC에서 Streamlit을 처음 실행하면 이메일 입력을 묻고 멈출 수 있다. `--server.headless true`를 붙이면 묻지 않지만 브라우저가 자동으로 열리지 않아 주소를 눌러야 한다. 강의장에서 사전 확인한다.
6. **빈칸 상태가 조용히 돈다**: 빈칸 `...`은 올바른 파이썬이라 채우지 않아도 앱이 뜬다. 결과는 빈 답변 말풍선, 대화가 쌓이지 않음이다. 오류가 나지 않으므로 ⛔ 기준(빈 말풍선, 앞 대화 사라짐)을 반드시 보이게 적는다.
7. **캐시**: 위 2절 참고. 앱을 띄운 채 파일을 고치면 UI 코드는 Rerun으로 반영되지만 `load_rag_chain()` 안의 값은 반영되지 않는다.
8. **외부 호출·비용**: 서버를 새로 띄울 때마다 첫 질문에서 약 50조각을 임베딩한다(메모리 Chroma, 저장 안 함). 사외 openai면 소액 과금이 된다. 터미널 출력에 `langchain-community` 지원 종료 경고가 뜬다. 무시해도 된다고 안내한다.
9. input(), 실제 메일 발송, 사내 전용 API는 없다.

## 5. 커리큘럼 대조 (`docs/CURRICULUM.md` 2.3)

| 커리큘럼 항목 | 목차 위치 |
|---|---|
| Streamlit 소개 | LEC 2~3절 |
| [실습] LangChain을 활용한 보험 약관 QA 챗봇 UI 구현 | LEC 4~7절, LAB 3장 과제 ①③, 예제 |
| [실습] 스트리밍 응답 연결 | LEC 8절, LAB 3장 과제 ② |
| (Multi-Agent 항목) | 2-2 권에서 다룬다 |

## 6. 물어볼 것

1. **앱 파일과 약관 PDF를 어디에 둘까요?** (가) `lessons/Chapter01/data/`에 약관 PDF(2MB)를 복사하고 app.py를 노트북 폴더에 쓴다. 원본 코드는 그대로 둔다. (나) `%%writefile ../work/app.py`로 쓰고 PDF를 `lessons/work/data/`에 복사하는 준비 셀을 둔다. Git 제외 폴더라 저장소가 깨끗하다. (다) PDF_PATH 한 줄만 프로젝트의 원본 data 폴더를 가리키게 바꾼다. 원본 코드가 달라진다. 제안은 (나)입니다.
2. **LAB 순서를 test → app으로 해도 될까요?** 원본 파일 이름 순은 app → test입니다. test는 "누를 때마다 전체 재실행"(p5)과 session_state(p11)를 가장 작게 보여 주므로 먼저 두는 편이 이해하기 쉽습니다.
3. **app.py의 강사 말투 주석 7줄을 수강생 화면에 남길까요?** "LLM이 이전 대화를 기억하지는 않는다"는 쓸모가 있지만 "가우스 모델을 호출할건데 … 하겠죠" 같은 말투와 사내 모델 이름이 섞여 있습니다. 솔루션본은 이 주석이 없어 깔끔합니다. 제안: 솔루션 쪽 주석을 따르고, 기억하지 않는다는 내용은 LEC 6절 "왜"에만 둔다.
