# 1-2 과제: requests와 SDK로 LLM 부르기

같은 질문을 두 가지 방법으로 보내고 답을 꺼냅니다. 챗봇 1단계(`course/Chapter01/chatbot/README.md`)는 이 과제 다음에 합니다.

## 1. 학습 목표

1. `requests`로 HTTP 요청을 직접 보내 LLM 답(`choices[0].message.content`)을 꺼낼 수 있다
2. SDK(`client.responses.create`)로 developer·user 메시지를 보내 `output_text`로 답을 받을 수 있다

## 2. 준비

VS Code 탐색기에서 `course/Chapter01/tasks/1-2/1-2_task.py`를 엽니다. 맨 위 설정 부분(주소·헤더·`client`·`PAYLOAD_EXTRA`)은 이미 준비되어 있으니 그대로 둡니다. `# ✍️ 목표` 주석 아래 두 자리만 채웁니다.

## 3. 할 일

1. **목표 1**: `requests.post`로 `{api_base_url}/chat/completions`에 질문(`QUESTION`)을 user 메시지로 보냅니다. 응답 JSON에서 `choices[0].message.content`를 꺼내 출력합니다.
2. **목표 2**: `client.responses.create`로 developer 메시지("친절한 IT 헬프데스크 상담원, 두 문장 이내로 답")와 user 메시지(`QUESTION`)를 보냅니다. `output_text`를 출력합니다.

`(아직 작성하지 않았습니다)` 줄은 채운 코드로 바꿉니다.

## 4. 프롬프트 힌트

- **목표 1**: 이미 있는 변수(`api_base_url`, `headers`, `model`, `PAYLOAD_EXTRA`, `QUESTION`)를 그대로 쓰라고 AI에게 알려 줍니다. 요청 JSON에 무엇을 넣고, 응답에서 어느 경로로 답을 꺼낼지 직접 적어 줍니다.
- **목표 2**: 노트북에서 본 SDK 방식(`client.responses.create`, `input`에 역할이 있는 메시지 목록)을 쓰라고 적습니다. developer 메시지에 넣을 역할과 답 길이도 정해 줍니다.

## 5. 실행

저장소 맨 위 폴더의 터미널에서 실행합니다.

```
uv run --env-file .env python course/Chapter01/tasks/1-2/1-2_task.py
```

`=== 1. requests로 직접 보내기 ===`와 `=== 2. SDK로 보내기 ===` 아래에 각각 답이 나오면 됩니다.

## 6. 채점받기

AI에게 **"1-2 과제 채점해 줘"**라고 말합니다. 학습 목표마다 🟢 통과 / ⛔ 수정 필요 / ❔ 확인 불가와 다음 할 일이 나옵니다.

## 7. 막히면

오류가 나면 마지막 줄만이 아니라 **오류 메시지 전체**를 복사해 AI에게 붙여 넣고, 원인과 고칠 곳을 물어봅니다.
