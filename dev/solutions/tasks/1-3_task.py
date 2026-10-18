"""1-3 과제: 회의 메모 정리 체인"""

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

llm = get_llm()


# 아래에 AI와 함께 코드를 작성합니다
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class MeetingNote(BaseModel):
    title: str = Field(description="회의 제목")
    decisions: list[str] = Field(description="결정 사항 목록")
    todos: list[str] = Field(description="할 일 목록")


parser = PydanticOutputParser(pydantic_object=MeetingNote)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "회의 메모를 정리하는 도우미야. 다음 형식으로 응답해.\n{format_instructions}"),
        ("human", "{memo}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser

memos = [
    {"memo": "신제품 출시일은 11월 5일로 정했다. 광고는 SNS 중심으로 간다. 민수는 포스터를 만들고, 지영은 예산안을 금요일까지 제출한다."},
    {"memo": "서버 점검은 토요일 새벽 2시에 하기로 했다. 공지는 하루 전에 보낸다. 철수가 공지문을 쓰고 영희가 백업을 확인한다."},
]

results = chain.batch(memos)

for i, note in enumerate(results, start=1):
    print(f"=== 메모 {i} ===")
    print("제목:", note.title)
    print("결정 사항:", note.decisions)
    print("할 일:", note.todos)
