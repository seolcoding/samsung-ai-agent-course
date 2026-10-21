import uuid

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from config.llm import get_llm

load_dotenv()


@tool
def ask_user(question: str, choices: list[str]) -> str:
    """사용자에게 선택지를 보여 주고 하나를 고르게 한다."""
    return ""  # 실행되지 않는다. 사람이 고른 답이 이 자리에 들어간다


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """메일을 보낸다."""
    return f"메일을 보냈습니다. 제목: {subject} | 본문: {body}"  # 연습용: 실제로 보내지 않는다


# ── Agent 만들기 ──
agent = create_deep_agent(
    model=get_llm(),
    tools=[ask_user, send_email],
    system_prompt=(
        "너는 홍길동 프로의 메일 비서다. 사용자가 정해야 할 것이 있으면 메일을 쓰기 전에 ask_user로 선택지를 주고 묻는다. "
        "메일은 홍길동 프로가 보내는 글로 짧게 쓰고 끝에 '홍길동 드림'을 붙인다."
    ),
    interrupt_on={
        # 묻는 도구는 사람이 답하기(respond)만, 보내는 도구는 승인·거절만 받는다
        "ask_user": {"allowed_decisions": ["respond"]},
        "send_email": {"allowed_decisions": ["approve", "reject"]},
    },
    checkpointer=MemorySaver(),
)

# ── 요청하고 질문 받기 ──
config = {"configurable": {"thread_id": str(uuid.uuid4())}}
request = (
    "김민수 책임(minsu.kim@partner.example.com)에게 내가 내일 오후 회의에 못 간다고 메일 보내 줘. "
    "다음 주로 미룰지 온라인으로 바꿀지는 먼저 나한테 물어봐."
)
result = agent.invoke({"messages": [("user", request)]}, config, version="v2")

# Agent가 멈췄습니다. 질문과 선택지를 봅니다
question = result.interrupts[0].value["action_requests"][0]["args"]
print(question)

# ── 답하고 승인하기 ──
answer = question["choices"][0]

# 고른 답을 보내면 Agent가 메일을 쓰고, 보내기 전에 다시 멈춘다
decision = {"type": "respond", "message": answer}
result = agent.invoke(Command(resume={"decisions": [decision]}), config, version="v2")
print("메일 초안:", result.interrupts[0].value["action_requests"][0]["args"]["body"])

# 초안을 승인한다
decision = {"type": "approve"}
result = agent.invoke(Command(resume={"decisions": [decision]}), config, version="v2")
for m in result.value["messages"]:
    print(f"[{m.type}] {m.content[:100]}")
