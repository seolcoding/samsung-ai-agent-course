"""
RAG as a Service (RAGaaS): 삼성 사내 RAG API 활용

기존 방식 vs RAGaaS 비교:
  기존: 청킹 → 임베딩 클래스 구현 → 벡터스토어 생성 → 검색
  RAGaaS: 문서 업로드(API 1회) → 검색(API 1회)
  청킹·임베딩·벡터스토어 관리를 API가 대신 처리한다.

⚠️  이 파일은 삼성 사내망에서만 동작합니다.
    .env 에 아래 항목이 필요합니다:
      rag_credential_key=...
      search_url=...
      index_name=...

실행:
  python 03-rag/05_ragaas.py
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from config.llm import get_llm

load_dotenv()

RAG_KEY   = os.getenv('rag_credential_key')
RAG_API_KEY = os.getenv('rag_api_key')
SEARCH_URL = os.getenv('search_url')
# 사용할 인덱스 네임
INDEX_NAME = 'rp-aicoa-meritz-pet'

HEADERS = {
    'Content-Type': 'application/json',
    'x-dep-ticket': RAG_KEY,
    'api-key': RAG_API_KEY,
}


# ── 1부: 문서 업로드 ──────────────────────────────────────────────────────────
# insert-doc 엔드포인트 하나로 청킹·임베딩·벡터스토어 저장을 모두 처리한다.
# chunk_factor: 청킹 방식과 크기를 서버에 위임 (직접 구현 불필요)

import requests

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
# TODO: insert-doc 엔드포인트로 문서를 업로드해 주세요.
# response = requests.post(
#     f'{SEARCH_URL}/dsllmrag/elastic/v2/insert-doc',
#     # 파이썬의 딕셔너리 형태 -> JSON 형태로 변환해서 전송
#     data= json.dumps(payload),
#     headers= HEADERS
# )
# print(f'상태: {response.status_code}')
# print(response.text[:200])
# print()


# ── 2부: 문서 검색 ────────────────────────────────────────────────────────────
# retrieve-* 엔드포인트: bm25(키워드), knn(의미), rrf(하이브리드) 중 선택

question = '펫보험 보장 내용이 뭐야?'

search_payload = {
    # INDEX를 기반으로 문서를 검색한다.
        # 따라서, 문서를 등록할 때, 하나의 문서 말고도
        # 다양한 그러나 하나의 범주에 속할 수 있는 문서들을
        # 잘 전처리 했다면 (RAG화 하기 적절하게)
        # 동일한 INDEX_NAME으로 여러 문서들을 등록해서 사용할 수도 있다.
    'index_name': INDEX_NAME,
    'permission_groups': ['rag-public'],
    'query_text': question,
    'num_result_doc': 3,
    # 'fields_exclude': ['v_merge_title_content'],
}

print('=== 문서 검색 (RRF: 하이브리드) ===')

# TODO: retrieve-rrf 엔드포인트로 관련 문서를 검색해 주세요.

response = requests.post(
    f'{SEARCH_URL}/dsllmrag/elastic/v2/retrieve-rrf',
    data=json.dumps(search_payload),
    headers=HEADERS
)
result = response.json()
# print(result)
hits = result['hits']['hits']
context_list = [hit['_source']['merge_title_content'] for hit in hits]
context = '\n\n'.join(context_list)
print(f'검색된 문서 수: {len(hits)}')
# print(context_list)


# ── 3부: RAG 체인 ─────────────────────────────────────────────────────────────
# 검색 결과를 context로 주입해 LLM이 문서 기반으로 답변하도록 한다.
# get_llm(): 로컬은 OpenAI, 사내망은 삼성 LLM으로 자동 전환


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

llm = get_llm()

# 모델에게 입력할 지시사항과, 사용자의 질문을 간단하게 정의
prompt = ChatPromptTemplate.from_messages([
    ('system', '당신은 문서 기반 QA 어시스턴트입니다. 주어진 context만 근거로 답하세요.'),
    ('human', 'context:\n{context}\n\nquestion:\n{question}'),
    # ai -> model의 답변을 관리하는 방식
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

# TODO: delete-doc 엔드포인트로 업로드한 문서를 삭제해 주세요.
# response = requests.post(
#     f'{SEARCH_URL}/dsllmrag/elastic/v2/delete-doc',
#     headers=HEADERS,
#     data=json.dumps(delete_payload),
# )
# print(f'=== 문서 삭제: {response.status_code} ===')
