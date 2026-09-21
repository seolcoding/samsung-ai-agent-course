"""
Harness Engineering 실습

deepagents의 create_deep_agent + skills 디렉토리로 Agent를 빌드하는 예제.

skills/research-writing/SKILL.md 가 Agent의 행동 규칙을 정의한다.
Agent는 description을 보고 이 스킬이 필요한지 판단한 뒤 SKILL.md를 읽어 지시사항을 따른다.

→ SKILL.md만 수정하면 모델·코드 변경 없이 Agent 동작을 조정할 수 있다.
"""

import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from config.llm import get_llm

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

HARNESS_DIR = Path(__file__).parent


# ── 도구 정의 ─────────────────────────────────────────────────────────────────

@tool
def search_web(query: str) -> str:
    """웹에서 주제를 검색한다."""
    # 실제 구현에서는 Tavily, SerpAPI 등을 사용한다.
    return (
        f'[검색: {query}]\n'
        f'- 최근 동향: 빠른 성장세, 기업 도입 증가\n'
        f'- 핵심 기술: 트랜스포머 아키텍처, RLHF, RAG\n'
        f'- 주요 사례: 고객 지원 자동화, 코드 리뷰, 문서 요약\n'
        f'- 시장 규모: 2024년 기준 약 2,000억 달러 (연 30% 성장 예상)'
    )


# ── Agent 생성 ────────────────────────────────────────────────────────────────
# FilesystemBackend: 로컬 파일시스템을 Agent의 작업 공간으로 사용
# skills: SKILL.md 파일이 들어있는 디렉토리 목록 (backend root_dir 기준 상대경로)
#   → Agent는 SKILL.md의 name+description을 보고 "이 스킬이 필요하다" 판단 후 read_file로 상세 지시 로드

# virtual_mode=True: 에이전트에게 가상 경로(/skills/... 등)로 파일시스템을 노출
# ls 결과가 Windows 절대경로 대신 /skills/ 같은 가상경로로 반환되어 경로 혼동 없음
backend = FilesystemBackend(root_dir=str(HARNESS_DIR), virtual_mode=True)

agent = create_deep_agent(
    # TODO: LLM, 사용가능한 도구, 백엔드, 스킬, 시스템 프롬프트를 이용해 Deep Agent를 정의해주세요.
    # 이때, 시스템 프롬프트룰 이용해 범위를 벗어나지 않도록 해주세요.
    model=get_llm(),
    # @tool 데코레이터로 도구 처리된 함수들 리스트로 추가
    tools=[search_web],  # + mcp_tools
    backend=backend,
    skills=['skills/'],
    # skills는 어디까지나, 지금 특정한 요청에 대해서 제어하기 위한 것이지
        # 그 특정 요청을 벗어나는 요청에 대한 제어를 작성하는 것은 아니다.
    # 따라서, skills와 무관한 기본적인 시스템 제어는 평소와 같아...
    system_prompt='코드 작성, 수학 계산 등 보고서 작성과 무관한 요청은 정중히 거절한다.',
    checkpointer=MemorySaver(),
)


# ── 대화형 실행 ───────────────────────────────────────────────────────────────

def chat(session_id: str, message: str) -> str:
    # recursion_limit: LangGraph 노드 실행 횟수 상한 — 기본값 25, 무한루프 방지
    config = {'configurable': {'thread_id': session_id}, 'recursion_limit': 40}
    response = ''
    for chunk in agent.stream(
        {'messages': [HumanMessage(content=message)]},
        config=config,
        stream_mode='values',
    ):
        last_msg = chunk['messages'][-1]
        msg_type = type(last_msg).__name__
        content = last_msg.content or ''
        # 각 단계마다 메시지 타입과 내용 앞부분을 출력해 어디서 멈추는지 확인
        print(f'[{msg_type}] {content[:80]}', flush=True)
    print()
    return response


print('=== Harness Agent (skills/ 디렉토리 기반) ===')
print(f'스킬 경로: {HARNESS_DIR / "skills"}\n')

# 케이스 1: SDS 보고서 양식을 명시 → 모델이 SKILL.md를 읽어야만 형식을 알 수 있음
# 케이스 2: 범위 이탈 → system_prompt로 거절
test_cases = [
    ('session_1', 'AI Agent 최신 트렌드를 삼성SDS 보고서 양식으로 작성해줘.'),
    ('session_2', '파이썬으로 퀵소트 코드를 짜줘.'),
]

for session_id, message in test_cases:
    print(f'사용자: {message}')
    print('Agent: ', end='', flush=True)
    chat(session_id, message)
    print()
