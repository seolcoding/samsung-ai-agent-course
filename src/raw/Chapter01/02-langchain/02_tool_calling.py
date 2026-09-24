"""
Tool Calling: LLM이 외부 도구를 자율적으로 선택·실행하기

핵심 흐름:
  사용자 질문 → LLM이 필요한 도구 결정 → 도구 실행 → 결과 반환

실행:
  python 02_tool_calling.py
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from config.llm import get_llm

load_dotenv()


# ── 도구 정의 (@tool 데코레이터) ────────────────────────────────────────────────
# 함수의 docstring이 LLM에게 전달되는 도구 설명이 된다.
# 타입 힌트가 JSON Schema로 변환되어 파라미터 형식을 LLM에게 알려준다.
# tool 데코레이터에 넣는 description은 절대적으로 LLM을 위한 설명. -> 한줄의 간략한 설명
    # 파이썬은, 함수의 인자를 타입힌트 (args: type) 작성 할 수 있는데 -> 이 자체도 LLM에게 도구를 사용할 힌트

# LLM이 사용자 질문에 맞춰서 적절한 도구를 호출 할 수 있어야 한다.
    # 그건 어떻게하는데?

@tool
def get_weather(city: str) -> str:
    """지정한 도시의 현재 날씨를 조회한다."""
    fake_data = {
        '서울': '맑음, 기온 22°C',
        '부산': '흐림, 기온 24°C',
        '제주': '비, 기온 20°C',
    }
    return fake_data.get(city, f'{city}의 날씨 데이터를 찾을 수 없습니다.')


@tool
def calculate(expression: str) -> str:
    """수학 수식을 계산한다. 예: '2 + 3 * 4'"""
    try:
        result = eval(expression, {'__builtins__': {}})  # noqa: S307
        return str(result)
    except Exception as e:
        return f'계산 오류: {e}'


# TODO: LLM에 연결할 도구 목록을 작성해 주세요.
tools = [get_weather, calculate]

# ── LLM에 도구 바인딩 ─────────────────────────────────────────────────────────
# bind_tools()는 LLM 호출 시마다 도구 스키마를 자동으로 포함시킨다.
llm = get_llm()
# TODO: bind_tools()를 사용해 LLM에 도구 스키마를 연결해 주세요.
                # bind_tools -> 메서드는 시퀀스를 전달받을 수 있음.
                # 한번에 여러 도구들 (tool 데코레이터로 정의된 함수들)
llm_with_tools = llm.bind_tools(tools)

# 도구 이름 → 실행 함수 매핑
# TODO: 도구 이름으로 실제 도구를 찾을 수 있도록 매핑을 만들어 주세요.
'''
    {
        'get_weahter': get_weather, 
        'calculate': calculate, 
    }
'''
tool_map = {tool.name: tool for tool in tools}


# ── 수동 도구 호출 루프 ───────────────────────────────────────────────────────
# LLM 응답에 tool_calls가 있으면 실행 후 결과를 다시 LLM에 전달한다.
# LangGraph의 ToolNode가 이 루프를 자동화한다 (05-langgraph/03_tool_node.py 참고).

def run_with_tools(question: str) -> str:
    messages = [HumanMessage(content=question)]

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

        for call in response.tool_calls:
            print(call)
            # TODO: tool_calls의 이름과 인자를 사용해 해당 도구를 실행해 주세요.
            tool_fn = tool_map[call['name']]
            result = tool_fn.invoke(call['args'])
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=call['id'],
                )
            )


# ── 실행 예시 ─────────────────────────────────────────────────────────────────

print('=== 날씨 질문 ===')
print(run_with_tools('서울 날씨 알려줘'))

print('\n=== 수학 계산 ===')
print(run_with_tools('(123 + 456) * 2를 계산해줘'))

print('\n=== 복합 질문 ===')
print(run_with_tools('서울과 부산 날씨를 비교해줘'))

# LangGraph ToolNode 방식으로 전환하면 이 루프가 필요 없어진다.
# → 05-langgraph/03_tool_node.py 참고
