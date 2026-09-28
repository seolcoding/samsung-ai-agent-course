"""삼성 사내 API 공통 설정. 사내망에서만 동작한다.

LLM·임베딩·RAGaaS 실습이 같은 주소와 인증 헤더를 쓰도록 이곳에 모은다.
값은 환경 파일에서 읽고, 화면에는 출력하지 않는다.
"""

import os
import uuid

from dotenv import load_dotenv

load_dotenv()


def require_env(*names: str) -> dict[str, str]:
    """환경변수 값을 모아 돌려준다. 비어 있는 이름이 있으면 그 목록을 알려 주고 멈춘다."""
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"사내 API 설정이 부족합니다: {missing}. 실행할 환경 파일을 확인하세요.")
    return {name: os.environ[name] for name in names}


def llm_config() -> dict:
    """사내 LLM 게이트웨이의 주소·모델·인증 헤더. 부를 때마다 새 메시지 ID를 만든다."""
    env = require_env("api_base_url", "model", "credential_key", "send_system_name", "user_id")
    return {
        "base_url": env["api_base_url"],
        "model": env["model"],
        "headers": {
            "x-dep-ticket": env["credential_key"],
            "Send-System-Name": env["send_system_name"],
            "User-Id": env["user_id"],
            "User-Type": "AD_ID",
            "Prompt-Msg-Id": str(uuid.uuid4()),
            "Completion-Msg-Id": str(uuid.uuid4()),
        },
    }


def embedding_config() -> dict:
    """사내 임베딩 API의 주소와 인증 헤더."""
    env = require_env("embedding_api_url", "embedding_x_dep_ticket")
    return {
        "url": f'{env["embedding_api_url"].rstrip("/")}/v1/embeddings',
        "headers": {
            "Content-Type": "application/json",
            "x-dep-ticket": env["embedding_x_dep_ticket"],
        },
    }


def ragaas_config(api_key: str | None = None) -> dict:
    """사내 RAGaaS의 기본 주소와 인증 헤더. x-dep-ticket과 api-key가 모두 필요하다."""
    env = require_env("search_url", "rag_credential_key")
    api_key = api_key or os.getenv("rag_api_key")
    if not api_key:
        raise RuntimeError("사내 API 설정이 부족합니다: ['rag_api_key']. 실행할 환경 파일을 확인하세요.")
    return {
        "url": f'{env["search_url"].rstrip("/")}/dsllmrag/elastic/v2',
        "headers": {
            "Content-Type": "application/json",
            "x-dep-ticket": env["rag_credential_key"],
            "api-key": api_key,
        },
    }
