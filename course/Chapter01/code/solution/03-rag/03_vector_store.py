from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PDFMinerLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.embeddings import get_embeddings

load_dotenv()


PDF_PATH = Path(__file__).parent / 'data' / 'meritz_pet_insurance.pdf'
loader = PDFMinerLoader(str(PDF_PATH.resolve()))
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=75,
)
chunks = text_splitter.split_documents(documents)

# get_embeddings(): src/config/embeddings.py 에서 EMBED_PROVIDER 환경변수로 전환
# 로컬: OpenAIEmbeddings / 사내: SamsungEmbeddings (02_embeddings.py에서 직접 구현한 그것)
embeddings = get_embeddings()
vectorstore = Chroma.from_documents(
    chunks,
    embedding=embeddings,
    # ChromaDB를 저장하고 싶을 때
    # persist_directory=str(Path(__file__).parent),
)

retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
print('retriever ready')
while True:
    question = input('prompt: ')
    results = retriever.invoke(question)
    for index, doc in enumerate(results):
        text = ' '.join(doc.page_content.split())
        print(f'{index}. len={len(doc.page_content)} \n- {text[:180]}...')
        print()

