"""3-1 과제 · 약관 질문에만 검색 도구를 쓰는 Agent

▶️ 실행   uv run --env-file .env python course/Chapter02/tasks/3-1_task.py
✅ 확인   실행하면 맨 끝에 🟢/⛔가 나옵니다
🆘 막히면 오류 메시지 전체를 AI에게 붙여 넣기
"""

import sys
import warnings
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool, tool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from config.check import check_env
from config.embeddings import get_embeddings
from config.llm import get_llm

warnings.filterwarnings("ignore", message=".*langchain-community.*")
from langchain_chroma import Chroma  # noqa: E402
from langchain_community.document_loaders import PDFMinerLoader  # noqa: E402
from langchain_text_splitters import RecursiveCharacterTextSplitter  # noqa: E402

load_dotenv()

# 설정 점검(모델·임베딩을 한 번씩 불러 봄). ⛔이 있으면 여기서 멈춥니다
if not check_env(["EMBED_PROVIDER"], live=True):
    sys.exit(1)

llm = get_llm()

# 약관 PDF → 조각 3개를 찾는 검색기
PDF_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "data" / "meritz_pet_insurance.pdf"
documents = PDFMinerLoader(str(PDF_PATH)).load()
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75).split_documents(documents)
retriever = Chroma.from_documents(chunks, embedding=get_embeddings()).as_retriever(search_kwargs={"k": 3})

SYSTEM = SystemMessage(content="당신은 펫보험 상담원입니다. 약관 질문은 search_policy 도구로 찾은 내용만 근거로 답합니다.")


class State(TypedDict):
    messages: Annotated[list, add_messages]


# ✍️ 1. 약관 검색 도구 만들기
# ✨ @tool search_policy(query: str) · retriever.invoke → 조각 글 합쳐 return · docstring에 언제 쓰는지
print("(1. 아직 작성하지 않았습니다)")


def build_policy_agent():
    # ✍️ 2. 도구를 반복해 부르는 그래프 만들기
    # ✨ llm.bind_tools · agent 노드(SYSTEM + messages) · ToolNode · tools_condition · tools → agent · return compile()
    print("(2. 아직 작성하지 않았습니다)")


QUESTIONS = ["반려동물 수술비도 보장되나요?", "안녕하세요, 자기소개를 한 줄로 해 주세요"]
runs = {}  # 질문 → 메시지 목록(맨 끝 확인에서 씁니다)
policy_agent = build_policy_agent()
for question in QUESTIONS:
    if policy_agent is None:
        break
    print(f"\n########## 질문: {question} ##########")
    policy_agent_result = policy_agent.invoke({"messages": [HumanMessage(content=question)]})
    results = runs[question] = policy_agent_result["messages"]
    for m in results:
        m.pretty_print()


# ── ✅ 확인 (바꾸지 않습니다) ──
print("\n✅ 확인")
found = globals().get("search_policy")
if not isinstance(found, BaseTool):
    print("⛔ 1. 아직 작성하지 않았습니다")
elif "보험" not in str(found.invoke({"query": "수술비 보장"})):
    print("⛔ 1. search_policy가 약관 글을 돌려주지 않습니다")
else:
    print("🟢 1. search_policy가 약관 조각을 찾아 돌려줍니다")
policy, hello = runs.get(QUESTIONS[0], []), runs.get(QUESTIONS[1], [])
if policy_agent is None:
    print("⛔ 2. 아직 작성하지 않았습니다")
elif not (any(isinstance(m, ToolMessage) for m in policy) and isinstance(policy[-1], AIMessage) and not policy[-1].tool_calls):
    print("⛔ 2. 약관 질문이 tools → agent를 거쳐 답으로 끝나지 않았습니다")
elif any(isinstance(m, ToolMessage) for m in hello):
    print("⛔ 2. 인사에도 도구를 불렀습니다(도구 docstring에 언제 쓰는지 분명히)")
else:
    print("🟢 2. 약관 질문만 tools를 거쳐 agent의 답으로 끝났습니다")
