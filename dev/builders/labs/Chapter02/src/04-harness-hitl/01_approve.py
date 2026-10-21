"""
사람 승인 실습 1: 메일을 보내기 전에 사람에게 승인받기

create_deep_agent에 interrupt_on을 주면 Agent가 그 도구를 부르기 직전에 멈춘다.
사람이 approve(그대로)·edit(고쳐서)·reject(보내지 않음) 중 하나로 답하면 이어서 실행한다.
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
def send_email(to: str, subject: str, body: str) -> str:
    """받는 사람에게 메일을 보낸다."""
    # 연습용 도구: 실제로 보내지 않고, 보냈다면 무엇이 갔을지만 돌려준다
    return f"메일을 보냈습니다. 받는 사람: {to} | 제목: {subject} | 본문: {body}"


# ── Agent 만들기 ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """너는 DS부문 홍길동 프로의 메일을 대신 써서 보내는 업무 비서다.

규칙:
- 메일을 보내 달라는 요청에는 send_email을 쓴다.
- 메일은 홍길동 프로가 보내는 글로, 짧고 정중하게 쓰고 끝에 '홍길동 드림'을 붙인다.
- 도구 결과로 확인하기 전에는 메일을 보냈다고 말하지 않는다.
- 보냈다고 알릴 때는 원래 요청이 아니라 도구 결과에 있는 제목과 본문을 그대로 옮긴다.
"""

mail_agent = create_deep_agent(
    model=get_llm(),
    tools=[send_email],
    system_prompt=SYSTEM_PROMPT,
    # send_email을 부르기 직전에 멈추고, 사람의 결정(세 가지 중 하나)을 기다린다
    interrupt_on={"send_email": {"allowed_decisions": ["approve", "edit", "reject"]}},
    # 멈춘 자리를 기억해 두어야 사람의 결정을 받은 뒤 이어서 실행할 수 있다
    checkpointer=MemorySaver(),
)

# ── 요청 보내고 멈춘 곳 보기 ──────────────────────────────────────────────────
# 실행할 때마다 새 대화(thread_id)로 시작한다
config = {"configurable": {"thread_id": f"mail-{uuid.uuid4().hex[:6]}"}}

# version="v2": 결과를 상태(.value)와 멈춘 곳(.interrupts)으로 나눠 받는다
mail_agent_result = mail_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "협력사 김민수 책임(minsu.kim@partner.example.com)에게 내일 오전 회의에 10분 늦는다고 메일 보내 줘.",
            }
        ]
    },
    config=config,
    version="v2",
)

if mail_agent_result.interrupts:
    pending = mail_agent_result.interrupts[0].value  # 사람이 검토할 도구 호출 목록
    request = pending["action_requests"][0]
    print("멈춘 도구:", request["name"])
    print("고를 수 있는 결정:", pending["review_configs"][0]["allowed_decisions"])
    for key, value in request["args"].items():
        print(f"- {key}: {value}")
else:
    print("멈추지 않고 끝났습니다. Agent가 send_email을 부르지 않았습니다.")
    print(mail_agent_result.value["messages"][-1].content)

# ── 결정 보내 이어 가기 ───────────────────────────────────────────────────────
decision_type = "approve"

if not mail_agent_result.interrupts:
    print("멈춘 곳이 없습니다. 위의 '요청 보내고 멈춘 곳 보기' 셀을 먼저 다시 실행합니다.")
else:
    if decision_type == "approve":  # 모델이 쓴 그대로 실행
        decision = {"type": "approve"}
    elif decision_type == "edit":  # 사람이 고친 값으로 실행
        edited_args = {
            **request["args"],
            "body": "김민수 책임님, 내일 오전 회의에 10분 늦게 들어가겠습니다. 죄송합니다. 홍길동 드림",
        }
        decision = {"type": "edit", "edited_action": {"name": request["name"], "args": edited_args}}
    else:  # 실행하지 않고, 이유를 모델에게 전한다
        decision = {"type": "reject", "message": "이 메일은 보내지 않습니다. 보내지 않았다고만 짧게 답하세요."}

    mail_agent_result = mail_agent.invoke(Command(resume={"decisions": [decision]}), config=config, version="v2")

    results = mail_agent_result.value["messages"]
    for m in results:
        m.pretty_print()
    if mail_agent_result.interrupts:
        print("\nAgent가 send_email을 다시 부르려고 또 멈췄습니다.")
