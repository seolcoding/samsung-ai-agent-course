"""
하네스 실습: 조사는 하위 Agent에게 맡기기

subagents에 하위 Agent를 적어 두면, 메인 Agent는 task 도구로 일을 맡긴다.
하위 Agent가 검색 결과를 혼자 읽고 정리한 답만 돌려주므로, 메인 Agent의 대화에는 긴 원문이 쌓이지 않는다.
"""

import uuid

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from config.llm import get_llm

load_dotenv()


@tool
def search_news(query: str) -> str:
    """반도체 업계 뉴스를 검색한다."""
    # 연습용 도구: 실제로 검색하지 않고, 정해 둔 가짜 기사 8건을 돌려준다
    articles = [
        "[기사 1] 메모리 업계, 고대역폭 메모리(HBM) 생산 능력 확대 계획을 잇달아 발표.",
        "[기사 2] AI 서버 수요 증가로 HBM 공급 부족이 내년까지 이어질 것이라는 전망.",
        "[기사 3] 차세대 HBM은 적층 단수를 늘려 용량을 키우는 방향으로 개발 중.",
        "[기사 4] 패키징 공정이 HBM 수율의 핵심 변수로 떠올라 관련 투자 확대.",
        "[기사 5] 고객사들이 HBM 공급처를 여러 곳으로 나누려는 움직임.",
        "[기사 6] 전력 효율이 HBM 경쟁의 새 기준으로 부각.",
        "[기사 7] 일부 고객사는 맞춤형 HBM 설계를 요구하기 시작.",
        "[기사 8] 장비 업계도 HBM용 본딩 장비 주문이 늘었다고 밝힘.",
    ]
    detail = " 업계 관계자는 수요와 공급, 기술 일정, 고객사 요구를 함께 살펴야 한다고 말했다." * 3
    return f"[검색어: {query}] (연습용 가짜 기사)\n" + "\n".join(a + detail for a in articles)


# ── 하위 Agent 정하기 ─────────────────────────────────────────────────────────
researcher = {
    "name": "researcher",
    "description": "주제 하나를 search_news로 검색해 정리해 돌려준다. 검색이 필요한 조사는 여기에 맡긴다.",
    "system_prompt": "너는 조사 담당이다. search_news로 검색한 뒤 핵심만 세 줄로 요약해 돌려준다. 검색 결과 원문은 돌려주지 않는다.",
    "tools": [search_news],  # 검색 도구는 하위 Agent만 가진다
}

# ── 메인 Agent 만들고 맡기기 ──────────────────────────────────────────────────
main_agent = create_deep_agent(
    model=get_llm(),
    tools=[],  # 메인 Agent에게는 검색 도구를 주지 않는다
    subagents=[researcher],
    system_prompt="너는 팀장 보고를 돕는 비서다. 조사가 필요하면 task 도구로 알맞은 하위 Agent에게 맡기고, 받은 내용으로 답한다.",
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": f"sub-{uuid.uuid4().hex[:6]}"}}
main_agent_result = main_agent.invoke(
    {"messages": [{"role": "user", "content": "HBM 시장 동향을 조사해서 팀장님께 드릴 세 줄 요약을 만들어 줘."}]},
    config=config,
    version="v2",
)

results = main_agent_result.value["messages"]
for m in results:
    m.pretty_print()

# 메인 Agent가 누구에게 맡겼는지, 받은 답(task 도구 결과)이 얼마나 긴지 본다
calls = [c for m in results for c in getattr(m, "tool_calls", None) or [] if c["name"] == "task"]
task_replies = [m for m in results if m.type == "tool" and m.name == "task"]
print("\n맡긴 하위 Agent:", [c["args"].get("subagent_type") for c in calls] or "없음(직접 답함)")
search_replies = [m for m in results if m.type == "tool" and m.name == "search_news"]
print("메인 Agent 대화에 들어온 하위 Agent 답:", sum(len(str(m.content)) for m in task_replies), "자")
print("메인 Agent 대화에 들어온 검색 원문:", sum(len(str(m.content)) for m in search_replies), "자")
