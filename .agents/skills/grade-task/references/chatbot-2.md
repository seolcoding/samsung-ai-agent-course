# 챗봇 2단계(1-3): 기억하고 도구 쓰는 챗봇

- 과제 파일: `course/Chapter01/chatbot/stage2.py` (화면은 `course/Chapter01/chatbot/ui.py`, 고치지 않는 파일)
- 확인 명령(저장소 맨 위에서, 화면 없이): `uv run --env-file .env python .agents/skills/grade-task/scripts/check_streamlit.py course/Chapter01/chatbot/stage2.py --stage 2`
  - "답 방식"을 대화 → 계산기 도구 → 정리 카드로 바꿔 가며 "내 이름은 민수야. 기억해 줘." → "내 이름이 뭐야?" → "1234 곱하기 5678은 얼마야?" → "재택근무의 장단점을 정리해 줘."를 보낸다. 💬는 채팅 메시지, 📂는 실행 기록 상자(`log_step`), `[제목] …` 줄은 앱이 터미널에 남긴 기록이다.
- 시작 상태: `chain = None`, `prompt`에 `MessagesPlaceholder`가 없고, `tool_answer`·`card_answer`가 "아직 … 않았습니다" 문장을 돌려준다. 네 자리가 모두 그대로면 채점하지 않는다. 일부만 했으면 한 목표씩 판정한다.

## 학습 목표와 확인 방법

1. `prompt | llm | StrOutputParser()` LCEL 체인으로 답할 수 있다
   - 확인: 코드에 `prompt | llm | StrOutputParser()`(같은 순서의 `|` 체인)가 있고 `chat_answer`가 그 체인의 `.stream(`으로 받은 조각을 `yield`한다. 확인 명령의 두 "대화" 질문에 assistant 💬 답이 있다. 체인을 만들어 두고 `chat_answer`는 여전히 `llm.stream(messages)`만 쓰면 ⛔(체인으로 답하지 않는다). `chain.invoke`로 받아 문자열을 돌려줘도 답이 나오면 🟢로 보되 1단계의 조각 보여 주기가 사라졌다고 한 줄 적는다
2. `MessagesPlaceholder("history")`에 이전 대화를 넣어 앞의 말을 기억하게 할 수 있다
   - 확인: `prompt`에 `MessagesPlaceholder("history")`(또는 `variable_name="history"`)가 system과 human 사이에 있고, 체인을 부를 때 `history`를 넣는다. 확인 명령에서 "내 이름이 뭐야?"의 `[모델에 보낸 메시지]`에 앞의 human·ai 메시지가 들어 있고, 답에 "민수"가 있다. 이름을 모른다고 답하거나 보낸 메시지에 앞 대화가 없으면 ⛔
3. `@tool`을 `bind_tools`로 연결하고 `tool_calls`를 실행해 `ToolMessage`로 돌려 최종 답을 받을 수 있다
   - 확인: 코드에 `@tool` 함수, `.bind_tools(`, `tool_calls`를 도는 코드, `ToolMessage(…, tool_call_id=…)`가 있다. 확인 명령의 계산 질문에서 `[도구 실행]` 기록에 도구 이름과 결과 7006652가 있고, assistant 💬 답에 7006652(쉼표가 있어도 됨)가 있다. 도구 실행 기록 없이 답만 맞으면 모델이 암산한 것이므로 ⛔. 도구 결과를 그대로 답으로 돌려주고 모델에 다시 보내지 않았으면(최종 답이 숫자만, ToolMessage 없음) ⛔
4. Pydantic 스키마로 답을 정해진 모양으로 받아 보여 줄 수 있다
   - 확인: 코드에 `BaseModel` 스키마(제목·요약·핵심 목록 칸)가 있고 `PydanticOutputParser`(또는 `with_structured_output`)로 받는다. 확인 명령의 `[받은 카드]`가 스키마 객체(예: `Card(title=…, summary=…, points=[…])`)이고, assistant 💬 답에 제목·요약·핵심 목록이 보인다. 모델에게 "이 형식으로 써 줘"라고 글로만 시키고 스키마 객체로 받지 않았으면 ⛔. 객체를 화면에 그대로(`Card(title=…)` 글자) 내보냈으면 🟢로 보되 마크다운으로 바꾸라고 다음 할 일에 적는다

## 확인 질문

"대화" 방식에서 "내 이름이 뭐야?"에 "민수"라고 답할 수 있었던 까닭은 무엇인가요?

1. `get_llm()`으로 만든 모델이 앞의 호출을 기억하기 때문
2. `StrOutputParser()`가 앞의 답을 저장해 두기 때문
3. Streamlit 화면에 앞의 대화가 보이기 때문
4. 앞의 대화(`history`)를 `MessagesPlaceholder` 자리에 넣어 이번 호출에 함께 보냈기 때문

정답: 4

해설:
- 1: 모델은 호출마다 받은 메시지만 봅니다. 앞의 호출을 스스로 기억하지 않습니다.
- 2: `StrOutputParser()`는 답 메시지에서 글자만 꺼냅니다. 아무것도 저장하지 않습니다.
- 3: 화면에 보이는 대화 기록은 사람을 위한 것입니다. 모델에게 보내지 않으면 모델은 모릅니다(시작본이 그랬습니다).
- 4: `[모델에 보낸 메시지]`에 앞의 human·ai 메시지가 함께 들어 있습니다. 그래서 모델이 이름을 압니다.
