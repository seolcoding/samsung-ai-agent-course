"""3-1 과제: 약관 검색 도구를 쓰는 Agent"""

from pathlib import Path

from dotenv import load_dotenv

from config.embeddings import get_embeddings
from config.llm import get_llm

load_dotenv()

llm = get_llm()
embeddings = get_embeddings()
PDF_PATH = Path(__file__).parent / "data" / "meritz_pet_insurance.pdf"


# 아래에 AI와 함께 코드를 작성합니다
import warnings
from typing import Annotated

warnings.filterwarnings("ignore", message=".*langchain-community.*")
from langchain_chroma import Chroma
from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

# 1. 약관 PDF -> 청크 -> 벡터 저장소 -> retriever (조각 3개)
documents = PDFMinerLoader(str(PDF_PATH.resolve())).load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75)
chunks = splitter.split_documents(documents)
vectorstore = Chroma.from_documents(chunks, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


# 2. 약관 검색 도구
@tool
def search_policy(query: str) -> str:
    """펫보험 약관에서 질문과 관련된 내용을 찾는다. 보장·보험금·청구 등 약관 질문에만 쓴다."""
    docs = retriever.invoke(query)
    return "\n\n".join(d.page_content for d in docs)


tools = [search_policy]
llm_with_tools = llm.bind_tools(tools)
SYSTEM = SystemMessage(content="당신은 펫보험 상담원입니다. 약관 질문은 search_policy 도구로 찾은 내용만 근거로 답합니다.")


# 3. 그래프: agent -> (tools_condition) -> tools -> agent
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

# 4. 질문 두 개
for question in ["반려동물 수술비도 보장되나요?", "안녕하세요, 자기소개를 한 줄로 해 주세요"]:
    print(f"\n=== {question} ===")
    policy_agent_result = policy_agent.invoke({"messages": [HumanMessage(content=question)]})
    results = policy_agent_result["messages"]
    for m in results:
        m.pretty_print()
