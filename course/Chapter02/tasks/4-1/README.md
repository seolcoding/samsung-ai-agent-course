# 4-1 과제: 회의록 요약 스킬을 쓰는 Deep Agent

## 학습 목표

1. `@tool` 도구와 시스템 프롬프트를 `create_deep_agent`에 묶어 Agent를 만들 수 있다
2. 머리말(`name`·`description`)과 양식 본문이 있는 SKILL.md를 쓰고 skills 폴더로 연결해 그 양식대로 답하게 할 수 있다
3. `system_prompt`로 범위 밖 요청을 거절시키고 두 요청의 결과를 비교할 수 있다
4. 코드·모델은 그대로 두고 SKILL.md 한 줄만 바꿔 출력이 달라지는 것을 전후 비교로 보일 수 있다

## 준비

VS Code 탐색기에서 이 폴더의 두 파일을 엽니다. 이 과제는 **두 파일을 고칩니다.**

- `course/Chapter02/tasks/4-1/4-1_task.py`: Agent를 만들고 실행하는 파일
- `course/Chapter02/tasks/4-1/skills/meeting-summary/SKILL.md`: Agent가 읽을 스킬

`4-1_task.py`의 맨 위 설정 줄, `REQUEST_1`·`REQUEST_2`, `copy_skills_with_one_line_changed` 함수는 그대로 둡니다. 스킬 폴더 이름(`meeting-summary`)도 바꾸지 않습니다.

## 할 일

`# ✍️ 목표 N` 자리를 채웁니다.

1. **목표 1** `@tool`로 회의록 도구 `get_meeting_notes`를 만듭니다. 회의 이름을 받아 정해 둔 회의록 글(결정 사항 1개, 담당자 이름이 있는 할 일 2개)을 돌려줍니다. 작업 공간 폴더를 받아 `create_deep_agent`로 Agent를 만들어 돌려주는 함수 `build_agent(root_dir)`를 만들고, `agent = build_agent(TASK_DIR)`로 Agent를 만듭니다.
2. **목표 2** SKILL.md의 `description`에 언제 쓰는지 적고, 본문에 양식을 적습니다. 답의 첫 줄은 `[회의 요약]`, 그 아래 `결정 사항`과 `할 일(담당자)` 두 칸입니다. `build_agent`의 `skills`로 이 스킬을 연결하고, `REQUEST_1`을 실행해 메시지를 `pretty_print()`로 출력합니다.
3. **목표 3** `build_agent`의 `system_prompt`에 회의록 요약 밖의 요청은 거절하라고 적습니다. `REQUEST_2`를 다른 `thread_id`로 실행해 출력하고, 두 요청의 마지막 답을 `=== 요청 1과 요청 2 비교 ===` 아래에 나란히 출력합니다.
4. **목표 4** SKILL.md에서 출력에 드러나는 줄 하나를 골라 `copy_skills_with_one_line_changed(바꿀 줄, 새 줄)`로 사본을 만듭니다. 같은 `build_agent`에 사본 폴더를 넣어 Agent를 만들고 `REQUEST_1`을 다시 실행합니다. 바꾸기 전(목표 2)과 후의 마지막 답을 `=== SKILL.md 한 줄 전후 비교 ===` 아래에 나란히 출력합니다.

## 프롬프트 힌트

1. **목표 1** 노트북 3장의 `create_deep_agent`처럼 `model=llm`, 도구, `FilesystemBackend(virtual_mode=True)`, `skills`, `system_prompt`, `MemorySaver()`를 넣어 달라고 합니다. 작업 공간 폴더만 인자로 받는 함수로 만들어 달라고 해야 목표 4에서 그대로 다시 쓸 수 있습니다.
2. **목표 2** SKILL.md는 AI에게 시키지 말고 직접 써 봅니다. Agent는 처음에 `description`만 보고 파일을 읽을지 정하므로, 어떤 요청에 쓰는지 분명히 적습니다. 연결할 때 `skills`에는 스킬 하나의 폴더가 아니라 스킬 폴더들을 담은 상위 폴더를 넣는다고 AI에게 알려 줍니다.
3. **목표 3** 무엇을 돕고 무엇을 거절할지를 시스템 프롬프트 한두 문장으로 정해 알려 줍니다. 두 요청은 대화가 섞이지 않게 서로 다른 `thread_id`로 실행해 달라고 합니다.
4. **목표 4** 바꿀 줄은 SKILL.md에 한 번만 나오고 답에 그대로 보이는 줄(예: 양식의 첫 줄)로 직접 정해 AI에게 알려 주고, 파일 안의 `copy_skills_with_one_line_changed`를 쓰라고 합니다. 코드·모델·시스템 프롬프트는 그대로 두고 작업 공간 폴더만 바꿔 같은 요청을 보내 달라고 합니다.

## 실행

VS Code 메뉴 **터미널 → 새 터미널**을 열고(저장소 맨 위 폴더에서 열립니다) 아래 명령으로 실행합니다. Agent를 세 번 실행하므로 수십 초 걸립니다.

```
uv run --env-file .env python course/Chapter02/tasks/4-1/4-1_task.py
```

## 채점받기

다 됐으면 AI에게 **"4-1 과제 채점해 줘"**라고 말합니다. 학습 목표마다 🟢 통과 / ⛔ 수정 필요 / ❔ 확인 불가와 다음 할 일이 나옵니다.

## 막히면

오류가 나면 마지막 줄만이 아니라 **오류 메시지 전체**를 복사해 AI에게 붙여 넣고, 원인부터 쉬운 말로 설명해 달라고 합니다.
