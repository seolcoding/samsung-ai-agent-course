import uuid

import questionary
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
    return ""


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """메일을 보낸다."""
    return f"메일을 보냈습니다. 제목: {subject}"  # 연습용: 실제로 보내지 않는다


agent = create_deep_agent(
    model=get_llm(),
    tools=[ask_user, send_email],
    system_prompt=(
        "너는 홍길동 프로의 메일 비서다. 사용자가 정해야 할 것이 있으면 메일을 쓰기 전에 ask_user로 선택지를 주고 묻는다. "
        "메일은 홍길동 프로가 보내는 글로 짧게 쓰고 끝에 '홍길동 드림'을 붙인다. 메일이 거절되면 이유에 맞춰 다시 써서 보낸다."
    ),
    interrupt_on={
        "ask_user": {"allowed_decisions": ["respond"]},
        "send_email": {"allowed_decisions": ["approve", "reject"]},
    },
    checkpointer=MemorySaver(),
)
config = {"configurable": {"thread_id": str(uuid.uuid4())}}

request = questionary.text(
    "Agent에게 보낼 요청:",
    default="김민수 책임(minsu.kim@partner.example.com)에게 내가 내일 오후 회의에 못 간다고 메일 보내 줘. "
    "다음 주로 미룰지 온라인으로 바꿀지는 먼저 나한테 물어봐.",
).ask()
print("Agent가 일하는 중입니다...")
result = agent.invoke({"messages": [("user", request)]}, config, version="v2")

# Agent가 멈출 때마다 메뉴로 답하고 이어서 실행한다. 몇 번 멈추든 이 반복문이 받는다
while result.interrupts:
    action = result.interrupts[0].value["action_requests"][0]
    if action["name"] == "ask_user":  # 질문: 화살표 메뉴로 고르기
        answer = questionary.select(action["args"]["question"], choices=action["args"]["choices"]).ask()
        decision = {"type": "respond", "message": answer}
    else:  # 메일: 보여 주고 승인 또는 거절
        print("\n" + action["args"]["body"] + "\n")
        if questionary.confirm("이 메일을 보낼까요?").ask():
            decision = {"type": "approve"}
        else:
            reason = questionary.text("고칠 점(Agent에게 전해집니다):").ask()
            decision = {"type": "reject", "message": reason}
    print("Agent가 일하는 중입니다...")
    result = agent.invoke(Command(resume={"decisions": [decision]}), config, version="v2")

print("\n" + result.value["messages"][-1].content)
