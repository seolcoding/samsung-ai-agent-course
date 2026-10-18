"""2-2 과제 · Researcher와 Writer로 나눈 Agent 팀

✍️ 할 곳  코드의 `# ✍️` 표시 2곳만 채웁니다 (`# ✨` 줄은 AI에게 말할 힌트)
▶️ 실행   uv run --env-file .env python course/Chapter01/tasks/2-2_task.py
✅ 확인   실행하면 맨 끝에 🟢/⛔가 나옵니다
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""
import inspect
from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

llm = get_llm()
TOPIC = "AI Agent 기술의 현황과 전망을 조사해서 짧은 글로 써 줘."


@tool
def search_web(query: str) -> str:
    """웹에서 주제를 조사한다."""
    return (
        f'["{query}" 검색 결과]\n'
        "- 주요 동향: 최근 급격한 성장세를 보이고 있음\n"
        "- 핵심 기술 요소: 도구 호출, 계획 세우기, 기억\n"
        "- 주요 플레이어: OpenAI, Anthropic, Google DeepMind\n"
        "- 미래 전망: 향후 3년간 지속적인 발전이 예상됨"
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    research_result: str  # Researcher가 정리한 조사 내용
    draft: str            # Writer가 쓴 글


# ✍️ 1. Researcher → Writer 두 노드
# ✨ researcher: 모델 답 → messages·research_result · writer: research_result 넣은 프롬프트 → draft · 바뀐 키만 dict
def researcher(state: State) -> dict:
    return {"research_result": "(1. 아직 작성하지 않았습니다)"}


def writer(state: State) -> dict:
    return {"draft": "(1. 아직 작성하지 않았습니다)"}


builder = StateGraph(State)
builder.add_node("researcher", researcher)
builder.add_node("writer", writer)
builder.add_edge(START, "researcher")
builder.add_edge("writer", END)

# ✍️ 2. 검색 도구는 Researcher에게만
# ✨ researcher 모델만 llm.bind_tools([search_web]) · ToolNode → "researcher_tools" · 아래 add_edge 대신 tool_calls 있으면 researcher_tools → researcher, 없으면 writer
print("(2. 아직 작성하지 않았습니다)")
builder.add_edge("researcher", "writer")

team = builder.compile()

flow, final, tool_steps = [], {}, set()
start = {"messages": [HumanMessage(content=TOPIC)], "research_result": "", "draft": ""}
try:  # recursion_limit: 멈추지 않고 돌면 40단계에서 멈춥니다
    for chunk in team.stream(start, {"recursion_limit": 40}, stream_mode="updates"):
        for node_name, update in chunk.items():
            flow.append(node_name)
            final.update(update or {})
            print(f"\n========= [{node_name}] =========")
            for m in (update or {}).get("messages", []):
                m.pretty_print()
                if m.type == "tool" or getattr(m, "tool_calls", None):
                    tool_steps.add(node_name)  # 도구를 부르거나 도구 결과가 나온 단계
except GraphRecursionError:
    print("\n✖ 40단계를 넘어 멈췄습니다(GraphRecursionError)")
print("\n=== 흐름 ===\n" + " → ".join(flow))
print("\n=== 조사 결과 (research_result) ===\n" + final.get("research_result", ""))
print("\n=== 최종 글 (draft) ===\n" + final.get("draft", ""))

# ── ✅ 확인 (바꾸지 않습니다) ──
research, draft = final.get("research_result", ""), final.get("draft", "")
print("\n✅ 확인")
if "아직 작성하지" in research + draft:
    print("⛔ 1. 아직 작성하지 않았습니다")
elif not research.strip() or not draft.strip():
    print("⛔ 1. research_result나 draft가 비어 있다")
elif "research_result" not in inspect.getsource(writer):
    print("⛔ 1. writer가 research_result를 읽지 않는다")
else:
    print("🟢 1. researcher가 research_result를, writer가 그것으로 draft를 넘겼다")
if "researcher_tools" not in team.nodes:
    print("⛔ 2. 아직 작성하지 않았습니다 (researcher_tools 노드가 없다)")
elif tool_steps != {"researcher", "researcher_tools"}:
    print(f"⛔ 2. 도구를 쓴 단계가 {sorted(tool_steps) or '없음'}이다 (researcher·researcher_tools만이어야 한다)")
elif flow.count("writer") != 1:
    print(f"⛔ 2. writer가 {flow.count('writer')}번 실행됐다 (흐름: {' → '.join(flow)})")
else:
    print("🟢 2. 검색 도구는 researcher 단계에서만 쓰였다")
