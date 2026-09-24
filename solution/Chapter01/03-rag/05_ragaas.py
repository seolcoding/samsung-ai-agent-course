"""
RAG as a Service (RAGaaS): 삼성 사내 RAG API 활용

기존 방식 vs RAGaaS 비교:
  기존: 청킹 → 임베딩 클래스 구현 → 벡터스토어 생성 → 검색
  RAGaaS: 문서 업로드(API 1회) → 검색(API 1회)
  청킹·임베딩·벡터스토어 관리를 API가 대신 처리한다.

사외에서는 RAG_PROVIDER=mock으로 요청·응답 형식을 연습한다.
실제 문서 내용이 필요한 실습은 사내망에서 RAG_PROVIDER=samsung으로 실행한다.

실행:
  python 03-rag/05_ragaas.py
"""
import os
from pathlib import Path

from dotenv import load_dotenv

from config.llm import get_llm
from config.ragaas import post_ragaas

load_dotenv()

RAG_PROVIDER = os.getenv('RAG_PROVIDER', 'samsung').strip().lower()
INDEX_NAME = os.getenv('index_name') or ('mock-pet-insurance' if RAG_PROVIDER == 'mock' else '')
if not INDEX_NAME:
    raise RuntimeError('사내 RAGaaS에는 index_name 환경변수가 필요합니다.')
# 실제 사내 요청의 x-dep-ticket과 api-key 헤더는 config/ragaas.py에서 설정한다.
print(f'RAGaaS 모드: {RAG_PROVIDER}')


# ── 1부: 문서 업로드 ──────────────────────────────────────────────────────────
# insert-doc 엔드포인트 하나로 청킹·임베딩·벡터스토어 저장을 모두 처리한다.
# chunk_factor: 청킹 방식과 크기를 서버에 위임 (직접 구현 불필요)

# 업로드할 텍스트 준비 (예: 파일을 읽어서 문자열로 전달)
PDF_PATH = Path(__file__).parent / 'data' / 'meritz_pet_insurance.pdf'

# pdfminer 로 텍스트 추출 (RAGaaS는 raw text를 받음)
from langchain_community.document_loaders import PDFMinerLoader
docs = PDFMinerLoader(str(PDF_PATH.resolve())).load()
raw_text = '\n'.join(doc.page_content for doc in docs)

payload = {
    'index_name': INDEX_NAME,
    'data': {
        'doc_id': 'meritz_pet_insurance',
        'title': '메리츠 펫보험 약관',
        'content': raw_text,
    },
    'chunk_factor': {
        'logic': 'fixed_size',
        'chunk_size': 500,
        'chunk_overlap': 75,
        'separator': ' ',
    },
}

print('=== 문서 업로드 ===')
response = post_ragaas('insert-doc', payload)
print(f'상태: {response.status_code}')
print(response.text[:200])
print()


# ── 2부: 문서 검색 ────────────────────────────────────────────────────────────
# retrieve-* 엔드포인트: bm25(키워드), knn(의미), rrf(하이브리드) 중 선택
# 기존 EnsembleRetriever 없이 API 파라미터만 바꾸면 검색 방식 전환 가능

question = '펫보험 보장 내용이 뭐야?'

search_payload = {
    'index_name': INDEX_NAME,
    'permission_groups': ['rag-public'],
    'query_text': question,
    'num_result_doc': 3,
    'fields_exclude': ['v_merge_title_content'],
}

print('=== 문서 검색 (RRF: 하이브리드) ===')
response = post_ragaas('retrieve-rrf', search_payload)
result = response.json()
hits = result['hits']['hits']

context_list = [hit['_source']['merge_title_content'] for hit in hits]
context = '\n\n'.join(context_list)
print(f'검색된 문서 수: {len(hits)}')
print()


# ── 3부: RAG 체인 ─────────────────────────────────────────────────────────────
# 검색 결과를 context로 주입해 LLM이 문서 기반으로 답변하도록 한다.
# get_llm(): 로컬은 OpenAI, 사내망은 삼성 LLM으로 자동 전환

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

llm = get_llm()

prompt = ChatPromptTemplate.from_messages([
    ('system', '당신은 문서 기반 QA 어시스턴트입니다. 주어진 context만 근거로 답하세요.'),
    ('human', 'context:\n{context}\n\nquestion:\n{question}'),
])

chain = prompt | llm | StrOutputParser()

print(f'=== 질문: {question} ===')
for chunk in chain.stream({'context': context, 'question': question}):
    print(chunk, end='', flush=True)
print('\n')


# ── 4부: 문서 삭제 (선택) ─────────────────────────────────────────────────────
# 실습 종료 후 업로드한 인덱스를 정리한다.

delete_payload = {
    'index_name': INDEX_NAME,
    'permission_groups': ['rag-public'],
    'doc_id': 'meritz_pet_insurance',
}

response = post_ragaas('delete-doc', delete_payload)
print(f'=== 문서 삭제: {response.status_code} ===')
