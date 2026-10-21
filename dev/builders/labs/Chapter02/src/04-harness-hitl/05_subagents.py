from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core.tools import tool

from config.llm import get_llm

load_dotenv()


@tool
def search_news(query: str) -> str:
    """반도체 업계 뉴스를 검색한다."""
    # 연습용: 정해 둔 가짜 기사를 돌려준다(약 1,500자)
    articles = [
        "메모리 업계, HBM 생산 능력 확대 계획을 잇달아 발표.",
        "AI 서버 수요로 HBM 공급 부족이 내년까지 이어질 전망.",
        "차세대 HBM은 적층 단수를 늘려 용량을 키우는 방향.",
        "패키징 공정이 HBM 수율의 핵심 변수로 떠오름.",
        "고객사들이 HBM 공급처를 여러 곳으로 나누려는 움직임.",
        "전력 효율이 HBM 경쟁의 새 기준으로 부각.",
    ]
    detail = " 업계 관계자는 수요와 공급, 기술 일정, 고객사 요구를 함께 살펴야 한다고 말했다." * 4
    return "\n".join(f"[기사 {i}] {a}{detail}" for i, a in enumerate(articles, 1))


# ── 하위 Agent 만들고 맡기기 ──
researcher = {
    "name": "researcher",
    "description": "검색이 필요한 조사를 맡는다.",
    "system_prompt": "search_news로 검색하고 핵심만 세 줄로 요약해 돌려준다.",
    "tools": [search_news],  # 검색 도구는 하위 Agent만 가진다
}

agent = create_deep_agent(
    model=get_llm(),
    subagents=[researcher],
    system_prompt="너는 팀장 보고를 돕는 비서다. 조사는 researcher에게 맡기고 받은 내용으로 답한다.",
)

request = "HBM 시장 동향을 세 줄로 요약해 줘."
result = agent.invoke({"messages": [("user", request)]}, version="v2")

# 메인 Agent의 대화
for m in result.value["messages"]:
    print(f"[{m.type}] {m.content[:100]}")

print("\n검색 원문 길이:", len(search_news.invoke("HBM")), "자")
