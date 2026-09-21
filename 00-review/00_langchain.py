from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from config.llm import get_llm

load_dotenv()


llm = get_llm()

# ── 기본 invoke ───────────────────────────────────────────────────────────────
# SystemMessage: LLM의 역할/행동 지침 설정
# HumanMessage: 사용자 입력
messages = [
    SystemMessage(content='너는 초보자를 위한 AI 튜터야.'),
    HumanMessage(content='LLM이 무엇인지 3문장으로 설명해줘.'),
]

response = llm.invoke(messages)
print(response.content)
print()

# ── Streaming ─────────────────────────────────────────────────────────────────
# stream()은 토큰 단위로 응답을 yield함
# end='' 로 줄바꿈 없이 실시간 출력
for chunk in llm.stream(messages):
    print(chunk.content, end='', flush=True)
print()
