# 챗봇 1단계(1-2): LangChain으로 부르고 답을 조각으로 보여 주기

- 과제 파일: `course/Chapter01/chatbot/stage1.py` (화면은 `course/Chapter01/chatbot/ui.py`, 고치지 않는 파일)
- 확인 명령(저장소 맨 위에서, 화면 없이): `uv run --env-file .env python .agents/skills/grade-task/scripts/check_streamlit.py course/Chapter01/chatbot/stage1.py --stage 1`
  - 사이드바 "답 말투"를 "한 문장으로"로 바꾸고 "LLM이 뭐야?"를 보낸다. 💬는 채팅 메시지, 📂는 실행 기록 상자(`log_step`), `[제목] …` 줄은 앱이 터미널에 남긴 기록이다.
- 시작 상태: `prompt = None`이고 `answer`가 "아직 답하는 코드가 없습니다…"를 돌려준다. 이 문장이 답으로 나오면 채점하지 않고 README대로 먼저 작성하라고 안내한다.
- 목표 1·2(requests, SDK)는 터미널 과제 `references/1-2.md`에서 채점한다.

## 학습 목표와 확인 방법

1. (목표 3) LangChain(`get_llm()`)으로 호출하고 `stream()`으로 답을 조각 단위로 화면에 보여 줄 수 있다
   - 확인: 코드의 `answer`에 `llm.stream(`이 있고 조각의 `content`를 `yield`한다(`ui.py`가 제너레이터를 `st.write_stream`으로 보여 준다). 확인 명령 출력에 assistant 💬 답 문장이 있고, `[받은 조각 수]`가 2 이상이다. `llm.invoke(`로 한 번에 받아 문자열을 돌려주거나, 조각을 모두 모은 뒤 한 번에 `return`하면 답이 나와도 ⛔(조각 단위로 보여 주지 않는다). `get_llm()` 대신 다른 모델·SDK를 만들었으면 ⛔
2. (목표 4) system·user를 나눈 `ChatPromptTemplate`에 변수를 넣어 호출할 수 있다
   - 확인: 코드에 `ChatPromptTemplate.from_messages`가 있고 `system` 메시지와 `human`(또는 `user`) 메시지가 따로 있으며, 사이드바의 `style`과 `question`을 변수로 넣는다(`prompt.invoke({...})`, `format_messages(...)` 또는 `prompt | llm` 모두 됨). 확인 명령 출력의 `[모델에 보낸 메시지]`에 system 메시지와 human 메시지가 따로 있고 system 쪽에 "한 문장으로"가 들어 있다. 질문을 f-string으로 한 문자열에 이어 붙였거나, system 메시지가 없거나, 고른 말투가 메시지에 없으면 ⛔. `[모델에 보낸 메시지]` 기록이 없으면 코드로만 판정하되 다음 할 일에 `log_step`을 넣으라고 적는다

## 확인 질문

`answer`가 `return llm.invoke(messages).content` 대신 `for chunk in llm.stream(messages): yield chunk.content`로 답하면 화면에서 무엇이 달라지나요?

1. 답이 다 만들어진 뒤 한 번에 나타나는 대신, 만들어지는 대로 글자 조각이 이어서 나타난다
2. 모델이 앞의 대화를 기억하게 된다
3. 답이 더 정확해진다
4. 답이 터미널에만 나오고 화면에는 나오지 않는다

정답: 1

해설:
- 1: `stream()`은 모델이 만드는 조각을 바로바로 보내 주고, `ui.py`의 `st.write_stream`이 받는 대로 이어 붙여 보여 줍니다. 기다리는 느낌이 줄어듭니다.
- 2: 기억은 앞의 대화를 메시지에 다시 넣어야 생깁니다(2단계). 받는 방식과는 관계가 없습니다.
- 3: 같은 모델, 같은 메시지이므로 답의 내용은 달라지지 않습니다. 받는 방식만 다릅니다.
- 4: `st.write_stream`이 화면에 보여 줍니다. 터미널에는 `log_step`으로 남긴 기록만 나옵니다.
