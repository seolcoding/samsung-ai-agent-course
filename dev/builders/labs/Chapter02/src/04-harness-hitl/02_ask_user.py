"""
사람 승인 실습 2: Agent가 사람에게 묻고 답을 받기

ask_user 도구는 respond 결정만 받게 해 둔다. 이 도구는 실제로 실행되지 않고,
사람이 고른 답이 도구 결과 자리에 그대로 들어간다.
"""

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
    """사용자에게 질문 하나와 고를 수 있는 선택지 목록을 보여 주고 하나를 고르게 한다."""
    # 이 줄은 실행되지 않는다. respond 결정이 사람의 답을 도구 결과로 대신 넣는다
    return f"[응답 없음: {question}]"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """받는 사람에게 메일을 보낸다."""
    # 연습용 도구: 실제로 보내지 않는다
    return f"메일을 보냈습니다. 받는 사람: {to} | 제목: {subject} | 본문: {body}"


# ── Agent 만들기 ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """너는 DS부문 홍길동 프로의 메일을 대신 써서 보내는 업무 비서다.

규칙:
- 요청에 사용자만 정할 수 있는 선택이 있으면, 메일을 쓰기 전에 ask_user로 먼저 묻는다.
  question에는 질문 한 문장, choices에는 고를 수 있는 선택지를 2개 이상 넣는다.
- ask_user의 답에 맞춰 메일 내용을 정한다.
- 보낼 준비가 되면 send_email을 쓴다.
- 메일은 홍길동 프로가 보내는 글로, 짧고 정중하게 쓰고 끝에 '홍길동 드림'을 붙인다.
- 도구 결과로 확인하기 전에는 메일을 보냈다고 말하지 않는다.
"""

mail_agent = create_deep_agent(
    model=get_llm(),
    tools=[ask_user, send_email],
    system_prompt=SYSTEM_PROMPT,
    interrupt_on={
        # 묻는 도구: 사람이 답하는 것(respond)만 허용한다
        "ask_user": {"allowed_decisions": ["respond"]},
        # 밖으로 나가는 도구: 승인·수정·거절 중 하나
        "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
    },
    checkpointer=MemorySaver(),
)

# ── 요청 보내고 질문 받기 ─────────────────────────────────────────────────────
config = {"configurable": {"thread_id": f"ask-{uuid.uuid4().hex[:6]}"}}

mail_agent_result = mail_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "협력사 김민수 책임(minsu.kim@partner.example.com)에게 내가 내일 오후 회의에 참석하기 어렵다고 메일 보내 줘. "
                    "그런데 먼저 회의를 다음 주로 미뤄 달라고 할지, 온라인으로 바꿔 달라고 할지 나한테 물어봐."
                ),
            }
        ]
    },
    config=config,
    version="v2",
)

request = mail_agent_result.interrupts[0].value["action_requests"][0] if mail_agent_result.interrupts else None
if request and request["name"] == "ask_user":
    print("질문:", request["args"]["question"])
    for i, choice in enumerate(request["args"]["choices"]):
        print(f"  [{i}] {choice}")
elif request:
    print(f"Agent가 묻지 않고 바로 {request['name']}을(를) 부르려 합니다. 이 셀을 한 번 더 실행합니다.")
else:
    print("멈추지 않고 끝났습니다. 이 셀을 한 번 더 실행합니다.")

# ── 답 골라 보내기 ────────────────────────────────────────────────────────────
answer = request["args"]["choices"][0]

print("고른 답:", answer)
# respond: 도구를 실행하지 않고, 사람의 답을 도구 결과로 넣는다
mail_agent_result = mail_agent.invoke(
    Command(resume={"decisions": [{"type": "respond", "message": answer}]}),
    config=config,
    version="v2",
)

draft = mail_agent_result.interrupts[0].value["action_requests"][0] if mail_agent_result.interrupts else None
if draft and draft["name"] == "send_email":
    print("\n보내기 전 메일 초안(승인을 기다리는 중):")
    for key, value in draft["args"].items():
        print(f"- {key}: {value}")
else:
    print("메일 초안 단계에서 멈추지 않았습니다. '요청 보내고 질문 받기' 셀부터 다시 실행합니다.")

# ── 승인하고 대화 보기 ────────────────────────────────────────────────────────
mail_agent_result = mail_agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}), config=config, version="v2"
)

results = mail_agent_result.value["messages"]
for m in results:
    m.pretty_print()
