"""3-1 과제 정답(강사용): 약관 검색 도구 Agent

PDF 경로가 과제 폴더 기준이므로 course/Chapter02/tasks/3-1/3-1_task.py 자리에 두고 실행합니다(저장소 맨 위에서):
    uv run --env-file .env python course/Chapter02/tasks/3-1/3-1_task.py
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# 약관 PDF(노트북 폴더의 data)
PDF_PATH = Path(__file__).resolve().parents[2] / "notebooks" / "data" / "meritz_pet_insurance.pdf"


# ✍️ 목표 1: config.check로 설정을 점검합니다(모델·임베딩을 실제로 한 번씩 호출). ⛔이 있으면 여기서 멈춥니다.
from config.check import check_env  # noqa: E402

if not check_env(["EMBED_PROVIDER"], live=True):
    sys.exit(1)


from config.embeddings import get_embeddings  # noqa: E402 — 점검을 먼저 하고 모델을 준비합니다
from config.llm import get_llm  # noqa: E402

llm = get_llm()
embeddings = get_embeddings()


# ✍️ 목표 2: 약관 PDF로 Chroma 검색기(조각 3개)를 만들고 @tool search_policy로 감쌉니다.
import warnings  # noqa: E402

warnings.filterwarnings("ignore", message=".*langchain-community.*")
from langchain_chroma import Chroma  # noqa: E402
from langchain_community.document_loaders import PDFMinerLoader  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from langchain_text_splitters import RecursiveCharacterTextSplitter  # noqa: E402

documents = PDFMinerLoader(str(PDF_PATH)).load()
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75).split_documents(documents)
vectorstore = Chroma.from_documents(chunks, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


@tool
def search_policy(query: str) -> str:
    """펫보험 약관에서 질문과 관련된 내용을 찾는다. 보장·보험금·청구 등 약관 질문에만 쓴다."""
    docs = retriever.invoke(query)
    return "\n\n".join(d.page_content for d in docs)


# ✍️ 목표 3: agent → (tools_condition) → tools → agent로 도는 그래프 policy_agent를 만듭니다.
from typing import Annotated  # noqa: E402

from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402
from langgraph.graph import START, StateGraph  # noqa: E402
from langgraph.graph.message import add_messages  # noqa: E402
from langgraph.prebuilt import ToolNode, tools_condition  # noqa: E402
from typing_extensions import TypedDict  # noqa: E402

tools = [search_policy]
llm_with_tools = llm.bind_tools(tools)
SYSTEM = SystemMessage(content="당신은 펫보험 상담원입니다. 약관 질문은 search_policy 도구로 찾은 내용만 근거로 답합니다.")


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> dict:
    return {"messages": [llm_with_tools.invoke([SYSTEM] + state["messages"])]}


builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
policy_agent = builder.compile()


# ✍️ 목표 4: 약관 질문 하나와 인사 하나를 policy_agent로 실행하고, 메시지를 pretty_print()로 출력합니다.
for question in ["반려동물 수술비도 보장되나요?", "안녕하세요, 자기소개를 한 줄로 해 주세요"]:
    print(f"\n########## 질문: {question} ##########")
    policy_agent_result = policy_agent.invoke({"messages": [HumanMessage(content=question)]})
    results = policy_agent_result["messages"]
    for m in results:
        m.pretty_print()
