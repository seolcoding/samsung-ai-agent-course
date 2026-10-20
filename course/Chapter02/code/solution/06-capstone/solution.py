"""
캡스톤: 리서치 자동화 멀티에이전트 시스템

4일 과정 통합 실습:
  LangGraph(멀티에이전트·HITL) + create_deep_agent(Harness) + MCP + RAGaaS + Langfuse

흐름:
  사용자 입력 → Supervisor → Researcher(MCP+RAG+웹검색) → [HITL 승인]
               → Writer(DS 보고서 작성) → 최종 출력

사전 준비:
  터미널 A: python course/Chapter02/code/solution/06-capstone/mcp_server.py   ← MCP 서버 먼저 실행
  터미널 B: python course/Chapter02/code/solution/06-capstone/solution.py

실행:
  python course/Chapter02/code/solution/06-capstone/solution.py
"""

import asyncio
import os
from pathlib import Path
from typing import Annotated, Literal

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
import config  # noqa: F401  .env의 COURSE_ENV(사내/사외)에 맞춰 연결 방식을 채운다
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
from config.ragaas import post_ragaas

load_dotenv()

CAPSTONE_DIR = Path(__file__).parent

# ── 도구 정의 ──────────────────────────────────────────────────────────────────

@tool
def search_web(query: str) -> str:
    """웹에서 최신 정보를 검색한다."""
    # 실제 환경에서는 Tavily, SerpAPI 등으로 교체
    return (
        f'[웹 검색: {query}]\n'
        f'- AI Agent 시장 2025년 기준 연 46% 성장\n'
        f'- LangGraph, CrewAI 등 멀티에이전트 프레임워크 기업 도입 급증\n'
        f'- RAG + Agent 결합 아키텍처가 사실상 표준으로 자리잡음\n'
        f'- 삼성·LG·SK 등 대기업 사내 AI Agent 파일럿 전면 확대'
    )


@tool
def rag_search(query: str) -> str:
    """사내 RAGaaS 또는 모의 응답에서 문서를 검색한다."""
    provider = os.getenv('RAG_PROVIDER', 'samsung').strip().lower()
    index_name = os.getenv('index_name') or ('mock-capstone' if provider == 'mock' else '')
    if not index_name:
        raise RuntimeError('사내 RAGaaS에는 index_name 환경변수가 필요합니다.')
    payload = {
        'index_name': index_name,
        'permission_groups': ['rag-public'],
        'query_text': query,
        'num_result_doc': 3,
        'fields_exclude': ['v_merge_title_content'],
    }
    response = post_ragaas('retrieve-rrf', payload)
    hits = response.json()['hits']['hits']
    if not hits:
        return 'RAGaaS 검색 결과 없음'
    return '\n\n'.join(hit['_source']['merge_title_content'] for hit in hits)


# ── State ─────────────────────────────────────────────────────────────────────

class State(TypedDict):
    messages: Annotated[list, add_messages]
    topic: str
    research_result: str
    draft: str
    next: str


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

    evaluation: ReportEvaluation = eval_llm.invoke(
        [HumanMessage(content=(
            '당신은 보고서 품질 평가 전문가다. 아래 보고서를 4개 기준으로 각각 0.0~1.0 점수로 평가하라.\n'
            '0.1 단위로 채점하고, 1.0은 완벽할 때만 부여한다. 근거 없이 높은 점수를 주지 마라.\n\n'
            f'## 주제\n{topic}\n\n'
            f'## 리서치 원문 (근거 자료)\n{research[:2000]}\n\n'
            f'## 평가 대상 보고서\n{report[:3000]}\n\n'
            '## 평가 기준 (각각 독립 채점)\n'
            '- relevance: 보고서가 주제를 정확히 다루는가. 주제 이탈·무관한 내용 포함 시 감점\n'
            '- faithfulness: 리서치 원문에 근거했는가. 원문에 없는 사실 포함 시 크게 감점\n'
            '- completeness: 서론·본론·결론, 데이터·근거, 시사점이 모두 갖춰졌는가\n'
            '- clarity: 문장이 간결·명확하고 구조가 읽기 쉬운가. 두루뭉술한 서술 시 감점\n'
        ))],
        config={'callbacks': [eval_handler]},
    )

    # last_trace_id: CallbackHandler가 기록한 트레이스에 지표별 점수를 추가한다
    trace_id = eval_handler.last_trace_id
    for dim_name, dim in [
        ('relevance',    evaluation.relevance),
        ('faithfulness', evaluation.faithfulness),
        ('completeness', evaluation.completeness),
        ('clarity',      evaluation.clarity),
    ]:
        langfuse_client.create_score(
            trace_id=trace_id,
            name=dim_name,
            value=dim.score,
            comment=dim.reason,
        )

    return evaluation


