import os

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'{name} 환경변수가 필요합니다. 실행할 환경 파일을 확인하세요.')
    return value


def get_embeddings(**kwargs):
    """
    EMBED_PROVIDER 환경변수에 따라 임베딩 인스턴스를 반환한다.
    - openai: OpenAI 임베딩 (사외)
    - samsung (기본값): 삼성 사내 임베딩 REST API
    """
    provider = os.getenv("EMBED_PROVIDER", "samsung").strip().lower()

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        _required("OPENAI_API_KEY")
        if "model" not in kwargs:
            kwargs["model"] = _required("OPENAI_EMBEDDING_MODEL")
        if os.getenv("OPENAI_BASE_URL"):
            # OpenAI 호환 서버(NVIDIA 등)는 글자 대신 토큰 번호 목록을 보내면 400으로 거절한다
            kwargs.setdefault("check_embedding_ctx_length", False)
        return OpenAIEmbeddings(**kwargs)

    # ── 삼성 사내 임베딩 ──────────────────────────────────────────────────────
    # pilot/day2/04_RAG/정답/rag_retriever.py 의 MyCustomEmbeddings 참고.
    # 사내 망에서만 동작함.
    #
    elif provider == "samsung":
        import requests
        from langchain_core.embeddings import Embeddings
        from config.samsung import embedding_config

        class _SamsungEmbeddings(Embeddings):
            def __init__(self, config: dict):
                self.config = config

            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                # 02_embeddings.py와 같이 한 번에 10개씩 나눠 요청한다.
                result = []
                for i in range(0, len(texts), 10):
                    resp = requests.post(
                        self.config["url"],
                        json={"input": texts[i:i + 10]},
                        headers=self.config["headers"],
                        timeout=120,
                    )
                    resp.raise_for_status()
                    result.extend(item["embedding"] for item in resp.json()["data"])
                return result

            def embed_query(self, text: str) -> list[float]:
                return self.embed_documents([text])[0]

        return _SamsungEmbeddings(embedding_config())
    # ─────────────────────────────────────────────────────────────────────────

    raise ValueError(f"지원하지 않는 EMBED_PROVIDER: {provider!r}. 'openai' 또는 'samsung'을 사용하세요.")
