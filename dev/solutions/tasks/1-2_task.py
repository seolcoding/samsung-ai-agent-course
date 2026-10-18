"""1-2 과제: IT 헬프데스크 상담 스크립트"""

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# 아래에 AI와 함께 코드를 작성합니다
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# 역할을 정하는 system 메시지
messages = [SystemMessage(content="당신은 친절한 IT 헬프데스크 상담원입니다. 쉬운 말로 짧게 답하세요.")]

# 1) 첫 질문
messages.append(HumanMessage(content="노트북이 너무 느려요. 어떻게 해야 하나요?"))
first = llm.invoke(messages)
print("[첫 질문] 노트북이 너무 느려요. 어떻게 해야 하나요?")
print("[첫 답]", first.content)

# 2) 앞 질문과 답을 쌓은 채로 두 번째 질문
messages.append(AIMessage(content=first.content))
messages.append(HumanMessage(content="방금 말한 첫 번째 방법을 더 자세히 알려 주세요."))

# 3) 두 번째 답은 stream()으로 조각을 받아 이어 붙여 출력
print("\n[두 번째 답]")
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
print()
