# 3-1 과제: 약관 검색 도구 Agent

과정 1에서 배운 도구 호출·RAG·LangGraph를 한 프로그램에 모읍니다. 펫보험 약관을 찾아보는 도구를 만들고, Agent가 약관 질문에만 그 도구를 쓰게 합니다.

## 1. 학습 목표

1. `config.check`로 설정을 점검하고 ⛔ 항목을 고쳐 모델 호출까지 통과시킬 수 있다
2. `get_embeddings()`와 Chroma로 검색기를 만들고 `@tool search_policy`로 감쌀 수 있다
3. `tools_condition`과 `add_edge("tools", "agent")`로 도구를 반복해 호출하는 그래프를 만들 수 있다
4. 약관 질문에서만 도구를 호출하고 인사에는 호출하지 않는 것을 `pretty_print`로 보여 줄 수 있다

## 2. 준비

- VS Code에서 `course/Chapter02/tasks/3-1/3-1_task.py`를 엽니다. 고치는 파일은 이것 하나입니다.
- 맨 위의 설정 줄(`load_dotenv()`, `PDF_PATH`, `llm = get_llm()`, `embeddings = get_embeddings()`)은 그대로 둡니다.
- 약관 PDF는 노트북 폴더의 `data/meritz_pet_insurance.pdf`이고, `PDF_PATH`가 이미 가리킵니다.
- `# ✍️ 목표 N` 주석 아래의 안내 출력 줄을 AI가 만든 코드로 바꿉니다.

## 3. 할 일

1. **설정 점검**: `config.check`의 점검 함수로 LLM과 임베딩 설정을 보고, 모델·임베딩을 실제로 한 번씩 불러 봅니다. ⛔이 하나라도 있으면 프로그램이 거기서 멈추게 합니다. ⛔이 나오면 → 안내대로 `.env`를 고쳐 다시 실행합니다.
2. **검색 도구**: PDF를 읽어 청크로 나누고, `embeddings`로 Chroma 벡터 저장소를 만들어 조각 3개를 찾는 검색기로 바꿉니다. 이 검색기를 `@tool`을 붙인 `search_policy(query: str)` 함수로 감쌉니다.
3. **그래프**: `messages` 하나를 가진 State로 agent 노드(도구를 연결한 LLM)와 tools 노드를 만들고, agent → (`tools_condition`) → tools → agent로 잇습니다. 이름은 `policy_agent`로 합니다.
4. **두 질문 실행**: "반려동물 수술비도 보장되나요?"와 "안녕하세요, 자기소개를 한 줄로 해 주세요"를 차례로 실행하고, 결과를 `policy_agent_result`로 받아 메시지마다 `pretty_print()`로 출력합니다.

## 4. 프롬프트 힌트

1. `config.check`에 있는 점검 함수 이름과, 실제 호출까지 해 보는 옵션을 AI에게 물어보게 합니다. 임베딩도 함께 보게 하고, 결과가 실패면 `sys.exit`로 멈추라고 적습니다. 키 값은 출력하지 말라고 덧붙입니다.
2. 수업의 RAG 코드처럼 `PDFMinerLoader`, `RecursiveCharacterTextSplitter`, Chroma를 쓰라고 하고, 위에 있는 `PDF_PATH`와 `embeddings`를 그대로 쓰라고 적습니다. 도구의 docstring에 "언제 쓰는 도구인지"를 분명히 쓰라고 합니다.
3. 수업의 LangGraph 방식(`StateGraph`, `ToolNode`, `tools_condition`, 노드는 바뀐 키만 dict로 반환)으로 짜 달라고 합니다. tools 노드가 끝나면 agent로 돌아가야 한다는 점을 꼭 적습니다.
4. 질문 두 개를 반복문으로 실행하고, 결과는 `results = policy_agent_result["messages"]`로 꺼내 하나씩 `pretty_print()`하라고 적습니다. 질문마다 구분 줄을 먼저 출력하게 하면 보기 쉽습니다.

## 5. 실행

저장소 맨 위 폴더에서 실행합니다. 모델을 여러 번 부르므로 수십 초 걸릴 수 있습니다.

```
uv run --env-file .env python course/Chapter02/tasks/3-1/3-1_task.py
```

## 6. 채점받기

AI에게 이렇게 말합니다.

> 3-1 과제 채점해 줘

## 7. 막히면

오류가 나면 마지막 줄만이 아니라 **오류 메시지 전체**를 AI에게 붙여 넣고 원인을 쉬운 말로 설명해 달라고 합니다.
