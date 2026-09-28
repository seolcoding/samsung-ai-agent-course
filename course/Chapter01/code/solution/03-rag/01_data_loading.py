"""
데이터 로딩과 청킹: PDF를 Document와 Chunk로 변환하기

핵심 개념:
  - Document = LangChain이 문서 본문과 메타데이터를 다루는 기본 단위
  - Chunking = 긴 문서를 검색 가능한 작은 조각으로 나누는 과정
  - chunk_size와 chunk_overlap은 검색 정확도와 문맥 보존 사이의 균형을 조정

실행:
  python 03-rag/01_data_loading.py
"""
from pathlib import Path

from langchain_community.document_loaders import PDFMinerLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


PDF_PATH = Path(__file__).parent / 'data' / 'meritz_pet_insurance.pdf'


# ── PDF 로딩 ─────────────────────────────────────────────────────────────────
# PDFMinerLoader: PDF 파일을 LangChain Document 목록으로 변환
# 각 Document는 page_content와 metadata를 가진다.
loader = PDFMinerLoader(str(PDF_PATH.resolve()))
documents = loader.load()  # 결과는 list[Document]가 된다.


# ── 문서 청킹 ─────────────────────────────────────────────────────────────────
# 전체 문서는 한 번에 LLM에 넣기 어렵기 때문에 검색 가능한 Chunk로 나눈다.
# RecursiveCharacterTextSplitter: 문단 → 줄 → 단어 → 문자 순서로 분할 지점을 찾는다.
# chunk_size: 각 Chunk의 최대 길이
# chunk_overlap: 인접 Chunk 사이에 겹쳐 둘 길이
text_splitter = RecursiveCharacterTextSplitter(
    # 작을수록 검색 단위가 정밀하지만 전체 문맥이 줄어든다.
    chunk_size=500,
    # 클수록 문맥 연결성이 좋아지지만 중복과 비용이 늘어난다.
    chunk_overlap=75,
)
chunks = text_splitter.split_documents(documents)


# ── 결과 확인 ─────────────────────────────────────────────────────────────────
for index, chunk in enumerate(chunks[:3]):
    text = " ".join(chunk.page_content.split())
    print(f"{index}. len={len(chunk.page_content)} \n- {text[:120]}...")
    print()
