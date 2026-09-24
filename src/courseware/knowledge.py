"""교육용 지식베이스. 실제 사내 문서나 의미 임베딩 검색이 아니다."""

import json
import re
from pathlib import Path

from langchain_core.embeddings import Embeddings


def load_documents() -> list[dict]:
    path = Path(__file__).parent / "data" / "knowledge.json"
    return json.loads(path.read_text(encoding="utf-8"))


def retrieve(query: str, k: int = 3) -> list[dict]:
    """태그·단어 겹침으로 검색한다. 의미 이해나 벡터 검색을 흉내 내지 않는다."""
    if not query.strip() or k <= 0:
        return []
    words = set(re.findall(r"[a-zA-Z0-9가-힣]+", query.lower()))
    ranked = []
    for doc in load_documents():
        tags = [tag.lower() for tag in doc["tags"]]
        score = sum(2 for tag in tags if tag in query.lower())
        score += sum(1 for word in words if len(word) > 1 and word in doc["text"].lower())
        if score:
            ranked.append({**doc, "score": score})
    return sorted(ranked, key=lambda d: (-d["score"], d["id"]))[:k]


def answer_from_documents(query: str) -> dict:
    hits = retrieve(query, k=2)
    answer = "\n".join(f'{d["text"]} [{d["id"]}]' for d in hits)
    return {"answer": answer or "문서에서 확인할 수 없습니다.", "sources": hits, "mode": "모의 자료·원문 발췌"}


class KeywordEmbeddings(Embeddings):
    """고정 단어의 출현 횟수 벡터. 학습된 의미 임베딩 모델이 아니다."""

    vocabulary = ["검색", "문서", "도구", "프로토콜", "승인", "보고서", "상태", "메모리", "평가", "기록", "반복", "종료"]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(text.count(word)) for word in self.vocabulary] for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
