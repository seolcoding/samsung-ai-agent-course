"""
터미널에서 화살표 메뉴로 Agent에게 답하는 일정 조율 Agent

Agent가 묻는 질문(ask_user)은 화살표 메뉴로 고르고, 보내기 전 메일(send_email)은
승인·수정·거절 중에서 고른다. 거절할 때 적은 이유는 Agent에게 전해져 다시 쓰게 한다.
메뉴는 questionary 라이브러리로 그린다. 없으면 번호를 입력하는 메뉴로 대신한다.
"""

import uuid

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from config.llm import get_llm

load_dotenv()

try:
    import questionary
except ImportError:  # questionary가 없으면 번호 입력 메뉴로 동작한다
    questionary = None


# ── 도구 ──────────────────────────────────────────────────────────────────────
@tool
def check_calendar(week: str) -> str:
    """'이번 주' 또는 '다음 주'에 회의를 잡을 수 있는 빈 시간을 찾는다."""
    # 연습용 일정표: 실제 일정 시스템 대신 정해 둔 값을 돌려준다
    free = {
        "이번 주": ["금요일 16:00"],
        "다음 주": ["화요일 14:00", "수요일 10:00", "목요일 16:00"],
    }
    slots = free.get(week.strip(), free["다음 주"])
    return f"{week}에 비어 있는 시간: " + ", ".join(slots)


@tool
def ask_user(question: str, choices: list[str]) -> str:
    """사용자에게 질문 하나와 고를 수 있는 선택지 목록을 보여 주고 하나를 고르게 한다."""
    return f"[응답 없음: {question}]"  # 실행되지 않는다. 사람의 답이 이 자리에 들어간다


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """받는 사람에게 메일을 보낸다."""
    return f"메일을 보냈습니다(연습용이라 실제로 보내지 않음). 받는 사람: {to} | 제목: {subject} | 본문: {body}"


SYSTEM_PROMPT = """너는 DS부문 홍길동 프로의 회의 일정을 조율하고 메일을 보내는 업무 비서다.

규칙:
- 사용자만 정할 수 있는 선택은 ask_user로 묻는다. choices에는 선택지를 2~4개 넣는다.
- 회의를 미루기로 했다면 check_calendar로 빈 시간을 찾고, 그 시간들을 선택지로 ask_user에 다시 묻는다.
- 정해진 내용으로 메일을 써서 send_email로 보낸다. 메일은 홍길동 프로가 보내는 글로, 짧고 정중하게 쓰고 끝에 '홍길동 드림'을 붙인다.
- 메일이 거절되면 거절 이유를 반영해 다시 써서 send_email을 부른다. 이유에 보내지 말라고 했으면 보내지 않는다.
- 도구 결과로 확인하기 전에는 메일을 보냈다고 말하지 않는다.
"""

INTERRUPT_ON = {
    "ask_user": {"allowed_decisions": ["respond"]},
    "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
}

DEFAULT_REQUEST = (
    "협력사 김민수 책임(minsu.kim@partner.example.com)에게 내가 내일 오후 회의에 참석하기 어렵다고 메일 보내 줘. "
    "회의를 미룰지 온라인으로 바꿀지는 나한테 먼저 물어봐."
)


# ── 메뉴 ──────────────────────────────────────────────────────────────────────
def choose(question: str, choices: list[str]) -> str | None:
    """선택지 중 하나를 고르게 한다. Ctrl+C로 그만두면 None."""
    if questionary:
        return questionary.select(question, choices=choices).ask()
    print(question)
    for i, choice in enumerate(choices, start=1):
        print(f"  {i}. {choice}")
    while True:
        picked = input("번호: ").strip()
        if picked.isdigit() and 1 <= int(picked) <= len(choices):
            return choices[int(picked) - 1]
        print(f"1부터 {len(choices)} 사이의 번호를 입력합니다.")


def ask_text(question: str, default: str = "") -> str | None:
    """글을 입력받는다. 그냥 Enter를 누르면 default."""
    if questionary:
        return questionary.text(question, default=default).ask()
    typed = input(f"{question} (Enter: 그대로) ").strip()
    return typed or default


def review_email(request: dict) -> dict | None:
    """보내기 전 메일을 보여 주고 승인·수정·거절 중 하나를 고르게 한다."""
    args = request["args"]
    print("\n── 보내기 전 메일 ──")
    print(f"받는 사람: {args.get('to')}\n제목: {args.get('subject')}\n{args.get('body')}")
    print("─" * 30)
    action = choose("이 메일을 어떻게 할까요?", ["승인: 그대로 보내기", "수정: 본문 고쳐 보내기", "거절: 이유 적어 돌려보내기"])
    if action is None:
        return None
    if action.startswith("승인"):
        return {"type": "approve"}
    if action.startswith("수정"):
        body = ask_text("고친 본문:", default=args.get("body", ""))
        if body is None:
            return None
        return {"type": "edit", "edited_action": {"name": request["name"], "args": {**args, "body": body}}}
    reason = ask_text("거절 이유(Agent에게 전해집니다):", default="더 짧게 다시 써 주세요.")
    if reason is None:
        return None
    return {"type": "reject", "message": reason}


def print_new_steps(messages: list, start: int) -> int:
    """지난번 이후 새로 생긴 도구 호출과 도구 결과를 한 줄씩 보여 준다."""
    for m in messages[start:]:
        for call in getattr(m, "tool_calls", None) or []:
            print(f"  → Agent가 {call['name']} 호출: {call['args']}")
        if m.type == "tool":
            print(f"  ← {m.name} 결과: {str(m.content)[:120]}")
    return len(messages)


# ── 실행 ──────────────────────────────────────────────────────────────────────
def main() -> None:
    if questionary is None:
        print("(questionary가 없어 번호 입력 메뉴로 실행합니다)\n")
    agent = create_deep_agent(
        model=get_llm(),
        tools=[check_calendar, ask_user, send_email],
        system_prompt=SYSTEM_PROMPT,
        interrupt_on=INTERRUPT_ON,
        checkpointer=MemorySaver(),
    )
    config = {"configurable": {"thread_id": f"terminal-{uuid.uuid4().hex[:6]}"}, "recursion_limit": 60}

    user_request = ask_text("Agent에게 보낼 요청:", default=DEFAULT_REQUEST)
    if not user_request:
        return
    print("\nAgent가 일하는 중입니다(수십 초 걸릴 수 있습니다)...")
    result = agent.invoke({"messages": [{"role": "user", "content": user_request}]}, config=config, version="v2")
    seen = print_new_steps(result.value["messages"], 0)

    # 멈출 때마다 사람의 결정을 모아 이어서 실행한다. 몇 번 멈추든 같은 반복문이 받는다
    while result.interrupts:
        decisions = []
        for request in result.interrupts[0].value["action_requests"]:
            if request["name"] == "ask_user":
                print()
                picked = choose(request["args"]["question"], request["args"]["choices"])
                decision = None if picked is None else {"type": "respond", "message": picked}
            else:
                decision = review_email(request)
            if decision is None:
                print("\n중단했습니다. 메일은 보내지 않았습니다.")
                return
            decisions.append(decision)
        print("\nAgent가 이어서 일하는 중입니다...")
        result = agent.invoke(Command(resume={"decisions": decisions}), config=config, version="v2")
        seen = print_new_steps(result.value["messages"], seen)

    print("\n── Agent의 마지막 답 ──")
    print(result.value["messages"][-1].content)


if __name__ == "__main__":
    main()
