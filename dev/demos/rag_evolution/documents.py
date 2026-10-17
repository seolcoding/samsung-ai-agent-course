"""2024년 제공 보험 PDF를 물리적 쪽번호와 함께 읽는다."""

from hashlib import sha256
from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader

DATA_DIR = Path(__file__).resolve().parent / "data"
PDF_PATH = DATA_DIR / "meritz_pet_insurance.pdf"
DOCUMENT_YEAR = 2024


def pdf_fingerprint() -> str:
    """현재 앱 PDF의 SHA-256. 벡터 인덱스 캐시 분리에 사용한다."""
    return sha256(PDF_PATH.read_bytes()).hexdigest()


def load_pdf_documents() -> list[Document]:
    """PDF 한 장을 Document 하나로 읽는다. page는 1부터 센 물리적 쪽수다."""
    reader = PdfReader(PDF_PATH)
    fingerprint = pdf_fingerprint()
    return [
        Document(
            page_content=(page.extract_text() or "").replace("\x00", " ").strip(),
            metadata={
                "source": PDF_PATH.name,
                "page": number,
                "year": DOCUMENT_YEAR,
                "pdf_sha256": fingerprint,
            },
        )
        for number, page in enumerate(reader.pages, start=1)
    ]
