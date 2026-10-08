from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PDFMinerLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.embeddings import get_embeddings
from config.llm import get_llm

load_dotenv()


PDF_PATH = Path(__file__).parent / 'data' / 'meritz_pet_insurance.pdf'
loader = PDFMinerLoader(str(PDF_PATH.resolve()))
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=75,
)
chunks = text_splitter.split_documents(documents)

embeddings = get_embeddings()
vectorstore = Chroma.from_documents(
    chunks,
    embedding=embeddings,
)

retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

llm = get_llm()
prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                '당신은 문서 기반 QA 어시스턴트입니다. 주어진 context만 근거로 답하세요.',
            ),
            ('human', 'context:\n{context}\n\nquestion:\n{question}'),
        ]
    )
def format_docs(docs):
    return '\n\n'.join(doc.page_content for doc in docs)


rag_chain = (
    { 'context': retriever | format_docs, 'question': RunnablePassthrough() }
    | prompt
    | llm
    | StrOutputParser()
)

print('RAG ready')
while True:
    question = input('prompt: ')
    for message in rag_chain.stream(question):
        print(message, end='')
    print('\n')
