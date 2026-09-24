"""테스트용 모델 대역. LLM의 판단 능력·품질을 검증하는 모델이 아니다."""

import re
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class ScriptedMultiplyModel(BaseChatModel):
    """숫자 두 개를 multiply로 보내고 결과를 돌려주는 고정 규칙이다."""

    @property
    def _llm_type(self) -> str:
        return "teaching-scripted-multiply"

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        names = [t.name if hasattr(t, "name") else t.get("name") for t in tools]
        if "multiply" not in names:
            raise ValueError("이 모의 모델은 multiply 도구 전용입니다.")
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs: Any):
        if isinstance(messages[-1], ToolMessage):
            reply = AIMessage(content=f"[모의 모델] 도구에서 확인한 결과: {messages[-1].content}")
        else:
            question = next((str(m.content) for m in reversed(messages) if isinstance(m, HumanMessage)), "")
            numbers = re.findall(r"-?\d+", question)
            if len(numbers) != 2:
                reply = AIMessage(content="[모의 모델] 곱할 정수 두 개를 입력해 주세요.")
            else:
                reply = AIMessage(content="", tool_calls=[{"name": "multiply", "args": {"a": int(numbers[0]), "b": int(numbers[1])}, "id": "multiply-demo", "type": "tool_call"}])
        return ChatResult(generations=[ChatGeneration(message=reply)])


class ScriptedTextModel(BaseChatModel):
    """정해 둔 텍스트를 반환한다. Deep Agents의 연결 구조 확인에 쓴다."""

    response: str = "[모의 모델] 실행 환경과 도구 연결을 확인했습니다."

    @property
    def _llm_type(self) -> str:
        return "teaching-scripted-text"

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs: Any):
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self.response))])
