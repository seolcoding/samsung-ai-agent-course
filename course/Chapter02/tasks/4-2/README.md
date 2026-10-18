# 4-2 과제: 기록과 점수가 남는 Agent

체인, 일반 함수, LangGraph 그래프의 실행을 Langfuse에 기록하고, 답변에 점수를 남깁니다. 실행 출력에 나온 trace ID로 Langfuse 화면에서 기록을 찾아봅니다.

## 1. 학습 목표

1. `CallbackHandler`를 config로 넘겨 체인 실행을 trace로 기록하고 trace ID를 출력할 수 있다
2. `@observe(name=...)`로 일반 함수를 한 trace 아래 중첩 span으로 기록할 수 있다
3. 규칙 점수와 LLM 채점 점수(0~1)를 `create_score`로 남기고 `flush()`할 수 있다
4. LangGraph 그래프에 `CallbackHandler`를 붙여 노드별 실행을 trace로 기록할 수 있다

## 2. 준비

- VS Code에서 `course/Chapter02/tasks/4-2/4-2_task.py`를 엽니다. 고치는 파일은 이것 하나입니다.
- 맨 위의 설정 줄(`truststore.inject_into_ssl()`, `load_dotenv()`, `langfuse = get_client()`, `llm = get_llm()`)과 미리 만들어 둔 `chain`, `get_weather` 도구는 그대로 둡니다.
- `=== 목표 N ===` 제목 줄은 그대로 두고, 그 아래 `# ✍️ 목표 N` 주석 아래의 안내 출력 줄을 AI가 만든 코드로 바꿉니다.
- `.env`에 Langfuse 키가 있어야 합니다. 저장소 맨 위에서 `uv run python -m config.check --langfuse`로 확인합니다.

## 3. 할 일

1. **체인 기록**: `CallbackHandler()`를 하나 만들어 `chain.invoke(..., config={"callbacks": [...]})`로 질문 하나를 실행합니다. 답과 `trace id: <ID>` 줄을 출력합니다.
2. **중첩 기록**: `@observe(name=...)`를 붙인 함수 두 개를 만듭니다. 바깥 함수는 안쪽 함수(참고 글을 돌려주는 간단한 함수)를 부른 뒤 그 글과 함께 `chain`을 실행합니다. 질문 하나로 실행하고 답과 `trace id: <ID>` 줄을 출력합니다.
3. **점수**: 목표 2의 trace에 규칙 점수 `short-answer`(답이 200자 이하면 1.0, 아니면 0.0)와 LLM 채점 점수 `llm-judge`(질문에 직접 답했는지 0.0~1.0)를 `langfuse.create_score`로 남기고, 두 점수를 출력합니다. 파일 맨 끝(`# ✍️ 목표 3 (마지막)`)에서 `langfuse.flush()`를 부릅니다.
4. **그래프 기록**: `get_weather`를 쓰는 agent → (`tools_condition`) → tools → agent 그래프 `weather_graph`를 만들고, 컴파일할 때 `CallbackHandler`를 붙입니다. "서울 날씨 알려줘"로 실행해 메시지를 `pretty_print()`로 출력하고, `trace id: <ID>` 줄을 출력합니다.

## 4. 프롬프트 힌트

1. 수업 코드처럼 `langfuse.langchain`의 `CallbackHandler`를 `config`의 `callbacks`로 넘기라고 합니다. 방금 실행한 trace ID는 핸들러의 `last_trace_id`로 꺼낼 수 있다고 알려 주고, `trace id: ` 뒤에 출력하게 합니다.
2. 수업의 `rag-pipeline` 예처럼 바깥 함수와 안쪽 함수에 각각 다른 이름으로 `@observe(name=...)`를 붙이라고 합니다. 바깥 함수 안의 `chain.invoke`에도 핸들러를 넘겨야 같은 trace에 묶인다는 점을 꼭 적습니다.
3. 목표 2에서 출력한 trace ID를 `create_score`의 `trace_id`로 쓰라고 합니다. LLM 채점은 "숫자 하나만 출력"하게 하는 채점용 체인을 따로 만들고, 숫자로 못 바꾸면 0.0으로 두게 합니다.
4. 수업의 LangGraph 방식(`StateGraph`, `ToolNode`, `tools_condition`, 노드는 바뀐 키만 dict로 반환)으로 짜고, `compile()` 뒤에 `with_config`로 핸들러를 붙이라고 합니다. 결과는 `results = weather_graph_result["messages"]`로 꺼내 하나씩 `pretty_print()`하게 합니다.

## 5. 실행

저장소 맨 위 폴더에서 실행합니다. 모델을 여러 번 부르므로 수십 초 걸릴 수 있습니다.

```
uv run --env-file .env python course/Chapter02/tasks/4-2/4-2_task.py
```

실행이 끝나면 Langfuse 화면의 **Tracing**에서 출력된 trace ID의 기록을 열어 봅니다. 목표 2의 기록에는 바깥 함수 아래 안쪽 함수와 체인이 매달려 있고, **Scores**에 점수 두 개가 보입니다. 기록은 몇 초 늦게 도착하니 새로고침합니다.

## 6. 채점받기

AI에게 이렇게 말합니다.

> 4-2 과제 채점해 줘

## 7. 막히면

오류가 나면 마지막 줄만이 아니라 **오류 메시지 전체**를 AI에게 붙여 넣고 원인을 쉬운 말로 설명해 달라고 합니다. `SSLError`나 `CERTIFICATE_VERIFY_FAILED`가 보이면 맨 위의 `truststore` 줄이 지워지지 않았는지 먼저 봅니다.
