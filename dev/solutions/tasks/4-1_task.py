"""4-1 과제: 회의록 요약 스킬을 쓰는 Deep Agent

실행(저장소 맨 위에서):
    uv run --env-file .env python course/Chapter02/tasks/4-1/4-1_task.py

강사용 정답. 이 파일은 course/Chapter02/tasks/4-1/4-1_task.py 자리에, 정답 SKILL.md(dev/solutions/tasks/4-1_skills/meeting-summary/SKILL.md)는
course/Chapter02/tasks/4-1/skills/meeting-summary/SKILL.md 자리에 놓고 실행한다(TASK_DIR가 이 파일의 폴더다).
"""

import atexit
import shutil
import tempfile
from pathlib import Path

from deepagents import create_deep_agent  # noqa: F401 — 목표 1에서 씁니다
from deepagents.backends import FilesystemBackend  # noqa: F401
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage  # noqa: F401
from langchain_core.tools import tool  # noqa: F401
from langgraph.checkpoint.memory import MemorySaver  # noqa: F401

from config.llm import get_llm

load_dotenv()

llm = get_llm()

# Agent의 작업 공간: 이 과제 폴더. 그 안의 skills/ 아래에 스킬 폴더(meeting-summary/)가 있습니다.
TASK_DIR = Path(__file__).resolve().parent

REQUEST_1 = "주간 회의 회의록을 가져와서 요약해 줘."
REQUEST_2 = "파이썬으로 피보나치 코드를 짜 줘."


def copy_skills_with_one_line_changed(old_line: str, new_line: str) -> Path:
    """skills 폴더를 임시 폴더에 복사하고, 사본 SKILL.md에서 한 줄만 바꿉니다(목표 4에서 씁니다).

    돌려주는 값은 사본 작업 공간 폴더입니다(그 안에 skills/가 있습니다).
    원본 SKILL.md와 저장소는 그대로이고, 사본은 실행이 끝나면 지워집니다. 이 함수는 고치지 않습니다.
    """
    work_dir = Path(tempfile.mkdtemp(prefix="skill_after_"))
    atexit.register(shutil.rmtree, work_dir, ignore_errors=True)
    shutil.copytree(TASK_DIR / "skills", work_dir / "skills")
    copy_file = work_dir / "skills" / "meeting-summary" / "SKILL.md"
    lines = copy_file.read_text(encoding="utf-8").splitlines()
    found = [i for i, line in enumerate(lines) if line.strip() == old_line.strip()]
    if len(found) != 1:
        raise ValueError(f"SKILL.md에 이 줄이 정확히 한 번 있어야 합니다(지금 {len(found)}번): {old_line!r}")
    lines[found[0]] = new_line
    copy_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n바꾼 줄(사본 SKILL.md, 원본은 그대로):\n- {old_line.strip()}\n+ {new_line.strip()}")
    return work_dir


# 목표 1: 회의록 도구와 Agent를 만드는 함수
@tool
def get_meeting_notes(meeting_name: str) -> str:
    """회의 이름으로 회의록을 가져온다."""
    return (
        f"[{meeting_name} 회의록]\n"
        "- 결정: 신규 사내 챗봇은 11월 첫 주에 시범 운영한다.\n"
        "- 할 일: 시범 운영 안내 메일 작성 (담당 김민수)\n"
        "- 할 일: 사용자 피드백 설문 준비 (담당 박지영)"
    )


SYSTEM_PROMPT = "회의록 요약만 돕는다. 코드 작성, 수학 계산 등 회의록 요약과 무관한 요청은 정중히 거절한다."


def build_agent(root_dir: Path):
    """root_dir를 작업 공간으로 쓰는 Deep Agent를 만든다. 스킬은 root_dir/skills/ 아래에서 찾는다."""
    backend = FilesystemBackend(root_dir=str(root_dir), virtual_mode=True)
    return create_deep_agent(
        model=llm,
        tools=[get_meeting_notes],
        backend=backend,
        skills=["skills/"],  # 스킬 폴더들을 담은 상위 폴더
        system_prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),
    )


def run(agent, thread_id: str, question: str) -> str:
    """요청 하나를 실행해 메시지를 모두 출력하고 마지막 답을 돌려준다."""
    print(f"\n=== {question} ===")
    deep_agent_result = agent.invoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    results = deep_agent_result["messages"]
    for m in results:
        m.pretty_print()
    return results[-1].content


agent = build_agent(TASK_DIR)


# 목표 2: 스킬을 읽고 양식대로 답하는 요청 1
answer_1 = run(agent, "request_1", REQUEST_1)


# 목표 3: 범위 밖 요청 2를 다른 thread_id로 실행하고 비교
answer_2 = run(agent, "request_2", REQUEST_2)
print("\n=== 요청 1과 요청 2 비교 ===")
print(f"[요청 1] {REQUEST_1}\n{answer_1}\n")
print(f"[요청 2] {REQUEST_2}\n{answer_2}")


# 목표 4: SKILL.md 한 줄만 바꾼 사본으로 같은 요청을 다시 실행
after_dir = copy_skills_with_one_line_changed(
    "[회의 요약]",
    "[주간 회의 요약]",
)
after_agent = build_agent(after_dir)
answer_after = run(after_agent, "request_1_after", REQUEST_1)
print("\n=== SKILL.md 한 줄 전후 비교 ===")
print(f"[바꾸기 전]\n{answer_1}\n")
print(f"[바꾼 후]\n{answer_after}")
