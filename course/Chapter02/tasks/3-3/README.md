# 3-3 과제: 번역 Agent를 A2A로 띄우고 불러 보기

한국어 문장을 영어로 옮기는 Translator Agent를 A2A 서버로 만들고, 같은 파일의 클라이언트가 카드를 읽은 뒤 번역을 맡깁니다. 서버를 빈 포트에 잠깐 띄우고 끄는 코드는 `3-3_task.py` 맨 아래에 미리 들어 있습니다.

## 1. 학습 목표

1. `t.AgentCard`와 `t.AgentSkill`로 Agent Card를 만들 수 있다
2. `AgentExecutor`에서 Agent 결과를 `t.Message`로 `EventQueue`에 내보내는 서버를 Starlette 앱으로 조립할 수 있다
3. `A2ACardResolver`로 카드를 읽고 메시지를 보내 응답 텍스트를 출력할 수 있다

## 2. 준비

- VS Code에서 `course/Chapter02/tasks/3-3/3-3_task.py`를 엽니다. 고치는 파일은 이것 하나입니다.
- 참고할 코드: `course/Chapter02/notebooks/a2a_server.py`(서버)와 `3-3_a2a_LAB` 노트북의 클라이언트 셀(`call_researcher`)
- 노트북 실습의 8001 서버는 켜 두지 않아도 됩니다. 이 과제는 비어 있는 다른 포트를 씁니다.

## 3. 할 일

`# ✍️ 목표 N` 자리만 채웁니다. 맨 위 import·설정 줄과 맨 아래 "고치지 않습니다" 부분은 그대로 둡니다.

1. **목표 1** `agent_card`: 이름 `Translator Agent`, 한영 번역 Skill 하나, 주소는 미리 있는 `URL`을 쓴 카드를 만듭니다.
2. **목표 2** `app`: 받은 글을 `llm`으로 영어로 번역해 `t.Message`로 EventQueue에 내보내는 `AgentExecutor`를 만들고, RequestHandler와 카드 조회·JSON-RPC 라우트로 Starlette 앱을 조립합니다.
3. **목표 3** `call_translator`: `A2ACardResolver`로 카드를 읽어 이름과 스킬 이름을 출력하고, 받은 글을 메시지로 보내 응답 `parts`의 글을 출력합니다.

## 4. 프롬프트 힌트

- **목표 1**: `a2a_server.py`의 Agent Card를 참고해 이름·설명·Skill을 번역 Agent에 맞게 바꿔 달라고 합니다. 주소는 파일에 있는 `URL`을 쓰라고 말합니다.
- **목표 2**: `a2a_server.py`의 Executor와 앱 조립 부분을 참고하되, 안쪽은 그래프 없이 `llm`에 "영어로만 번역" 지시를 붙여 부르게 하라고 합니다. 결과를 `app` 변수에 담으라고 말합니다.
- **목표 3**: 노트북의 `call_researcher` 셀처럼 카드 읽기 → 트랜스포트 → 메시지 보내기 순서로 쓰되, 요청에는 파일의 `HEADERS`를 붙이라고 합니다. 받은 글은 반환하지 말고 바로 출력하라고 말합니다.

## 5. 실행

VS Code 메뉴 **터미널 → 새 터미널**을 열고(저장소 맨 위 폴더에서 열립니다) 실행합니다. 서버 터미널을 따로 켜지 않아도 명령 한 번으로 끝납니다.

```
uv run --env-file .env python course/Chapter02/tasks/3-3/3-3_task.py
```

다 되면 `[만든 카드]`, `[서버] … 띄웠습니다`, 카드에서 읽은 이름·스킬, 번역 결과, `[서버] 껐습니다` 순서로 나옵니다.

## 6. 채점받기

AI에게 **"3-3 과제 채점해 줘"**라고 말합니다.

## 7. 막히면

- 오류가 나면 마지막 줄만이 아니라 **오류 메시지 전체**를 복사해 AI에게 붙여 넣고 "원인을 쉬운 말로 설명하고 고쳐 줘"라고 합니다.
- 명령이 끝나지 않고 멈춰 있으면 Ctrl+C로 멈추고, 그 상황을 AI에게 그대로 알립니다.
