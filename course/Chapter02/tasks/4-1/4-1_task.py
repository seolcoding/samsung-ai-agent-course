"""4-1 과제: 회의록 요약 스킬을 쓰는 Deep Agent

실행(저장소 맨 위에서):
    uv run --env-file .env python course/Chapter02/tasks/4-1/4-1_task.py

고칠 파일은 두 개입니다. 이 파일(4-1_task.py)과 skills/meeting-summary/SKILL.md.
할 일과 프롬프트 힌트는 같은 폴더의 README.md에 있습니다.
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


# ✍️ 목표 1: @tool 회의록 도구 get_meeting_notes와, 작업 공간 폴더를 받아 Deep Agent를 돌려주는 build_agent(root_dir)를 만듭니다.
#            그다음 agent = build_agent(TASK_DIR)로 이 폴더를 작업 공간으로 쓰는 Agent를 만듭니다.
print("✍️ 목표 1은 아직 비어 있습니다. README.md의 할 일을 봅니다.")


# ✍️ 목표 2: skills/meeting-summary/SKILL.md를 쓰고 build_agent의 skills로 연결합니다.
#            REQUEST_1을 실행하고 메시지를 pretty_print()로 출력합니다.
print("✍️ 목표 2는 아직 비어 있습니다.")


# ✍️ 목표 3: system_prompt로 회의록 요약 밖의 요청을 거절시키고, REQUEST_2를 다른 thread_id로 실행합니다.
#            두 요청의 마지막 답을 나란히 출력해 비교합니다.
print("✍️ 목표 3은 아직 비어 있습니다.")


# ✍️ 목표 4: copy_skills_with_one_line_changed로 SKILL.md 한 줄만 바꾼 사본을 만들고, 같은 build_agent로 사본 Agent를 만듭니다.
#            REQUEST_1을 다시 실행해 바꾸기 전(목표 2)과 후의 마지막 답을 나란히 출력합니다.
print("✍️ 목표 4는 아직 비어 있습니다.")
