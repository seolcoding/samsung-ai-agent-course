import uuid

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from config.llm import get_llm

load_dotenv()


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """메일을 보낸다."""
    return f"메일을 보냈습니다. 제목: {subject} | 본문: {body}"  # 연습용: 실제로 보내지 않는다


# ── Agent 만들기 ──
agent = create_deep_agent(
    model=get_llm(),
    tools=[send_email],
    system_prompt="너는 홍길동 프로의 메일 비서다. 메일은 짧게 쓰고 끝에 '홍길동 드림'을 붙인다.",
    # send_email을 쓰기 직전에 멈추고, 사람의 결정(승인·수정·거절)을 기다린다
    interrupt_on={"send_email": {"allowed_decisions": ["approve", "edit", "reject"]}},
    checkpointer=MemorySaver(),  # 멈춘 자리를 기억한다
)

# ── 요청하고 멈춘 곳 보기 ──
config = {"configurable": {"thread_id": str(uuid.uuid4())}}  # 실행할 때마다 새 대화
request = "김민수 책임(minsu.kim@partner.example.com)에게 내일 회의에 10분 늦는다고 메일 보내 줘."
result = agent.invoke({"messages": [("user", request)]}, config, version="v2")

# Agent가 멈췄습니다. 보내려던 메일을 봅니다
email = result.interrupts[0].value["action_requests"][0]["args"]
print(email)

# ── 결정 보내기 ──
decision = {"type": "approve"}

result = agent.invoke(Command(resume={"decisions": [decision]}), config, version="v2")
for m in result.value["messages"]:
    print(f"[{m.type}] {m.content[:100]}")
