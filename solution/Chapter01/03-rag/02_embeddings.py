"""
임베딩(Embedding): 텍스트를 숫자 벡터로 변환하기

핵심 개념:
  - 임베딩 = 텍스트의 '의미'를 숫자 벡터로 표현
  - 의미가 비슷한 텍스트는 벡터 공간에서 가까이 위치
  - RAG에서 '관련 문서 검색'은 이 벡터 거리를 계산하는 것

실행:
  python 03-rag/02_embeddings.py
"""
import os

import numpy as np
from dotenv import load_dotenv
from config.embeddings import get_embeddings

load_dotenv()

import requests
from langchain_core.embeddings import Embeddings

API_URL = os.getenv('embedding_api_url')
TICKET  = os.getenv('embedding_x_dep_ticket')
BATCH   = 10  # API 한 번에 처리 가능한 최대 텍스트 수

class SamsungEmbeddings(Embeddings):

    def embed_documents(self, texts):
        # BATCH 개씩 나눠서 API 호출, 결과를 하나로 합침
        result = []
        for i in range(0, len(texts), BATCH):
            res = requests.post(
                f'{API_URL}/v1/embeddings',
                json={'input': texts[i:i + BATCH]},
                headers={'x-dep-ticket': TICKET},
                timeout=30,
            )
            res.raise_for_status()
            result.extend(item['embedding'] for item in res.json()['data'])
        return result

    def embed_query(self, text):
        # 질문 하나를 임베딩할 때는 embed_documents 재활용
        return self.embed_documents([text])[0]

provider = os.getenv('EMBED_PROVIDER', 'samsung').strip().lower()
if provider == 'samsung':
    if not API_URL or not TICKET:
        raise RuntimeError('embedding_api_url과 embedding_x_dep_ticket이 필요합니다.')
    embeddings = SamsungEmbeddings()
else:
    # 사외에서는 같은 유사도 실습을 OpenAI 임베딩으로 실행한다.
    embeddings = get_embeddings()

sentences = [
    '강아지가 공원에서 뛰어놀고 있다.',
    '개가 잔디밭에서 달리고 있다.',
    '오늘 주식시장이 크게 하락했다.',
]

# embed_documents(): 텍스트 리스트 → 벡터 리스트
vectors = embeddings.embed_documents(sentences)

print('=== 벡터 기본 정보 ===')
print(f'문장 수    : {len(vectors)}')
print(f'벡터 차원  : {len(vectors[0])}')
print(f'앞 5개 값  : {[v for v in vectors]}')
print()


# ── 코사인 유사도 ─────────────────────────────────────────────────────────────
# 코사인 유사도: 1에 가까울수록 의미가 유사, 0에 가까울수록 관련 없음
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

v = [np.array(vec) for vec in vectors]
print('=== 문장 간 유사도 ===')
print(f'[강아지] vs [개]   : {cosine_similarity(v[0], v[1]):.4f}')   # 높아야 함
print(f'[강아지] vs [주식] : {cosine_similarity(v[0], v[2]):.4f}')   # 낮아야 함
print()

# embed_query(): 질문 하나를 벡터로 변환 (검색 시 사용)
query_vec = np.array(embeddings.embed_query('애완동물이 뛰노는 모습'))
scores = [cosine_similarity(query_vec, v_i) for v_i in v]
best = scores.index(max(scores))
print(f'질문: "애완동물이 뛰노는 모습"')
print(f'가장 유사한 문장: "{sentences[best]}" (유사도: {scores[best]:.4f})')
print()


# ── 실습: SamsungEmbeddings 구현 ──────────────────────────────────────────────
# 삼성 사내 임베딩 API는 LangChain과 직접 호환되지 않는다.
# langchain_core.embeddings.Embeddings 를 상속해 아래 두 메서드만 구현하면
# vectorstore, retriever 등 LangChain의 모든 컴포넌트에서 그대로 사용 가능하다.
#
# 아래 주석을 해제하고 SamsungEmbeddings 를 완성한 뒤,
# embeddings = SamsungEmbeddings() 로 교체해 위 유사도 계산을 다시 실행해 보자.



