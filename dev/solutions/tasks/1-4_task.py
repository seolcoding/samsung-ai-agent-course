"""1-4 과제: 약관 질문 RAG"""

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

warnings.filterwarnings("ignore", message=".*langchain-community.*")
from langchain_chroma import Chroma
from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. PDF 읽기 -> 청크 나누기 (쪽 번호가 남도록 쪽마다 읽는다)
documents = PDFMinerLoader(str(PDF_PATH.resolve()), mode="page").load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=75)
chunks = splitter.split_documents(documents)

# 2. 벡터 저장소 -> retriever (조각 3개)
vectorstore = Chroma.from_documents(chunks, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 3. 프롬프트 + RAG 체인
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "당신은 약관 QA 어시스턴트입니다. 주어진 context만 근거로 답하세요. "
            "context에 없으면 '약관에 없는 내용입니다'라고 모른다고 답하세요.",
        ),
        ("human", "context:\n{context}\n\nquestion:\n{question}"),
    ]
)
chain = prompt | llm | StrOutputParser()

# 4. 질문 두 개: 약관에 있는 것, 없는 것
questions = ["펫보험 보장 내용이 뭐야?", "내 자동차 보험료는 얼마야?"]
for question in questions:
    docs = retriever.invoke(question)
    pages = [d.metadata.get("page") for d in docs]
    context = "\n\n".join(d.page_content for d in docs)

    print(f"=== 질문: {question} ===")
    print("검색된 쪽 번호:", pages)
    print("답:", chain.invoke({"context": context, "question": question}))
    print()
