# 3-4 과제: 그래프 나누고 기억하기

LangGraph 심화 기능 네 가지를 아주 작은 그래프로 하나씩 만들어 봅니다. 그래프마다 노드는 한두 개면 됩니다.

## 1. 학습 목표

1. 따로 compile한 서브그래프를 부모 노드에서 호출해 결과를 부모 State로 넘길 수 있다
2. fan-out/fan-in으로 두 작업을 동시에 실행하고 `Annotated` 리듀서로 모을 수 있다
3. `MemorySaver`와 `thread_id`로 같은 thread는 이어 가고 다른 thread는 모르는 것을 `get_state` 메시지 수로 보일 수 있다
4. `InMemoryStore` namespace에 사용자 정보를 `put`하고 새 thread에서 `search`로 꺼내 쓸 수 있다

## 2. 준비

- VS Code에서 `course/Chapter02/tasks/3-4/3-4_task.py`를 엽니다. 고치는 파일은 이것 하나입니다.
- 맨 위의 설정 줄(`load_dotenv()`, `llm = get_llm()`)과 과제에 쓰는 값(`DOCUMENT`, `TOPIC`, `USER_ID`, `USER_INFO`)은 그대로 둡니다.
- `# ✍️ 목표 N` 주석 아래의 `(아직 작성하지 않았습니다)` 출력 줄을 AI가 만든 코드로 바꿉니다. `=== 목표 N ===` 제목 줄은 남겨 둡니다.

## 3. 할 일

1. **서브그래프**: 서브그래프 전용 State(`text`·`summary`)로 `DOCUMENT`를 한 문장으로 요약하는 `summary_subgraph`를 만들어 따로 compile합니다. 부모 그래프 `parent_graph`의 노드가 이 서브그래프를 `invoke`하고, 받은 요약을 부모 State의 `summary`로 돌려줍니다. 끝나면 부모 State의 `summary`를 출력합니다.
2. **fan-out/fan-in**: `TOPIC`의 장점 한 문장을 쓰는 `pros` 노드와 단점 한 문장을 쓰는 `cons` 노드를 START에서 동시에 시작하고, 둘 다 `merge` 노드로 모이게 합니다. 두 노드는 같은 키 `notes`에 한 줄씩 더하고(`장점: …`, `단점: …`), `notes`에는 목록을 이어 붙이는 `Annotated` 리듀서를 붙입니다. `merge`는 모이는 자리만 만들면 되므로 값을 바꾸지 않아도 됩니다. 그래프 그림(`draw_ascii()`)과 `notes`를 출력합니다.
3. **MemorySaver**: 대화 노드 하나짜리 `chat_graph`를 `MemorySaver`로 compile합니다. `thread_a`에서 "내 이름은 홍길동이야."와 "내 이름이 뭐야?"를, `thread_b`에서 "내 이름이 뭐야?"를 보낸 뒤, `get_state`로 thread마다 메시지 수를 출력합니다.
4. **Store**: `InMemoryStore`의 `("memories", USER_ID)` namespace에 `USER_INFO`를 `put`합니다(key는 `"profile"`, 값은 `{"fact": USER_INFO}`). 노드가 그 namespace를 `search`해 시스템 메시지에 넣는 `store_graph`를 `compile(checkpointer=MemorySaver(), store=store)`로 만들고, 처음 쓰는 thread `session_2`에서 "내 이름이랑 취미 알아?"를 실행합니다.

## 4. 프롬프트 힌트

1. 수업의 Subgraph 예제처럼 서브그래프와 부모 그래프의 State를 따로 두고, 부모 노드 함수 안에서 `summary_subgraph.invoke(...)`를 부르라고 적습니다. 노드는 바뀐 키만 dict로 돌려주라고 덧붙입니다.
2. `add_edge`로 START에서 두 갈래, 두 노드에서 `merge`로 한 갈래씩 잇게 하라고 적습니다. `notes`에 `Annotated[list[str], operator.add]`를 붙이고 각 노드는 한 줄짜리 목록을 돌려주라고 합니다.
3. 결과 메시지는 `results = chat_graph_result["messages"]`로 꺼내 `pretty_print()`하고, 메시지 수는 `chat_graph.get_state(config).values["messages"]`의 길이로 출력하라고 적습니다. 두 thread는 config의 `thread_id`만 다르게 하라고 합니다.
4. 기억은 모델 답에서 뽑지 말고 `store.put`으로 바로 넣으라고 적습니다. 노드는 `store.search(("memories", user_id))`로 꺼내 쓰고, 답 메시지는 `pretty_print()`, 끝에 `get_state`의 메시지 수와 Store의 내용을 출력하게 합니다.

## 5. 실행

저장소 맨 위 폴더에서 실행합니다. 모델을 일곱 번쯤 부르므로 수십 초 걸릴 수 있습니다.

```
uv run --env-file .env python course/Chapter02/tasks/3-4/3-4_task.py
```

## 6. 채점받기

AI에게 이렇게 말합니다.

> 3-4 과제 채점해 줘

## 7. 막히면

오류가 나면 마지막 줄만이 아니라 **오류 메시지 전체**를 AI에게 붙여 넣고 원인을 쉬운 말로 설명해 달라고 합니다.
