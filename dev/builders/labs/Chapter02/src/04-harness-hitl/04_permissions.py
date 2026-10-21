"""
하네스 실습: 파일 권한으로 Agent가 고칠 수 있는 곳 정하기

FilesystemPermission은 Agent의 파일 도구(write_file·edit_file 등)가 어느 경로에 무엇을 할 수 있는지 정한다.
mode는 allow(허용)·deny(막음)·interrupt(사람 승인을 기다림) 셋 중 하나다.
"""

import uuid
from pathlib import Path

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from config.llm import get_llm

load_dotenv()

WORK_DIR = Path("harness_plus")  # Agent의 작업 폴더. Agent에게는 이 폴더가 맨 위(/)로 보인다
RULES_FILE = WORK_DIR / "reference" / "meeting_rules.md"
RULES_TEXT = """# 회의실 사용 규칙

- 회의실은 사내 예약 시스템으로 하루 전까지 예약한다.
- 회의가 끝나면 화이트보드를 지운다.
"""
RULES_FILE.parent.mkdir(parents=True, exist_ok=True)

# ── Agent 만들기 ──────────────────────────────────────────────────────────────
file_agent = create_deep_agent(
    model=get_llm(),
    backend=FilesystemBackend(root_dir=str(WORK_DIR), virtual_mode=True),
    permissions=[
        FilesystemPermission(operations=["write"], paths=["/reference/**"], mode="deny"),
    ],
    system_prompt="너는 팀 문서를 정리하는 비서다. 파일을 고칠 수 없으면 그 이유를 짧게 말한다.",
    checkpointer=MemorySaver(),  # mode가 interrupt일 때 멈춘 자리를 기억한다
)

# ── 규칙 파일 고쳐 달라고 하기 ────────────────────────────────────────────────
RULES_FILE.write_text(RULES_TEXT, encoding="utf-8")  # 실행할 때마다 처음 내용으로 되돌리고 시작한다
config = {"configurable": {"thread_id": f"perm-{uuid.uuid4().hex[:6]}"}}

file_agent_result = file_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "/reference/meeting_rules.md를 읽고, 맨 아래에 '- 금요일 오후 회의실은 예약 없이 쓸 수 있다.' 한 줄을 더해 줘.",
            }
        ]
    },
    config=config,
    version="v2",
)

results = file_agent_result.value["messages"]
for m in results:
    m.pretty_print()
if file_agent_result.interrupts:
    request = file_agent_result.interrupts[0].value["action_requests"][0]
    print(f"\n사람 승인을 기다리며 멈췄습니다: {request['name']} {request['args'].get('file_path')}")

print("\n=== 실행 뒤 파일 내용 ===")
print(RULES_FILE.read_text(encoding="utf-8"))
