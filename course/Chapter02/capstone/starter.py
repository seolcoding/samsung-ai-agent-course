"""
캡스톤: 리서치 자동화 멀티에이전트 시스템

4일 과정 통합 실습:
  LangGraph(멀티에이전트·HITL) + create_deep_agent(Harness) + MCP + RAGaaS + Langfuse

흐름:
  사용자 입력 → Supervisor → Researcher(MCP+RAG+웹검색) → [HITL 승인]
               → Writer(SDS 보고서 작성) → 최종 출력

실행 (저장소 맨 위에서, 터미널 두 개):
  터미널 A: uv run python course/Chapter02/capstone/mcp_server.py   ← MCP 서버 먼저
  터미널 B: uv run python course/Chapter02/capstone/starter.py

starter.py는 구현할 부분(TODO)이 남아 있는 실습 뼈대다. AI와 함께 TODO를 채운다.
사내망 밖(.env의 COURSE_ENV=out)에서는 RAGaaS가 네트워크 없이 모의 응답을 돌려준다.
"""

import asyncio
import os
from pathlib import Path
from typing import Annotated, Literal

import truststore

truststore.inject_into_ssl()  # PC에 등록된 인증서(회사 인증서 포함)를 믿게 합니다. Langfuse보다 먼저 둡니다(지우지 않습니다)

from deepagents import create_deep_agent  # noqa: E402
from deepagents.backends import FilesystemBackend  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from langchain_mcp_adapters.client import MultiServerMCPClient  # noqa: E402
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.graph.message import add_messages  # noqa: E402
from langfuse import get_client  # noqa: E402
from langfuse.langchain import CallbackHandler  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from typing_extensions import TypedDict  # noqa: E402

from config.llm import get_llm  # noqa: E402
from config.ragaas import post_ragaas  # noqa: E402

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
    # TODO: post_ragaas('retrieve-rrf', payload)를 Coding AI에게 구현하게 하고
    # 사내망 밖(.env의 COURSE_ENV=out)에서 결과에 [MOCK RAGaaS]가 표시되는지 검토하세요.


# ── State ─────────────────────────────────────────────────────────────────────

# TODO: 필요한 필드를 추가하세요.
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ── Supervisor 라우팅 스키마 ───────────────────────────────────────────────────

class RouteDecision(BaseModel):
    next: Literal['researcher', 'writer', 'END']
    reason: str


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
    eval_llm = get_llm().with_structured_output(ReportEvaluation)
    # CallbackHandler가 LLM 호출을 자동으로 트레이스로 기록한다
    eval_handler = CallbackHandler()

    # TODO: 평가를 진행하고 Langfuse에 점수를 기록


# ── 메인 함수 (async: MCP 클라이언트가 비동기) ──────────────────────────────────
# MCP 도구는 서버에서 비동기로 받아 오므로, Agent·노드·그래프를 모두 main() 안에서 만든다.

async def main(topic: str):
    langfuse = get_client()
    langfuse_handler = CallbackHandler()
    langfuse_config = {'callbacks': [langfuse_handler]}

    # ── MCP 클라이언트 연결 ────────────────────────────────────────────────────
    # mcp_server.py가 먼저 실행돼 있어야 한다 (http://localhost:8001/sse)
    # TODO: MCP 서버에 연결해 도구 목록(mcp_tools)을 받아 오고, 받은 도구 이름을 출력

    # ── Researcher 에이전트 ────────────────────────────────────────────────────
    # virtual_mode=True: Windows 경로 문제 없이 /skills/ 가상경로로 파일 접근
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

    # ── 그래프 조립 ────────────────────────────────────────────────────────────
    builder = StateGraph(State)
    builder.add_node('supervisor', supervisor_node)
    builder.add_node('researcher', researcher_node)
    builder.add_node('writer', writer_node)
    # TODO: 그래프 조립
    builder.add_edge(START, 'supervisor')  # 자리표시: 연결이 하나도 없으면 compile()이 멈춰서 시작 연결만 넣어 둠. 나머지 연결을 이어서 넣습니다

    app = builder.compile()

    config = {'configurable': {'thread_id': 'capstone-session'}}
    initial_state = {
        'messages': [],
    }

    # TODO: app.ainvoke로 실행하고 단계별 진행 상황 출력
    print('⚠️ 실행 코드(6.6)가 아직 비어 있어 여기서 끝납니다. 4-3 LAB 6장을 따라 TODO를 채웁니다.')  # 자리표시: 6.6을 채울 때 이 줄을 지웁니다


if __name__ == '__main__':
    asyncio.run(main('생성형 AI가 바꾸는 소프트웨어 개발의 미래'))
