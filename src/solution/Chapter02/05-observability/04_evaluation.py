"""
평가(Evaluation): LLM 응답에 점수 매기기

핵심 개념:
  - 트레이싱만으로는 '답변이 좋은지 나쁜지' 알 수 없다.
  - score()로 각 트레이스에 점수를 남기면 품질 추세를 정량적으로 추적할 수 있다.
  - 평가 방식 3가지:
      1. 수동 평가  — 사람이 직접 점수 입력
      2. 규칙 기반  — 길이·키워드 포함 여부 등 코드로 판단
      3. LLM 평가   — 다른 LLM이 응답 품질을 채점 (LLM-as-a-Judge)

실행:
  python src/solution/Chapter02/05-observability/04_evaluation.py
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langfuse import get_client
from langfuse.langchain import CallbackHandler

from config.llm import get_llm

load_dotenv()

langfuse = get_client()
llm = get_llm()


def run_chain(question: str, handler: CallbackHandler) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ('system', '한국어로 간결하게 답변하세요. 반드시 예시를 포함하세요.'),
        ('human', '{question}'),
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({'question': question}, config={'callbacks': [handler]})


# ── 1. 규칙 기반 평가 ──────────────────────────────────────────────────────────
print('=== 규칙 기반 평가 ===')
handler1 = CallbackHandler()
question1 = 'Python 리스트와 튜플의 차이를 설명해줘'
answer1 = run_chain(question1, handler1)
print(f'답변: {answer1}\n')

# get_trace_id(): 직전 invoke에서 생성된 trace의 ID를 반환
trace_id1 = handler1.last_trace_id

# 예시 포함 여부를 규칙으로 판단해 점수 부여
has_example = any(keyword in answer1 for keyword in ['예:', '예를 들어', '예시', '[', '('])
langfuse.create_score(
    trace_id=trace_id1,
    name='has-example',        # 대시보드에 표시될 평가 항목 이름
    value=1.0 if has_example else 0.0,
    comment='예시 포함 여부 자동 검사',
)
print(f'예시 포함 여부: {"✓" if has_example else "✗"} (score={1.0 if has_example else 0.0})')
print()


# ── 2. LLM-as-a-Judge 평가 ────────────────────────────────────────────────────
# 별도 LLM이 응답 품질을 0~1로 채점 — 사람 평가 없이 대규모 자동 평가에 사용
print('=== LLM-as-a-Judge 평가 ===')
handler2 = CallbackHandler()
question2 = '딥러닝이란 무엇인가요?'
answer2 = run_chain(question2, handler2)
print(f'답변: {answer2}\n')

trace_id2 = handler2.last_trace_id

judge_prompt = ChatPromptTemplate.from_messages([
    ('system', '아래 답변의 품질을 0.0~1.0 사이 숫자 하나만 출력하세요. 다른 텍스트는 출력하지 마세요.'),
    ('human', '질문: {question}\n답변: {answer}'),
])
judge_chain = judge_prompt | llm | StrOutputParser()

# judge LLM 호출은 평가용이므로 별도 트레이스로 기록하지 않음 (callbacks 미전달)
score_str = judge_chain.invoke({'question': question2, 'answer': answer2})
try:
    score_value = max(0.0, min(1.0, float(score_str.strip())))
except ValueError:
    score_value = 0.5

langfuse.create_score(
    trace_id=trace_id2,
    name='llm-judge-quality',
    value=score_value,
    comment=f'LLM 자동 채점: {score_str.strip()}',
)
print(f'LLM 채점 점수: {score_value}')
print()


# ── 3. 수동 평가 시뮬레이션 ────────────────────────────────────────────────────
# 실제 서비스에서는 사용자 피드백(좋아요/싫어요)을 받아 score()로 기록
print('=== 수동 평가 시뮬레이션 ===')
handler3 = CallbackHandler()
answer3 = run_chain('강화학습을 쉽게 설명해줘', handler3)
trace_id3 = handler3.last_trace_id

# 사용자가 👍를 눌렀다고 가정
user_feedback = 1.0
langfuse.create_score(
    trace_id=trace_id3,
    name='user-feedback',
    value=user_feedback,
    comment='사용자 좋아요',
)
print(f'답변: {answer3}')
print(f'사용자 평가: 👍 (score={user_feedback})')
print()

langfuse.flush()
print('✓ 대시보드 [Scores] 탭에서 평가 결과를 확인하세요.')
