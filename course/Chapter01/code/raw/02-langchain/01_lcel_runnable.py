"""
LCEL Runnable: LangChain 구성 요소를 파이프라인으로 연결하기

핵심 개념:
  - Runnable = invoke, stream, batch를 공통으로 제공하는 실행 단위
  - LCEL = prompt → model → parser 흐름을 | 연산자로 선언하는 방식
  - RunnableParallel, RunnablePassthrough, RunnableLambda로 입력 흐름을 조합 가능

실행:
  python 02-langchain/01_lcel_runnable.py
"""
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

from config.llm import get_llm


load_dotenv()

model = get_llm() # 가우스

# ── 기본 LCEL 체인 ────────────────────────────────────────────────────────────
# ChatPromptTemplate: `{}` 변수만 바꿔 재사용할 수 있는 프롬프트 템플릿
    # 사용자가 입력한 값 -> 우리가 제어 및 통제와 개선
prompt = ChatPromptTemplate.from_messages([
    # TODO: system, human 메시지 튜플을 작성해 주세요.
    ('system', '너는 초보자를 위한 AI 튜터야'),
    # 사용자마다 서로 다른 내용의 주제를 질문하게 될 것이다.
        # 그러나, 우리가 만든 에이전트는 항상 동등한 수준의 답변을
    ('human', '{topic}을 초보자에게 3문장으로 설명해 줘')
])

# StrOutputParser: LLM 출력을 문자열로 변환
parser = StrOutputParser()

# LCEL: LangChain Expression Language
# - 프롬프트 작성 → LLM 호출 → 출력 파싱 과정을 하나의 실행 단위로 묶는다.
# - prompt, model, parser는 모두 Runnable 계열 객체다.
# - Runnable | Runnable 결과도 Runnable이므로 체인을 계속 이어붙일 수 있다.
# TODO: 위에 정의한 프롬프트, 모델, 출력 파서를 파이프라인 연산자로 연결해 주세요.
    # 사용자 입력 -> 모델에게 전달 -> 정해진 출력방식으로 출력
chain = prompt | model | parser # runnable

# Runnable 실행 방식:
# - invoke(): 단일 입력 처리
# - stream(): 토큰/청크 단위 출력
# - batch(): 여러 입력 일괄 처리

# 파이썬 주석처리 -> 주석처리할 대상을 드래그 ctrl + /
# answer = chain.invoke({'topic': 'LLM'})
# print(answer)
# print('----')
# for chunk in chain.stream({'topic': 'LangChain'}):
#     print(chunk, end='', flush=True)
# print()

# print('----')
# inputs = [{'topic': 'LangChain Expression Language'}, {'topic': 'LangChain Runnable'}]
# responses = chain.batch(inputs)
# for topic_input, response in zip(inputs, responses):
#     print(f"{topic_input.get('topic')}: {response.strip()}")


# ── RunnableParallel ──────────────────────────────────────────────────────────
# 여러 Runnable을 병렬로 실행해 결과를 dict로 모을 때 사용
pros_chain = ChatPromptTemplate.from_template('{country}로 여행갈 때의 장점을, 5개 정도 목록 형식으로 설명해줘.') | model | StrOutputParser()
cons_chain = ChatPromptTemplate.from_template('{country}로 여행갈 때의 단점을, 5개 정도 목록 형식으로 설명해줘.') | model | StrOutputParser()

    # 주의) 변수명이 pros, cons로 고정인게 아님!
    # 이거 내가 맘음대로 지을 수 있음!
runnable = RunnableParallel(pros=pros_chain, cons=cons_chain)
answers = runnable.invoke({'country': '베트남'})
print('pros')
print(answers.get('pros'))

print('cons')
print(answers.get('cons'))

# answers = {'pros': '', 'cons': ''}
# for chunk in runnable.stream({'country': 'USA'}):
#     for key in chunk:
#         answers[key] += chunk[key]

# from pprint import pprint
# pprint(answers)

# Python dict가 pipe 사이에 들어가면 자동으로 RunnableParallel처럼 동작한다.
parallel_dict = RunnablePassthrough() | {
    'pros': ChatPromptTemplate.from_template('{country}로 여행갈 때의 장점을, 5개 정도 목록 형식으로 설명해줘.') | model | StrOutputParser(),
    'cons': ChatPromptTemplate.from_template('{country}로 여행갈 때의 단점을, 5개 정도 목록 형식으로 설명해줘.') | model | StrOutputParser(),
}

answers = parallel_dict.invoke({'country': '베트남'})
print('pros')
print(answers.get('pros'))

print('cons')
print(answers.get('cons'))


# ── RunnablePassthrough ───────────────────────────────────────────────────────
# 입력값을 그대로 다음 단계에 전달하면서 부가 필드를 추가할 때 사용
def get_question_length(text: str):
    return len(text)

# 예: 사용자 질문을 바탕으로 맥락 정보나 메타데이터를 추가
passthrough = RunnablePassthrough.assign(length=lambda x: get_question_length(x['question']))
print(passthrough.invoke({'question': 'RunnablePassthrough의 역할이 뭐야?'}))

prompt = ChatPromptTemplate.from_template('{question} 3문장으로 설명해줘.')
chain = passthrough | prompt | model | StrOutputParser()
print(chain.invoke({'question': 'RunnablePassthrough의 역할이 뭐야?'}))


# ── RunnableLambda ────────────────────────────────────────────────────────────
# 일반 Python 함수를 Runnable로 감싸 체인 안에서 사용할 때 활용
acronym_dict = {
    'GPT': 'Generative Pre-trained Transformer',
    'LLM': 'Large Language Model',
    'LCEL': 'LangChain Expression Language',
}
def translate_acronym(acronym: str):
    # response = model.invoke()
    # return response
    return acronym_dict.get(acronym, acronym)

print(RunnableLambda(translate_acronym).invoke('GPT'))

prompt = ChatPromptTemplate.from_messages([
    ('system', '너는 초보자를 위한 AI 튜터야.'),
    ('human', '{topic}을 초급자에게 3문장으로 설명해줘.'),
])

chain = {
    'topic': RunnableLambda(translate_acronym),
} | prompt | model | StrOutputParser()
print(chain.invoke('GPT'))
