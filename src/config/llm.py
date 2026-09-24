import os
import uuid

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'{name} 환경변수가 필요합니다. 실행할 환경 파일을 확인하세요.')
    return value

def get_llm(**kwargs):
    """
    LLM_PROVIDER 환경변수에 따라 LLM 인스턴스를 반환한다.
    - openai: OpenAI ChatOpenAI (사외)
    - samsung (기본값): 삼성 사내 LLM
    """
    provider = os.getenv("LLM_PROVIDER", "samsung").strip().lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        if "model" not in kwargs:
            kwargs["model"] = _required("OPENAI_MODEL")
        if kwargs["model"] == "gpt-6-luna":
            # 이 수업의 도구 호출 실습은 Chat Completions를 사용한다.
            kwargs.setdefault("reasoning_effort", "none")
        return ChatOpenAI(api_key=_required("OPENAI_API_KEY"), **kwargs)

    elif provider == "samsung":
        from langchain_openai import ChatOpenAI
        if "model" not in kwargs:
            kwargs["model"] = _required("model")
        return ChatOpenAI(
            # 사내 게이트웨이는 x-dep-ticket으로 인증한다. SDK 필수값만 채운다.
            api_key="samsung-gateway",
            base_url=_required("api_base_url"),
            default_headers={
                "x-dep-ticket": _required("credential_key"),
                "Send-System-Name": _required("send_system_name"),
                "User-Id": _required("user_id"),
                "User-Type": "AD_ID",
                "Prompt-Msg-Id": str(uuid.uuid4()),
                "Completion-Msg-Id": str(uuid.uuid4()),
            },
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False,
                }
            },
            **kwargs,
        )

    raise ValueError(f"지원하지 않는 LLM_PROVIDER: {provider!r}. 'openai' 또는 'samsung'을 사용하세요.")
