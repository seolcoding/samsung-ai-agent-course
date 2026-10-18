# 3-2 과제: MCP 서버를 직접 띄우는 Agent

## 학습 목표

1. FastMCP `@mcp.tool()`로 함수 2개를 MCP 도구로 등록할 수 있다
2. `MultiServerMCPClient`를 stdio로 연결해 `get_tools()`로 도구 목록을 받을 수 있다
3. 받은 MCP 도구를 LangGraph Agent에 붙여 질문에 도구로 답하게 할 수 있다
4. `@mcp.resource()`와 `@mcp.prompt()`를 정의하고 읽어 올 수 있다

## 준비

VS Code 탐색기에서 `course/Chapter02/tasks/3-2/3-2_task.py`를 엽니다. 이 파일 하나가 MCP 서버이자 클라이언트입니다. 클라이언트가 이 파일을 `--server`로 다시 실행해 서버로 쓰므로(stdio 방식), 서버 터미널을 따로 켜지 않습니다. 맨 위 설정 줄과 맨 아래 `if __name__ == "__main__":` 부분은 그대로 둡니다.

## 할 일

`# ✍️ 목표 N` 주석 자리를 채웁니다.

1. **목표 1** 서버에 `@mcp.tool()`로 도구 2개를 등록합니다. 용어 사전 찾기(용어를 받아 `GLOSSARY`에서 뜻을 돌려줌)와 글자 수 세기(공백 포함)입니다.
2. **목표 2** `main()`에서 `MultiServerMCPClient`를 stdio로 이 파일에 연결하고, `get_tools()`로 받은 도구의 이름과 설명을 `=== 사용 가능한 MCP 도구 ===` 아래에 출력합니다.
3. **목표 3** 받은 도구로 agent → tools → agent 그래프를 만들고 두 질문 `MCP가 무슨 뜻이야? 사전에서 찾아 줘.`, `'에이전트 개발 교육'은 몇 글자야?`를 실행합니다. 결과는 `mcp_graph_result["messages"]`를 `results`로 꺼내 `pretty_print()`로 출력합니다.
4. **목표 4** 서버에 `@mcp.resource("glossary://terms")`(사전에 있는 용어 목록)와 `@mcp.prompt()`(용어를 받아 "쉽게 설명해 달라"는 질문을 만드는 템플릿)를 정의합니다. `main()`에서 그 Resource와 Prompt(용어 `RAG`)를 읽어 `=== Resource ===`, `=== Prompt ===` 아래에 출력합니다.

## 프롬프트 힌트

1. **목표 1** 파일의 `GLOSSARY`와 목표 1 주석을 가리키며, 노트북 서버 코드처럼 `@mcp.tool()` 함수 2개를 만들어 달라고 합니다. 도구 설명(docstring)을 한국어로 넣어 달라고 하고, 서버 쪽에는 `print()`를 넣지 말라고 덧붙입니다.
2. **목표 2** 서버 프로그램은 지금 실행 중인 파이썬(`sys.executable`)으로 이 파일을 `--server`와 함께 띄우는 stdio 설정이라고 알려 줍니다. 포트·SSE는 쓰지 말라고 하고, 도구 목록을 이름과 설명으로 출력해 달라고 합니다.
3. **목표 3** 노트북 3장처럼 `bind_tools`, `ToolNode`, `tools_condition`으로 그래프를 만들어 달라고 합니다. 결과를 `pretty_print()`로 보여 달라고 해야 도구 호출(`Tool Message`)까지 보입니다.
4. **목표 4** Resource 주소와 Prompt가 할 일을 정해서 알려 주고, 클라이언트에서는 `get_tools()`와 같은 client로 Resource와 Prompt를 읽어 내용을 출력해 달라고 합니다. Resource와 Prompt는 도구 목록에 나오지 않는다는 점도 확인해 달라고 합니다.

## 실행

VS Code 메뉴 **터미널 → 새 터미널**을 열고(저장소 맨 위 폴더에서 열립니다) 아래 명령으로 실행합니다. 서버도 이 명령 안에서 잠깐 떴다가 함께 꺼집니다.

```
uv run --env-file .env python course/Chapter02/tasks/3-2/3-2_task.py
```

## 채점받기

다 됐으면 AI에게 **"3-2 과제 채점해 줘"**라고 말합니다. 학습 목표마다 🟢 통과 / ⛔ 수정 필요 / ❔ 확인 불가와 다음 할 일이 나옵니다.

## 막히면

오류가 나면 마지막 줄만이 아니라 **오류 메시지 전체**를 복사해 AI에게 붙여 넣고, 원인부터 쉬운 말로 설명해 달라고 합니다.
