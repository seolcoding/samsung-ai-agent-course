"""4-1 과제: 회의록 요약 스킬을 쓰는 Deep Agent"""

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# 아래에 AI와 함께 코드를 작성합니다
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

# 1. SKILL.md 쓰기: 과제 파일 옆 harness/task/skills/meeting-summary/SKILL.md
TASK_DIR = Path(__file__).parent / "harness" / "task"
skill_dir = TASK_DIR / "skills" / "meeting-summary"
skill_dir.mkdir(parents=True, exist_ok=True)
(skill_dir / "SKILL.md").write_text(
    """---
name: meeting-summary
description: 회의록 요약 스킬. 사용자가 회의록을 요약해 달라고 할 때 쓴다. 보고서 작성 요청에는 쓰지 않는다.
---

# meeting-summary

회의록을 요약할 때는 get_meeting_notes 도구로 회의록을 먼저 가져온 뒤, 아래 양식을 그대로 따른다.

```
[회의 요약]
■ 결정 사항
- (결정된 내용)
■ 할 일(담당자)
- (할 일) - (담당자)
```

- 첫 줄은 반드시 [회의 요약]이다.
- 회의록에 없는 내용은 지어내지 않는다.
""",
    encoding="utf-8",
)


# 2. 회의록 도구
@tool
def get_meeting_notes(meeting_name: str) -> str:
    """회의 이름으로 회의록을 가져온다."""
    return (
        f"[{meeting_name} 회의록]\n"
        "- 결정: 신규 사내 챗봇은 11월 첫 주에 시범 운영한다.\n"
        "- 할 일: 시범 운영 안내 메일 작성 (담당 김민수)\n"
        "- 할 일: 사용자 피드백 설문 준비 (담당 박지영)"
    )


# 3. Deep Agent 만들기
backend = FilesystemBackend(root_dir=str(TASK_DIR), virtual_mode=True)
agent = create_deep_agent(
    model=llm,
    tools=[get_meeting_notes],
    backend=backend,
    skills=["skills/"],
    system_prompt="회의록 요약만 돕는다. 코드 작성, 수학 계산 등 회의록 요약과 무관한 요청은 정중히 거절한다.",
    checkpointer=MemorySaver(),
)

# 4. 요청 두 개 실행
requests = [
    ("task_1", "주간 회의 회의록을 가져와서 요약해 줘."),
    ("task_2", "파이썬으로 피보나치 코드를 짜 줘."),
]
for thread_id, question in requests:
    print(f"\n=== {question} ===")
    deep_agent_result = agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    results = deep_agent_result["messages"]
    for m in results:
        m.pretty_print()
