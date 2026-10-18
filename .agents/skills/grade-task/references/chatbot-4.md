# 챗봇 4단계(2-1): LangGraph 에이전트 챗봇

- 과제 파일: `course/Chapter01/chatbot/stage4.py` (화면은 `course/Chapter01/chatbot/ui.py`, 고치지 않는 파일)
- 확인 명령(저장소 맨 위에서, 화면 없이): `uv run --env-file .env python .agents/skills/grade-task/scripts/check_streamlit.py course/Chapter01/chatbot/stage4.py --stage 4`
  - "답 방식"을 "에이전트"로 두고 ① "안녕! 내 이름은 민수야." ② "반려견이 수술을 받으면 수술비도 보장되나요?" ③ "내 이름이 뭐야?"를 보낸다. 이어서 "도구 실행 전 승인 받기"를 켜고 ④ "반려견 입원비도 보장되나요?" → "승인" 버튼, ⑤ "반려견 통원 치료비도 보장되나요?" → "거부" 버튼, 마지막으로 "대화 지우기" 뒤 ⑥ "내 이름이 뭐야?"를 보낸다. 💬는 채팅 메시지, 📂는 실행 기록 상자, 🔘는 화면 버튼, `[노드 순서] …`·`[도구 결과] …`는 앱이 터미널에 남긴 기록이다. 1~2분 걸릴 수 있다.
  - 출력에 약관 PDF 글이 섞여 `grep`이 바이너리로 볼 수 있다. 출력을 거르지 말고 그대로 읽는다.
- 시작 상태: `agent_graph = None`이고 `agent_answer`가 "아직 에이전트를 만들지 않았습니다…"를 돌려준다. 그대로면 채점하지 않는다. `run_graph`·`approval_buttons`는 처음부터 있던 코드라 채점 대상이 아니다(고쳤으면 원래대로 두라고 안내한다).

## 학습 목표와 확인 방법

1. `StateGraph`에 agent 노드와 `ToolNode`를 넣고 `Literal` 반환 갈림길 함수로 conditional edge를 이어 compile할 수 있다
   - 확인: 코드에 `StateGraph(`, `add_node("agent", …)`, `add_node("tools", ToolNode(…))`, `add_conditional_edges("agent", <갈림길 함수>)`, `add_edge("tools", "agent")`, `.compile(`이 있고, 갈림길 함수의 반환 타입이 `Literal[...]`이다(`tools_condition`을 그대로 쓰거나 반환 타입이 없으면 ⛔). 노드는 바뀐 키만 dict로 돌려준다(`{"messages": [...]}`). 확인 명령 ①의 `[노드 순서]`가 `agent`이고 답이 나온다. `create_agent`로 대신 만들었으면 ⛔
2. 약관 검색을 `@tool search_policy`로 바꿔 약관 질문에서만 tools 노드를 거치게 할 수 있다
   - 확인: 코드에 `@tool`이 붙은 `search_policy`가 있고 3단계의 `search`(또는 retriever)로 약관 글을 돌려준다. 확인 명령 ①·③(인사·이름)의 `[노드 순서]`는 `agent`만, ②(약관)는 `agent → tools → agent`이고 `[도구 결과]`에 약관 글이 있으며 답이 그 내용(수술, 입원의료비, 보상한도 등)으로 답한다. 인사에도 tools를 거치거나 약관 질문에 tools를 거치지 않으면 ⛔
3. `MemorySaver`와 `thread_id`로 대화 기억을 그래프에 맡길 수 있다
   - 확인: 코드에서 `MemorySaver()`를 `@st.cache_resource` 함수(또는 `st.session_state`)로 한 번만 만들어 `compile(checkpointer=…)`에 주고, config에 `st.session_state.thread_id`를 넣으며, 그래프에는 이번 질문 하나만 넣는다(`history`를 메시지로 넣으면 ⛔: 기억을 그래프에 맡긴 것이 아니다). 확인 명령 ③의 답에 "민수"가 있고, "대화 지우기" 뒤 ⑥에서는 이름을 모른다고 답한다. ③에서 이름을 모르면 ⛔(질문마다 `MemorySaver()`를 새로 만들면 이렇게 된다). ⑥에서도 "민수"라고 하면 ⛔(thread_id를 고정값으로 썼다)
4. `interrupt_before`로 도구 실행 전에 멈추고 승인·거부로 재개할 수 있다
   - 확인: 코드의 compile에 토글 값에 따라 `interrupt_before=["tools"]`가 들어가고, `resume`이 승인이면 `None`으로 이어 가며(`run_graph(None, config)` 또는 `invoke(None, config)`), 거부면 대기 중인 `tool_calls`마다 `ToolMessage(…, tool_call_id=…)`를 만들어 `update_state(config, …, as_node="tools")`로 넣은 뒤 이어 간다. 확인 명령 ④에서 답이 "⏸ 도구를 실행하기 전에 승인이 필요합니다…"이고 🔘에 승인·거부가 있으며, "승인" 뒤 `[노드 순서] tools → agent`와 약관 답이 나온다. ⑤에서 "거부" 뒤 `[도구 결과]` 없이 `[노드 순서] agent`로 끝난다. ④에서 버튼이 나오지 않거나(`'승인' 버튼을 찾지 못함`), 거부 뒤에 `[도구 결과]`가 찍히면(거부했는데 도구가 실행됨) ⛔

## 확인 질문

4단계에서 `answer`가 `history`를 쓰지 않고 이번 질문 하나만 그래프에 넣는데도 "내 이름이 뭐야?"에 답할 수 있었던 까닭은 무엇인가요?

1. Streamlit 화면이 앞의 대화를 모델에게 보내 주기 때문
2. `ToolNode`가 앞의 질문을 저장해 두기 때문
3. checkpointer(`MemorySaver`)가 같은 `thread_id`의 State(메시지 목록)를 저장해 두고, 다음 실행 때 그 뒤에 새 질문을 이어 붙이기 때문
4. 갈림길 함수의 반환 타입을 `Literal`로 달았기 때문

정답: 3

해설:
- 1: 화면의 대화 기록(`st.session_state.messages`)은 4단계 그래프에 넣지 않습니다.
- 2: `ToolNode`는 도구 호출을 실행할 뿐 대화를 저장하지 않습니다.
- 3: 같은 `thread_id`로 부르면 저장해 둔 메시지에 새 질문이 더해집니다. "대화 지우기"가 `thread_id`를 새로 만들면 빈 기록에서 다시 시작합니다.
- 4: `Literal`은 그래프 그림에 갈래를 보이게 하고 갈 곳을 분명히 할 뿐, 기억과는 관계가 없습니다.
