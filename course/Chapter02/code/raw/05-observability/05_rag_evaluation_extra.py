"""
RAG 파이프라인 다차원 평가 (Extra)

구조:
  1. @observe로 retrieve → generate 단계를 각각 span으로 기록
  2. LLM Judge가 정확성·관련성·완성도 3개 차원을 독립적으로 채점
  3. 의도적으로 오염된 컨텍스트를 섞어 점수가 실제로 달라지는 것을 확인

점수가 달라지는 이유:
  - CASE A: 정확한 컨텍스트 → 고득점
  - CASE B: 빈 컨텍스트 (검색 실패 시뮬레이션) → 낮은 관련성
  - CASE C: 오염된 컨텍스트 (엉뚱한 문서) → 낮은 정확성

실행:
  python course/Chapter02/code/raw/05-observability/05_rag_evaluation_extra.py
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langfuse import get_client, observe
from langfuse.langchain import CallbackHandler
from pydantic import BaseModel, Field

from config.llm import get_llm

load_dotenv()

langfuse = get_client()
llm = get_llm()


# ── 가상 문서 저장소 ────────────────────────────────────────────────────────────
DOCS = {
    'langgraph': (
        'LangGraph는 LangChain 위에서 동작하는 상태 기반 멀티에이전트 프레임워크다. '
        'StateGraph로 노드(함수)와 엣지(전환 조건)를 정의하며, MemorySaver로 체크포인트를 저장한다. '
        'LangChain 0.x의 AgentExecutor를 대체하며 복잡한 루프·분기 흐름을 지원한다.'
    ),
    'rag': (
        'RAG(Retrieval-Augmented Generation)는 외부 문서를 검색해 LLM의 답변 근거로 활용하는 기법이다. '
        '벡터 임베딩으로 유사 문서를 찾고, 해당 내용을 프롬프트 컨텍스트에 삽입한다. '
        '환각(hallucination)을 줄이고 최신 정보를 반영할 수 있다는 장점이 있다.'
    ),
    'noise': (
        '오늘 서울 날씨는 맑고 기온은 23도이다. '
        '내일은 구름이 많고 오후에 비가 올 수 있다. '
        '주말에는 기온이 낮아질 전망이다.'
    ),
}


# ── 평가 결과를 구조화하기 위한 Pydantic 모델 ──────────────────────────────────
class EvalScore(BaseModel):
    correctness: float = Field(description='사실 정확성 0.0~1.0')
    relevance: float = Field(description='질문과의 관련성 0.0~1.0')
    completeness: float = Field(description='답변 완성도 0.0~1.0')
    reason: str = Field(description='채점 근거 한 줄')


# ── RAG 단계별 함수 ─────────────────────────────────────────────────────────────

@observe(name='retrieve')
def retrieve(query: str, doc_key: str) -> str:
    """doc_key로 문서를 가져온다. 실제 환경에서는 벡터 검색으로 대체."""
    return DOCS.get(doc_key, '')


@observe(name='generate')
def generate(question: str, context: str, handler: CallbackHandler) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ('system', '아래 컨텍스트만 참고해 질문에 답하세요. 컨텍스트가 없으면 모른다고 하세요.\n\n{context}'),
        ('human', '{question}'),
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke(
        {'context': context, 'question': question},
        config={'callbacks': [handler]},
    )


@observe(name='rag-pipeline')
def rag_pipeline(question: str, doc_key: str, handler: CallbackHandler) -> tuple[str, str]:
    context = retrieve(question, doc_key)
    answer = generate(question, context, handler)
    return answer, context


# ── LLM Judge ──────────────────────────────────────────────────────────────────

def judge(question: str, context: str, answer: str) -> EvalScore:
    # structured output: LLM이 EvalScore 형식으로만 응답하도록 강제
    judge_llm = llm.with_structured_output(EvalScore)
    prompt = ChatPromptTemplate.from_messages([
        ('system',
         '질문, 참고 컨텍스트, 답변을 보고 3개 항목을 0.0~1.0으로 채점하세요.\n'
         '- correctness: 컨텍스트 기준으로 답변이 사실적으로 맞는지\n'
         '- relevance: 답변이 질문에 직접 답하는지\n'
         '- completeness: 컨텍스트의 핵심 정보를 빠짐없이 담았는지'),
        ('human', '질문: {question}\n\n컨텍스트: {context}\n\n답변: {answer}'),
    ])
    chain = prompt | judge_llm
    return chain.invoke({'question': question, 'context': context, 'answer': answer})


# ── 테스트 케이스 ───────────────────────────────────────────────────────────────

test_cases = [
    {
        'name': 'CASE A — 정확한 컨텍스트',
        'question': 'LangGraph가 뭔가요?',
        'doc_key': 'langgraph',   # 정확한 문서
    },
    {
        'name': 'CASE B — 빈 컨텍스트 (검색 실패)',
        'question': 'RAG의 장점은 무엇인가요?',
        'doc_key': 'missing',     # 존재하지 않는 키 → 빈 컨텍스트
    },
    {
        'name': 'CASE C — 오염된 컨텍스트 (엉뚱한 문서)',
        'question': 'RAG가 환각을 줄이는 원리를 설명해줘',
        'doc_key': 'noise',       # 날씨 문서 → 완전히 엉뚱함
    },
]


print('=== RAG 파이프라인 다차원 평가 ===\n')

for case in test_cases:
    print(f"[{case['name']}]")
    print(f"Q: {case['question']}")

    handler = CallbackHandler()
    answer, context = rag_pipeline(case['question'], case['doc_key'], handler)
    trace_id = handler.last_trace_id

    print(f"A: {answer[:120]}{'...' if len(answer) > 120 else ''}")

    # 3개 차원 채점
    score = judge(case['question'], context, answer)
    print(f"채점 → 정확성: {score.correctness:.1f} | 관련성: {score.relevance:.1f} | 완성도: {score.completeness:.1f}")
    print(f"근거: {score.reason}")

    # Langfuse에 차원별 점수 기록
    for name, value in [
        ('correctness', score.correctness),
        ('relevance', score.relevance),
        ('completeness', score.completeness),
    ]:
        langfuse.create_score(trace_id=trace_id, name=name, value=value)

    print()

langfuse.flush()
print('✓ 대시보드 [Scores] 탭에서 케이스별 차이를 확인하세요.')
