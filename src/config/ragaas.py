"""사내 RAGaaS 요청과 사외 실습용 모의 응답."""

import json
import os

from dotenv import load_dotenv

load_dotenv()

_ENDPOINTS = {"insert-doc", "retrieve-rrf", "delete-doc"}


class MockResponse:
    """requests.Response에서 실습 코드가 사용하는 부분만 제공한다."""

    status_code = 200

    def __init__(self, body: dict):
        self._body = body
        self.text = json.dumps(body, ensure_ascii=False)

    def json(self) -> dict:
        return self._body

    def raise_for_status(self) -> None:
        pass


def post_ragaas(endpoint: str, payload: dict, *, api_key: str | None = None):
    """RAG_PROVIDER=mock이면 네트워크 없이 같은 응답 형태를 돌려준다."""
    if endpoint not in _ENDPOINTS:
        raise ValueError(f"지원하지 않는 RAGaaS 엔드포인트: {endpoint}")

    provider = os.getenv("RAG_PROVIDER", "samsung").strip().lower()
    if provider == "mock":
        if endpoint == "retrieve-rrf":
            question = payload.get("query_text", "")
            return MockResponse({
                "hits": {
                    "hits": [{
                        "_source": {
                            "merge_title_content": (
                                f"[MOCK RAGaaS] 질문: {question}. "
                                "이 문장은 API 요청·응답 흐름을 연습하기 위한 모의 자료이며 "
                                "실제 사내 문서나 보험 약관의 내용이 아닙니다."
                            )
                        }
                    }]
                }
            })
        return MockResponse({"status": "mock", "endpoint": endpoint})

    if provider != "samsung":
        raise ValueError(f"지원하지 않는 RAG_PROVIDER: {provider!r}. 'mock' 또는 'samsung'을 사용하세요.")

    required = ("search_url", "rag_credential_key")
    missing = [name for name in required if not os.getenv(name)]
    api_key = api_key or os.getenv("rag_api_key")
    if not api_key:
        missing.append("rag_api_key")
    if missing:
        raise RuntimeError(f"사내 RAGaaS 설정이 부족합니다: {missing}")

    import requests

    response = requests.post(
        f'{os.environ["search_url"].rstrip("/")}/dsllmrag/elastic/v2/{endpoint}',
        json=payload,
        headers={
            "Content-Type": "application/json",
            "x-dep-ticket": os.environ["rag_credential_key"],
            "api-key": api_key,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response
