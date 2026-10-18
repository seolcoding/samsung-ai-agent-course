"""4-1 과제 · 회의록 요약 스킬을 쓰는 Deep Agent

✍️ 할 곳  코드의 `# ✍️` 표시 2곳만 채웁니다 (`# ✨` 줄은 AI에게 말할 힌트)
▶️ 실행   uv run --env-file .env python course/Chapter02/tasks/4-1_task.py
✅ 확인   실행하면 맨 끝에 🟢/⛔가 나옵니다
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""

from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from config.llm import get_llm

load_dotenv()
llm = get_llm()

TASK_DIR = Path(__file__).resolve().parent  # Agent의 작업 공간. 스킬은 그 안의 4-1_skills/ 아래에 있습니다
SKILL_MD = TASK_DIR / "4-1_skills" / "meeting-summary" / "SKILL.md"
SYSTEM_PROMPT = "회의록 요약만 돕는다. 회의록 요약과 무관한 요청은 정중히 거절한다."


@tool
def get_meeting_notes(meeting_name: str) -> str:
    """회의 이름으로 회의록을 가져온다."""
    return (
        f"[{meeting_name} 회의록]\n"
        "- 결정: 신규 사내 챗봇은 11월 첫 주에 시범 운영한다.\n"
        "- 할 일: 시범 운영 안내 메일 작성 (담당 김민수)\n"
        "- 할 일: 사용자 피드백 설문 준비 (담당 박지영)"
    )


def build_agent():
    # ✍️ 1. Deep Agent 만들기
    # ✨ create_deep_agent · model=llm · tools=[get_meeting_notes] · FilesystemBackend(root_dir=TASK_DIR, virtual_mode=True) · skills=["4-1_skills/"] · system_prompt=SYSTEM_PROMPT · MemorySaver()
    return create_deep_agent(
        model=llm,
        tools=[get_meeting_notes],
        backend=FilesystemBackend(root_dir=str(TASK_DIR), virtual_mode=True),
        skills=["4-1_skills/"],  # 스킬 폴더들을 담은 상위 폴더
        system_prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),
    )


agent = build_agent()

# ✍️ 2. 요약 양식 스킬 쓰기 → 4-1_skills/meeting-summary/SKILL.md
# ✨ description: 언제 쓰는지 · 본문: get_meeting_notes 먼저 → 첫 줄 [회의 요약] → 결정 사항 → 할 일(담당자)
if "✍️" in SKILL_MD.read_text(encoding="utf-8"):
    print("(2. 아직 작성하지 않았습니다)")

results = []
if agent is not None:
    deep_agent_result = agent.invoke(
        {"messages": [HumanMessage(content="주간 회의 회의록을 가져와서 요약해 줘.")]},
        config={"configurable": {"thread_id": "request_1"}},
    )
    results = deep_agent_result["messages"]
    for m in results:
        m.pretty_print()


# ── ✅ 확인 (바꾸지 않습니다) ──
print("\n✅ 확인")
tool_msgs = [m for m in results if isinstance(m, ToolMessage)]
if agent is None:
    print("⛔ 1. 아직 작성하지 않았습니다")
elif not any(m.name == "get_meeting_notes" for m in tool_msgs):
    print("⛔ 1. Agent가 get_meeting_notes 도구를 부르지 않았습니다")
else:
    print("🟢 1. Deep Agent가 회의록 도구를 불러 썼습니다")
skill = SKILL_MD.read_text(encoding="utf-8")
final = str(results[-1].content).strip() if results else ""
if "✍️" in skill:
    print("⛔ 2. 아직 작성하지 않았습니다")
elif "name: meeting-summary" not in skill or "description:" not in skill:
    print("⛔ 2. SKILL.md 머리말에 name과 description이 있어야 합니다")
elif agent is None:
    print("⛔ 2. 1의 Agent가 있어야 확인합니다")
elif not any(m.name == "read_file" and "meeting-summary" in str(m.content) for m in tool_msgs):
    print("⛔ 2. Agent가 SKILL.md를 읽지 않았습니다(description, skills 경로를 확인합니다)")
elif not final.startswith("[회의 요약]") or "김민수" not in final:
    print("⛔ 2. 답의 첫 줄이 [회의 요약]이 아니거나 담당자(김민수)가 빠졌습니다")
else:
    print("🟢 2. 스킬을 읽고 그 양식대로 답했습니다")
