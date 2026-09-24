"""조사→승인→작성→검토를 실제 LangGraph로 실행하는 교육용 캡스톤."""

import operator
import re
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from fastmcp import Client
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from pydantic import BaseModel

from courseware.knowledge import retrieve
from courseware.mcp_server import build_mcp


class ReportState(TypedDict, total=False):
    topic: str
    evidence: list[dict]
    approved: bool
    report: str
    writer_executed: bool
    evaluation: dict
    next: str
    reason: str
    trace: Annotated[list[str], operator.add]


class RouteDecision(BaseModel):
    next: Literal["research", "approval", "writer", "evaluate", "FINISH"]
    reason: str


def evaluate_report(report: str, evidence: list[dict]) -> dict:
    """형식과 출처 ID를 검사한다. 의미상 근거 충실성은 사람이 별도로 검토한다."""
    expected = {d["id"] for d in evidence}
    cited = set(re.findall(r"\[(D\d+)\]", report))
    sections = ["## 핵심 내용", "## 근거", "## 한계"]
    return {
        "structure": sum(title in report for title in sections) / len(sections),
        "citation_validity": bool(cited) and cited <= expected,
        "unknown_citations": sorted(cited - expected),
        "faithfulness": "사람의 내용 검토 필요",
    }


def build_capstone(*, use_mcp: bool = True, live_model=None):
    """live_model=None이면 원문을 발췌해 보고서를 만든다. 자동 외부 호출은 없다."""

    def supervise(state: ReportState):
        if "evidence" not in state:
            choice, reason = "research", "먼저 근거를 조사합니다."
        elif not state["evidence"]:
            choice, reason = "FINISH", "근거가 없어 작성하지 않습니다."
        elif "approved" not in state:
            choice, reason = "approval", "작성 전에 근거를 확인받습니다."
        elif not state["approved"]:
            choice, reason = "FINISH", "사용자가 작성을 거절했습니다."
        elif not state.get("writer_executed"):
            choice, reason = "writer", "승인된 근거로 작성합니다."
        elif not state.get("evaluation"):
            choice, reason = "evaluate", "형식과 출처를 검사합니다."
        else:
            choice, reason = "FINISH", "검사를 마쳤습니다. 내용은 사람이 검토합니다."
        decision = RouteDecision(next=choice, reason=reason)
        return {**decision.model_dump(), "trace": [f"supervisor:{choice}"]}

    async def research(state: ReportState):
        if use_mcp:
            async with Client(build_mcp()) as client:
                result = await client.call_tool("search_knowledge", {"query": state["topic"], "k": 3})
            evidence = result.data
        else:
            evidence = retrieve(state["topic"], k=3)
        return {"evidence": evidence, "writer_executed": False, "report": "", "trace": ["research:mcp" if use_mcp else "research:local"]}

    def approve(state: ReportState):
        if not state["evidence"]:
            return {"approved": False, "trace": ["approval:no-evidence"]}
        decision = interrupt({"question": "이 근거로 보고서를 작성할까요?", "evidence": state["evidence"]})
        if not isinstance(decision, dict) or type(decision.get("approved")) is not bool:
            raise ValueError("승인값은 {'approved': True} 또는 {'approved': False}여야 합니다.")
        return {"approved": decision["approved"], "trace": [f'approval:{decision["approved"]}']}

    async def write(state: ReportState):
        evidence = state["evidence"]
        if live_model is not None:
            rules = (Path(__file__).parent / "skills/report/SKILL.md").read_text(encoding="utf-8")
            context = "\n".join(f'[{d["id"]}] {d["text"]}' for d in evidence)
            result = await live_model.ainvoke([
                ("system", rules + "\n소제목은 '## 핵심 내용', '## 근거', '## 한계'를 사용하세요."),
                ("human", f'작성 승인: True\n주제: {state["topic"]}\n근거:\n{context}'),
            ])
            report = str(result.content)
        else:
            excerpts = "\n".join(f'- {d["text"]} [{d["id"]}]' for d in evidence)
            sources = "\n".join(f'- [{d["id"]}] {d["title"]} — {d["source"]}' for d in evidence)
            report = f'# {state["topic"]}\n\n## 핵심 내용\n{excerpts}\n\n## 근거\n{sources}\n\n## 한계\n교육용 모의 자료를 원문 발췌한 보고서입니다. 실제 회사 정책이나 최신 시장 조사 결과가 아닙니다.'
        return {"report": report, "writer_executed": True, "trace": ["writer:live" if live_model is not None else "writer:extractive"]}

    def evaluate(state: ReportState):
        return {"evaluation": evaluate_report(state["report"], state["evidence"]), "trace": ["evaluate:rules"]}

    graph = StateGraph(ReportState)
    graph.add_node("supervisor", supervise)
    graph.add_node("research", research)
    graph.add_node("approval", approve)
    graph.add_node("writer", write)
    graph.add_node("evaluate", evaluate)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", lambda s: s["next"], {
        "research": "research", "approval": "approval", "writer": "writer",
        "evaluate": "evaluate", "FINISH": END,
    })
    for step in ["research", "approval", "writer", "evaluate"]:
        graph.add_edge(step, "supervisor")
    return graph.compile(checkpointer=InMemorySaver())
