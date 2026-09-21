"""
캡스톤: 리서치 자동화 멀티에이전트 시스템

4일 과정 통합 실습:
  LangGraph(멀티에이전트·HITL) + create_deep_agent(Harness) + MCP + RAGaaS + Langfuse

흐름:
  사용자 입력 → Supervisor → Researcher(MCP+RAG+웹검색) → [HITL 승인]
               → Writer(SDS 보고서 작성) → 최종 출력

사전 준비:
  터미널 A: python 12-capstone/mcp_server.py   ← MCP 서버 먼저 실행
  터미널 B: python 12-capstone/solution.py

실행:
  python 12-capstone/solution.py
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Annotated, Literal

import requests
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from pydantic import BaseModel
from typing_extensions import TypedDict

from config.llm import get_llm

load_dotenv()

CAPSTONE_DIR = Path(__file__).parent

# ── 도구 정의 ──────────────────────────────────────────────────────────────────
# TODO: 사용할 도구를 정의

@tool
def search_web(query: str) -> str:
    """웹에서 최신 정보를 검색한다."""


@tool
def rag_search(query: str) -> str:
    """내부 지식베이스에서 관련 문서를 검색한다. 삼성 사내망에서는 RAGaaS API를 사용한다."""


# ── State ─────────────────────────────────────────────────────────────────────

# TODO: 필요한 필드를 추가하세요.
class State(TypedDict):
    messages: Annotated[list, add_messages]




# ── 평가 스키마 ───────────────────────────────────────────────────────────────

class EvalDimension(BaseModel):
    score: float  # 0.0 ~ 1.0 (0.1 단위로 엄격 채점)
    reason: str


class ReportEvaluation(BaseModel):
    relevance: EvalDimension     # 주제 관련성
    faithfulness: EvalDimension  # 리서치 근거 충실도
    completeness: EvalDimension  # 보고서 구성 완성도
    clarity: EvalDimension       # 문장·구조 명확성


def evaluate_report(
    topic: str, research: str, report: str, langfuse_client
) -> ReportEvaluation:
    """LLM Judge: 4개 기준으로 보고서를 평가하고 Langfuse에 지표별 점수를 기록한다.

    1.0은 완벽할 때만 — 0.1 단위 엄격 채점으로 의미 있는 점수 분포를 만든다.
    """
    langfuse = get_client()
    langfuse_handler = CallbackHandler()
    langfuse_config = {'callbacks': [langfuse_handler]}

    eval_llm = get_llm().with_structured_output(ReportEvaluation)
    # CallbackHandler가 LLM 호출을 자동으로 트레이스로 기록한다
    eval_handler = CallbackHandler()

    # TODO: 평가를 진행하고 Langfuse에 점수를 기록

# ── Researcher 에이전트 ────────────────────────────────────────────────────

researcher_backend = FilesystemBackend(
    root_dir=str(CAPSTONE_DIR), virtual_mode=True,
)
# TODO: 자료조사 skill을 가진 Researcher Agent


# ── Writer 에이전트 ────────────────────────────────────────────────────────
writer_backend = FilesystemBackend(
    root_dir=str(CAPSTONE_DIR), virtual_mode=True,
)
# TODO: 보고서 작성 skill을 가진 Writer Agent


# ── LangGraph 노드 정의 ────────────────────────────────────────────────────
class RouteDecision(BaseModel):
    next: Literal['researcher', 'writer', 'END']
    reason: str


# TODO: Supervisor 노드 정의
supervisor_llm = get_llm().with_structured_output(RouteDecision)


def supervisor_node(state: State) -> dict:
    pass


# TODO: Researcher 노드 정의
async def researcher_node(state: State) -> dict:
    pass


# TODO: Writer 노드 정의
async def writer_node(state: State) -> dict:
    pass


def route(state: State) -> str:
    return state.get('next', 'END')


builder = StateGraph(State)
builder.add_node('supervisor', supervisor_node)
builder.add_node('researcher', researcher_node)
builder.add_node('writer', writer_node)
# TODO: 그래프 조립 

app = builder.compile()


# ── 메인 함수 (async: MCP 클라이언트가 비동기) ──────────────────────────────────

async def main(topic: str):
    

    config = {'configurable': {'thread_id': 'capstone-session'}}
    initial_state = {
        'messages': [],
    }

    # TODO: app.invoke로 실행하고 단계접 진행 상황 출력


if __name__ == '__main__':
    asyncio.run(main('생성형 AI가 바꾸는 소프트웨어 개발의 미래'))
