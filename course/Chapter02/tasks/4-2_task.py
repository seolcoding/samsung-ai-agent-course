"""4-2 과제 · 기록과 점수가 남는 체인

▶️ 실행   uv run --env-file .env python course/Chapter02/tasks/4-2_task.py
✅ 확인   실행하면 맨 끝에 🟢/⛔가 나옵니다
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""

import time
from pathlib import Path

import truststore

truststore.inject_into_ssl()  # PC에 등록된 인증서(회사 인증서 포함)를 믿게 합니다. Langfuse보다 먼저 둡니다

from dotenv import load_dotenv  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langfuse import get_client  # noqa: E402
from langfuse.langchain import CallbackHandler  # noqa: E402

from config.llm import get_llm  # noqa: E402

load_dotenv()
langfuse = get_client()
llm = get_llm()

QUESTION = "RAG를 한 문장으로 설명해줘"

chain = ChatPromptTemplate.from_messages([
    ("system", "한국어로 3문장 이내로 답하세요."),
    ("human", "{question}"),
]) | llm | StrOutputParser()

# 답변이 질문에 직접 답했는지 0.0~1.0 숫자 하나로 매기는 채점 체인
judge_chain = ChatPromptTemplate.from_messages([
    ("system", "아래 답변이 질문에 직접 답했는지 0.0~1.0 사이 숫자 하나만 출력하세요."),
    ("human", "질문: {question}\n답변: {answer}"),
]) | llm | StrOutputParser()


print("=== 1. trace 남기기 ===")
# ✍️ 1. 체인 실행을 Langfuse trace로 남기기
# ✨ CallbackHandler() · chain.invoke(QUESTION, config callbacks) → answer · trace_id = handler.last_trace_id · 답과 "trace id:" 출력
print("(1. 아직 작성하지 않았습니다)")


print("\n=== 2. 점수 남기기 ===")
# ✍️ 2. 그 trace에 점수 두 개 남기기
# ✨ short-answer: 200자 이하 1.0 · llm-judge: judge_chain → float(못 바꾸면 0.0) · langfuse.create_score(trace_id=trace_id) 두 번 · 점수 출력
print("(2. 아직 작성하지 않았습니다)")


langfuse.flush()  # 모아 둔 기록과 점수를 Langfuse로 보냅니다


# ── ✅ 확인 (바꾸지 않습니다) ──
print("\n✅ 확인")
tid = globals().get("trace_id")
todo_2 = 'print("(2. 아직 작성하지 않았습니다)")' in [line.strip() for line in Path(__file__).read_text(encoding="utf-8").splitlines()]
names, scores, error = [], [], ""
for _ in range(6 if isinstance(tid, str) else 0):  # 기록은 몇 초 늦게 도착합니다(최대 30초 기다림)
    try:
        names = [o.name for o in langfuse.api.observations.get_many(trace_id=tid, limit=50).data]
        scores = [s for s in langfuse.api.scores_v3.get_many_v3(trace_id=tid).data if 0 <= s.value <= 1]
    except Exception as e:  # 연결·권한 문제는 아래에서 ❔로 알립니다
        error = f"{type(e).__name__}: {str(e)[:80]}"
        break
    if names and (todo_2 or {"short-answer", "llm-judge"} <= {s.name for s in scores}):
        break
    time.sleep(5)
if not isinstance(tid, str):
    print("⛔ 1. 아직 작성하지 않았습니다")
elif not names:
    print(f"❔ 1. Langfuse에서 trace {tid}를 찾지 못했습니다({error or '30초 안에 도착하지 않음'})")
else:
    print("🟢 1. 체인 실행이 trace로 남았습니다" if "RunnableSequence" in names else "⛔ 1. trace에 체인 실행이 없습니다(callbacks를 확인합니다)")
if todo_2 or not isinstance(tid, str):
    print("⛔ 2. 아직 작성하지 않았습니다")
elif {"short-answer", "llm-judge"} <= {s.name for s in scores}:
    print("🟢 2. trace에 short-answer와 llm-judge 점수(0~1)가 남았습니다")
else:
    print(f"❔ 2. Langfuse에서 점수를 조회하지 못했습니다({error})" if error else "⛔ 2. trace에 0~1 점수 두 개(short-answer, llm-judge)가 없습니다")