# ── 메인 함수 (async: MCP 클라이언트가 비동기) ──────────────────────────────────

async def main(topic: str):
    langfuse = get_client()
    langfuse_handler = CallbackHandler()
    langfuse_config = {'callbacks': [langfuse_handler]}

    # ── MCP 클라이언트 연결 ────────────────────────────────────────────────────
    # mcp_server.py 가 먼저 실행돼 있어야 한다
    mcp_client = MultiServerMCPClient({
        'capstone': {'transport': 'sse', 'url': 'http://localhost:8001/sse'},
    })
    mcp_tools = await mcp_client.get_tools()
    print(f'MCP 도구 로드: {[t.name for t in mcp_tools]}\n')

    # ── Researcher 에이전트 ────────────────────────────────────────────────────
    # virtual_mode=True: Windows 경로 문제 없이 /skills/ 가상경로로 파일 접근
    researcher_backend = FilesystemBackend(
        root_dir=str(CAPSTONE_DIR), virtual_mode=True,
    )
    researcher = create_deep_agent(
        model=get_llm(),
        tools=[search_web, rag_search, *mcp_tools],
        backend=researcher_backend,
        skills=['skills/researcher/'],
        system_prompt='주어진 주제를 리서치하고 결과를 정리하는 역할만 수행한다. 보고서 작성은 하지 않는다.',
        checkpointer=MemorySaver(),
    )

    # ── Writer 에이전트 ────────────────────────────────────────────────────────
    writer_backend = FilesystemBackend(
        root_dir=str(CAPSTONE_DIR), virtual_mode=True,
    )
    writer = create_deep_agent(
        model=get_llm(),
        tools=[],
        backend=writer_backend,
        skills=['skills/ds-report-writer/'],
        system_prompt='제공된 리서치 결과를 삼성전자 DS부문 보고서 양식으로 작성하는 역할만 수행한다.',
        checkpointer=MemorySaver(),
    )

    # ── LangGraph 노드 정의 ────────────────────────────────────────────────────

    supervisor_llm = get_llm().with_structured_output(RouteDecision)

    def supervisor_node(state: State) -> dict:
        situation = (
            f'주제: {state["topic"]}\n'
            f'리서치 완료: {"예" if state.get("research_result") else "아니오"}\n'
            f'초안 완료: {"예" if state.get("draft") else "아니오"}'
        )
        decision = supervisor_llm.invoke([
            HumanMessage(content=(
                f'현재 상황:\n{situation}\n\n'
                '다음 중 하나를 결정하라:\n'
                '- researcher: 리서치가 필요한 경우\n'
                '- writer: 리서치는 완료됐고 보고서 작성이 필요한 경우\n'
                '- END: 보고서까지 완료된 경우'
            ))
        ])
        return {'next': decision.next}

    async def researcher_node(state: State) -> dict:
        print('🔍 Researcher 실행 중...')
        result = await researcher.ainvoke(
            {'messages': [HumanMessage(content=f'다음 주제를 리서치하라: {state["topic"]}')]},
            config={'configurable': {'thread_id': f'researcher-{state["topic"][:20]}'}, **langfuse_config},
        )
        research_result = result['messages'][-1].content
        return {'research_result': research_result}

    async def writer_node(state: State) -> dict:
        print('✍️  Writer 실행 중...')
        result = await writer.ainvoke(
            {'messages': [HumanMessage(
                content=f'아래 리서치 결과로 보고서를 작성하라:\n\n{state["research_result"]}'
            )]},
            config={'configurable': {'thread_id': f'writer-{state["topic"][:20]}'}, **langfuse_config},
        )
        draft = result['messages'][-1].content
        return {'draft': draft}

    def route(state: State) -> str:
        return state.get('next', 'END')

    # ── 그래프 조립 ────────────────────────────────────────────────────────────
    builder = StateGraph(State)
    builder.add_node('supervisor', supervisor_node)
    builder.add_node('researcher', researcher_node)
    builder.add_node('writer', writer_node)

    builder.add_edge(START, 'supervisor')
    builder.add_conditional_edges('supervisor', route, {
        'researcher': 'researcher',
        'writer': 'writer',
        'END': END,
    })
    # 각 에이전트 완료 후 다시 Supervisor로 복귀
    builder.add_edge('researcher', 'supervisor')
    builder.add_edge('writer', 'supervisor')

    # interrupt_before=['writer']: 리서치 완료 후 사용자가 승인해야 Writer 실행
    app = builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=['writer'],
    )

    config = {'configurable': {'thread_id': 'capstone-session'}}
    initial_state = {
        'messages': [],
        'topic': topic,
        'research_result': '',
        'draft': '',
        'next': '',
    }

    # ── 1단계: Supervisor → Researcher 실행 후 HITL에서 중단 ──────────────────
    print(f'=== 캡스톤: {topic} ===\n')
    print('--- 1단계: 리서치 ---')
    await app.ainvoke(initial_state, config=config)

    # 리서치 결과 출력
    snapshot = app.get_state(config)
    research = snapshot.values.get('research_result', '')
    print(f'\n리서치 결과:\n{research[:500]}...\n' if len(research) > 500 else f'\n리서치 결과:\n{research}\n')

    # ── HITL: 사용자 승인 ──────────────────────────────────────────────────────
    approval = input('보고서 작성을 시작할까요? (y/n): ').strip().lower()
    if approval != 'y':
        print('취소됐습니다.')
        langfuse.flush()
        return

    # ── 2단계: Writer 실행 → 최종 보고서 ──────────────────────────────────────
    print('\n--- 2단계: 보고서 작성 ---')
    # None 전달: 중단된 지점부터 재개
    await app.ainvoke(None, config=config)

    final = app.get_state(config).values.get('draft', '')
    print(f'\n{"="*60}')
    print(final)
    print('='*60)

    # ── 3단계: LLM Judge 평가 ──────────────────────────────────────────────────
    print('\n--- 3단계: 보고서 평가 (LLM Judge) ---')
    evaluation = evaluate_report(topic, research, final, langfuse)

    dims = [
        ('관련성   ', evaluation.relevance),
        ('근거충실도', evaluation.faithfulness),
        ('완성도   ', evaluation.completeness),
        ('명확성   ', evaluation.clarity),
    ]
    avg = sum(d.score for _, d in dims) / len(dims)

    print()
    for label, dim in dims:
        filled = round(dim.score * 10)
        bar = '█' * filled + '░' * (10 - filled)
        print(f'  {label}  {bar}  {dim.score:.1f}  {dim.reason}')
    print(f'  {"─"*58}')
    print(f'  종합 점수  {"─"*20}  {avg:.2f} / 1.0')

    langfuse.flush()
    print('\n✓ Langfuse 대시보드에서 전체 실행 흐름과 평가 점수를 확인하세요.')


if __name__ == '__main__':
    asyncio.run(main('생성형 AI가 바꾸는 소프트웨어 개발의 미래'))
