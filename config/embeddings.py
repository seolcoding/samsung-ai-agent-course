import os

from dotenv import load_dotenv

load_dotenv()


def get_embeddings(**kwargs):
    """
    EMBED_PROVIDER 환경변수에 따라 임베딩 인스턴스를 반환한다.
    - openai (기본값): OpenAI text-embedding-3-small
    - samsung: 삼성 사내 임베딩 REST API (아래 주석 블록 활성화)
    """
    provider = os.getenv("EMBED_PROVIDER", "samsung")

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        kwargs.setdefault("model", os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))
        return OpenAIEmbeddings(**kwargs)

    # ── 삼성 사내 임베딩 ──────────────────────────────────────────────────────
    # pilot/day2/04_RAG/정답/rag_retriever.py 의 MyCustomEmbeddings 참고.
    # 사내 망에서만 동작함.
    #
    elif provider == "samsung":
        import requests
        from langchain_core.embeddings import Embeddings
    
        class _SamsungEmbeddings(Embeddings):
            def __init__(self, api_url: str, ticket: str):
                self.api_url = api_url
                self.ticket = ticket
    
            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                resp = requests.post(
                    f"{self.api_url}/v1/embeddings",
                    json={"input": texts},
                    headers={
                        "Content-Type": "application/json",
                        "x-dep-ticket": self.ticket,
                    },
                )
                resp.raise_for_status()
                return [item["embedding"] for item in resp.json()["data"]]
    
            def embed_query(self, text: str) -> list[float]:
                return self.embed_documents([text])[0]
    
        return _SamsungEmbeddings(
            api_url=os.getenv("embedding_api_url"),
            ticket=os.getenv("embedding_x_dep_ticket"),
        )
    # ─────────────────────────────────────────────────────────────────────────

    raise ValueError(f"지원하지 않는 EMBED_PROVIDER: {provider!r}. 'openai' 또는 'samsung'을 사용하세요.")
