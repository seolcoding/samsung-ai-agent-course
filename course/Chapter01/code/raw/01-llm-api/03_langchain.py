from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from config.llm import get_llm

load_dotenv()

# 핵심은 llm 을 사용해서 답변을 만들어 내는 것.
    # ai에게 어떤 지시를 내리고, 답변을 받을 수 있어야 한다는 것.
    # AI에게 어떤 지시를 내린다 -> 채팅창에 시킬일을 적는다.
        # AI API등을 사용할떄는 그 지시조차도 구분해야한다. 사용자가 질문하고 싶은 것, 시스템적으로 지시하고 싶은것 (프롬프트)
llm = get_llm()

# ── 기본 invoke ───────────────────────────────────────────────────────────────
# SystemMessage: LLM의 역할/행동 지침 설정
# HumanMessage: 사용자 입력
messages = [
    # TODO: SystemMessage와 HumanMessage를 작성해 주세요.
    SystemMessage(content='너는 초보자를 위한 AI 튜터야'),   # 기존에 사용하던 페르소나
    HumanMessage(content='LLM이 무엇인지 3문장으로 설명 해 줘.')
]

# TODO: invoke()로 메시지를 전달해 응답을 생성해 주세요.
response = llm.invoke(messages) # AIMessage라는 응답을 뱉어냈으니
print(response.content)

# ── Streaming ─────────────────────────────────────────────────────────────────
# stream()은 토큰 단위로 응답을 yield함
# end='' 로 줄바꿈 없이 실시간 출력
# TODO: stream()으로 응답을 실시간 출력해 주세요.
for chunk in llm.stream(messages):
    print(chunk)
