"""세션에서 선택한 연결 설정. 전역 환경변수를 바꾸지 않는다."""

import hashlib
import json
import os
import uuid
from collections.abc import Callable

import requests
from langchain_core.embeddings import Embeddings

MODE_ALIASES = {"녹화 재생": "demo", "화면 데모": "demo", "OpenAI 실행": "openai", "사내 실행": "samsung"}
FIELDS = (
    "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_EMBEDDING_MODEL", "OPENAI_BASE_URL",
    "api_base_url", "model", "credential_key", "send_system_name", "user_id",
    "embedding_api_url", "embedding_x_dep_ticket",
)


def _read(reader: Callable | None, name: str) -> str:
    value = reader(name) if reader is not None else None
    return str(value if value not in (None, "") else os.getenv(name, "")).strip()


def initial_mode(reader: Callable | None = None) -> str:
    """명시된 LLM provider, embedding provider, COURSE_ENV 순서로 초기 선택한다."""
    for field in ("LLM_PROVIDER", "EMBED_PROVIDER", "COURSE_ENV"):
        value = _read(reader, field).lower()
        if value in ("openai", "out", "outside"):
            return "openai"
        if value in ("samsung", "inside"):
            return "samsung"
    return "demo"


def resolve_settings(mode: str, reader: Callable | None = None) -> dict:
    mode = MODE_ALIASES.get(mode, mode)
    if mode not in ("demo", "openai", "samsung"):
        raise ValueError("실행 모드는 demo, openai, samsung 중 하나여야 합니다.")
    settings = {name: _read(reader, name) for name in FIELDS}
    settings["mode"] = mode
    settings["llm_provider"] = settings["embed_provider"] = mode
    if mode == "openai":
        settings["model"] = settings["OPENAI_MODEL"]
        settings["OPENAI_MODEL"] = settings["model"]
    settings["embed_model"] = settings["OPENAI_EMBEDDING_MODEL"] if mode == "openai" else "사내 임베딩"
    return settings


def missing_settings(settings: dict, rag: bool = False) -> list[str]:
    mode = settings["mode"]
    if mode == "demo":
        return []
    if mode == "openai":
        fields = ["OPENAI_API_KEY", "OPENAI_MODEL"]
        if rag:
            fields.append("OPENAI_EMBEDDING_MODEL")
    else:
        fields = ["api_base_url", "model", "credential_key", "send_system_name", "user_id"]
        if rag:
            fields += ["embedding_api_url", "embedding_x_dep_ticket"]
    return [field for field in fields if not settings.get(field)]


def cache_fingerprint(settings: dict, chunk_size: int) -> str:
    """인증·endpoint·모델·PDF·청킹이 다른 인덱스는 공유하지 않는다."""
    from documents import pdf_fingerprint
    payload = {field: settings.get(field, "") for field in FIELDS}
    payload.update(mode=settings["mode"], chunk_size=chunk_size, pdf=pdf_fingerprint())
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def gateway_headers(settings: dict) -> dict:
    return {
        "x-dep-ticket": settings["credential_key"],
        "Send-System-Name": settings["send_system_name"],
        "User-Id": settings["user_id"], "User-Type": "AD_ID",
        "Prompt-Msg-Id": str(uuid.uuid4()), "Completion-Msg-Id": str(uuid.uuid4()),
    }


def model_options(settings: dict) -> dict:
    if settings["mode"] == "samsung" or settings.get("OPENAI_BASE_URL"):
        # 사내 게이트웨이와 OpenAI 호환 서버(NVIDIA Nemotron 등)는 생각 단계를 끈다(켜 두면 답이 비거나 느리다)
        return {"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}
    return {"reasoning_effort": "none"} if settings["model"] == "gpt-6-luna" else {}


def client_options(settings: dict) -> dict:
    if settings["mode"] == "samsung":
        return {"api_key": "samsung-gateway", "base_url": settings["api_base_url"],
                "default_headers": gateway_headers(settings)}
    if settings.get("OPENAI_BASE_URL"):  # OpenAI 호환 서버(NVIDIA 등)
        return {"api_key": settings["OPENAI_API_KEY"], "base_url": settings["OPENAI_BASE_URL"]}
    return {"api_key": settings["OPENAI_API_KEY"]}


class SamsungEmbeddings(Embeddings):
    """수업 config와 같은 x-dep-ticket 인증, input 목록, 10개 배치."""

    def __init__(self, settings: dict):
        self.url = settings["embedding_api_url"].rstrip("/") + "/v1/embeddings"
        self.headers = {"Content-Type": "application/json", "x-dep-ticket": settings["embedding_x_dep_ticket"]}

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = []
        for offset in range(0, len(texts), 10):
            batch = texts[offset:offset + 10]
            response = requests.post(self.url, json={"input": batch}, headers=self.headers, timeout=120)
            response.raise_for_status()
            data = response.json()["data"]
            if len(data) != len(batch):
                raise ValueError("사내 임베딩 응답 개수가 요청과 다릅니다.")
            if all("index" in item for item in data):
                data = sorted(data, key=lambda item: item["index"])
            result.extend(item["embedding"] for item in data)
        return result

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
