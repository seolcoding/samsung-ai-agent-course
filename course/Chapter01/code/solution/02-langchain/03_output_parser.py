"""
Output Parser: LLM 출력을 구조화된 데이터로 변환하기

두 가지 방식 비교:
  1. PydanticOutputParser + format_instructions → 프롬프트에 형식 지시 포함
  2. .with_structured_output()                 → LLM의 function-calling 기능 활용 (권장)

실행:
  python 03_output_parser.py
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# ── 출력 스키마 정의 ───────────────────────────────────────────────────────────

class MovieReview(BaseModel):
    title: str = Field(description='영화 제목')
    genre: str = Field(description='장르 (예: 액션, 드라마, SF)')
    rating: float = Field(description='평점 (1.0 ~ 10.0)')
    summary: str = Field(description='100자 이내 한 줄 요약')
    recommend: bool = Field(description='추천 여부')


# ── 방법 1: PydanticOutputParser ──────────────────────────────────────────────
# 프롬프트에 JSON 형식 지시문을 주입하여 LLM이 구조화된 출력을 생성하도록 유도.
# LLM이 지시를 따르지 않으면 파싱 실패 가능.

print('=== 방법 1: PydanticOutputParser ===')

parser = PydanticOutputParser(pydantic_object=MovieReview)

prompt = ChatPromptTemplate.from_messages([
    ('system', '영화 리뷰 전문가야. 다음 형식으로 응답해.\n{format_instructions}'),
    ('human', '{movie} 리뷰 작성해줘'),
]).partial(format_instructions=parser.get_format_instructions())

chain1 = prompt | llm | parser
review1: MovieReview = chain1.invoke({'movie': '인터스텔라'})

print(f'제목   : {review1.title}')
print(f'장르   : {review1.genre}')
print(f'평점   : {review1.rating}')
print(f'요약   : {review1.summary}')
print(f'추천   : {"✓" if review1.recommend else "✗"}')


# ── 방법 2: .with_structured_output() ────────────────────────────────────────
# LLM의 function-calling(tool use) 기능을 활용하므로 더 안정적.
# 프롬프트에 형식 지시를 추가할 필요 없음.

print('\n=== 방법 2: with_structured_output() ===')

structured_llm = llm.with_structured_output(MovieReview)

prompt2 = ChatPromptTemplate.from_messages([
    ('system', '영화 리뷰 전문가야.'),
    ('human', '{movie} 리뷰 작성해줘'),
])

chain2 = prompt2 | structured_llm
review2: MovieReview = chain2.invoke({'movie': '기생충'})

print(f'제목   : {review2.title}')
print(f'장르   : {review2.genre}')
print(f'평점   : {review2.rating}')
print(f'요약   : {review2.summary}')
print(f'추천   : {"✓" if review2.recommend else "✗"}')


# ── 비교 요약 ─────────────────────────────────────────────────────────────────
print('''
┌─────────────────────┬──────────────────────────┬──────────────────────────┐
│                     │ PydanticOutputParser      │ with_structured_output() │
├─────────────────────┼──────────────────────────┼──────────────────────────┤
│ 안정성              │ LLM 지시 이행에 의존      │ function-calling 보장    │
│ 프롬프트 복잡도     │ format_instructions 필요  │ 프롬프트 단순            │
│ 구형 모델 지원      │ ✓ (모든 텍스트 LLM)       │ function-calling 필요    │
│ 권장               │ 구형 모델 / 커스텀 파싱    │ GPT-4o 이상 기본 권장    │
└─────────────────────┴──────────────────────────┴──────────────────────────┘
''')
