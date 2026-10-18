# 챗봇 3단계(1-4): 약관 RAG 챗봇

- 과제 파일: `course/Chapter01/chatbot/stage3.py` (화면은 `course/Chapter01/chatbot/ui.py`, 고치지 않는 파일)
- 확인 명령(저장소 맨 위에서, 화면 없이): `uv run --env-file .env python .agents/skills/grade-task/scripts/check_streamlit.py course/Chapter01/chatbot/stage3.py --stage 3`
  - "답 방식"을 "약관 질문", "검색 방식"을 "로컬 Chroma"로 두고 "반려견이 수술을 받으면 수술비도 보장되나요?" → "삼성전자의 오늘 주가는 얼마야?"를 보낸 뒤, "검색 방식"을 "사내 RAGaaS"로 바꿔 첫 질문을 다시 보낸다. 💬는 채팅 메시지, 📂는 실행 기록 상자(`log_step`), `[제목] …` 줄은 앱이 터미널에 남긴 기록이다. 첫 임베딩 때문에 1분쯤 걸릴 수 있다.
  - 출력에 약관 PDF 글이 섞여 `grep`이 바이너리로 볼 수 있다. 출력을 거르지 말고 그대로 읽는다.
- 시작 상태: `search`가 빈 목록을, `rag_answer`가 "아직 약관 검색을 만들지 않았습니다…"를 돌려준다. 그대로면 채점하지 않는다.
- 사내/사외: `uv run python -m config.check --json`의 `실행 환경(COURSE_ENV)`이 `out`(사외)이면 RAGaaS는 모의 응답(`[MOCK RAGaaS] …`)을 준다.

## 학습 목표와 확인 방법

1. PDF 읽기·분할·`get_embeddings()`·Chroma 저장을 `@st.cache_resource`로 한 번만 만들 수 있다
   - 확인: 코드에 `@st.cache_resource`가 붙은 함수 안에 PDF 읽기(`PDFMinerLoader` 등), `RecursiveCharacterTextSplitter`, `get_embeddings()`, `Chroma.from_documents`가 있다. 확인 명령 출력에서 `[벡터 저장소] 청크 N개 저장`(N은 수십 개) 줄이 로컬 Chroma 질문 두 번에 걸쳐 **한 번만** 나온다. 두 번 나오면 질문마다 다시 만드는 것이므로 ⛔. 그 줄이 없으면 코드로 판정하되 다음 할 일에 `print`를 넣으라고 적는다. `get_embeddings()` 대신 다른 임베딩 클래스를 직접 만들었으면 ⛔
2. `as_retriever(search_kwargs={"k": 3})`로 찾은 청크를 context로 넣어 답하고 근거를 보여 줄 수 있다
   - 확인: 코드에 `as_retriever(search_kwargs={"k": 3})`가 있고, 찾은 글을 합쳐 프롬프트의 `{context}`에 넣는다. 확인 명령의 수술비 질문(로컬 Chroma)에서 📂 근거 상자가 있고 제목이나 내용으로 3개임을 알 수 있으며, assistant 💬 답이 근거의 내용(수술, 입원의료비, 보상한도 등)으로 답한다. 근거 상자가 없거나, context를 넣지 않고 질문만 보냈으면 ⛔
3. 맥락에 없는 질문에는 "문서에서 확인할 수 없습니다"라고 답하게 할 수 있다
   - 확인: 프롬프트 system 메시지에 context만 근거로 하라는 말과 "문서에서 확인할 수 없습니다" 문구가 있다. 확인 명령의 주가 질문에 대한 assistant 💬 답에 "문서에서 확인할 수 없습니다"가 있다(문장 부호·존댓말 차이는 괜찮다). 주가를 지어내거나 일반 지식으로 답하면 ⛔
4. 검색 방식(로컬 Chroma / 사내 RAGaaS)을 골라 두 검색 결과를 비교할 수 있다(사내망)
   - 확인: 코드의 `search`가 "검색 방식" 값에 따라 갈라지고, RAGaaS 쪽은 `post_ragaas("retrieve-rrf", …)`를 부르며 `["hits"]["hits"]`의 `_source.merge_title_content`를 꺼낸다(`requests.post`로 직접 부르거나 주소·키를 코드에 쓰면 ⛔). 확인 명령의 마지막 질문에 `근거 (사내 RAGaaS …)` 상자가 있다.
     - 사내(`COURSE_ENV=samsung`): 근거에 실제 약관 글이 있고 답이 그 글로 답하면 🟢.
     - 사외(`out`): 근거가 `[MOCK RAGaaS]`이면 코드 경로는 맞지만 실제 비교는 할 수 없으므로 ❔로 두고, "사외라 모의 응답만 확인했습니다. 사내망에서 다시 확인합니다"라고 적는다. 근거 상자 자체가 없거나 오류가 나면 ⛔

## 확인 질문

Streamlit 앱에서 벡터 저장소를 만드는 함수에 `@st.cache_resource`를 붙이는 까닭은 무엇인가요?

1. 검색 결과가 더 정확해지기 때문
2. Streamlit은 질문(입력)마다 파일 전체를 다시 실행하므로, 붙이지 않으면 질문할 때마다 PDF를 읽고 임베딩을 다시 하기 때문
3. 붙이지 않으면 Chroma를 만들 수 없기 때문
4. 대화 기록이 화면에서 사라지지 않게 하기 때문

정답: 2

해설:
- 1: 캐시는 같은 결과를 다시 쓰는 것뿐입니다. 검색 결과는 같습니다.
- 2: 캐시가 없으면 질문마다 "청크 N개 저장"이 다시 찍히고 임베딩 비용과 시간이 그만큼 듭니다. 붙이면 처음 한 번만 만들고 다음부터는 만든 것을 꺼내 씁니다.
- 3: 캐시 없이도 Chroma는 만들어집니다. 다만 질문마다 새로 만듭니다.
- 4: 대화 기록은 `ui.py`가 `st.session_state`에 둡니다. `@st.cache_resource`와는 관계가 없습니다.
