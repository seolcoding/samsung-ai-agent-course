import uuid
from pathlib import Path

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from config.llm import get_llm

load_dotenv()

RULES = Path("harness_plus/reference/rules.md")  # Agent에게는 /reference/rules.md로 보인다
RULES.parent.mkdir(parents=True, exist_ok=True)

# ── Agent 만들기 ──
# 규칙: /reference/ 아래 파일에 쓰기(write)를 mode에 따라 허용·막음·승인 대기
rule = FilesystemPermission(operations=["write"], paths=["/reference/**"], mode="deny")

agent = create_deep_agent(
    model=get_llm(),
    backend=FilesystemBackend(root_dir="harness_plus", virtual_mode=True),  # 작업 폴더
    permissions=[rule],
    checkpointer=MemorySaver(),
)

# ── 파일 고쳐 달라고 하기 ──
# 실행할 때마다 파일을 처음 내용으로 되돌린다
RULES.write_text("# 회의실 규칙\n- 하루 전까지 예약한다.\n", encoding="utf-8")

config = {"configurable": {"thread_id": str(uuid.uuid4())}}
request = "/reference/rules.md 맨 아래에 '- 금요일에는 예약 없이 쓴다.' 한 줄을 더해 줘."
result = agent.invoke({"messages": [("user", request)]}, config, version="v2")

print("Agent의 답:", result.value["messages"][-1].content)
print("멈췄나요?:", bool(result.interrupts))
print("--- 실행 뒤 파일 ---")
print(RULES.read_text(encoding="utf-8"))
