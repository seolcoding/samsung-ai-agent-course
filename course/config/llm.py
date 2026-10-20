import os

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
            # gpt-6 계열은 도구가 있으면 Responses API로 자동 전환되므로 고정한다.
            kwargs.setdefault("use_responses_api", False)
        if os.getenv("OPENAI_BASE_URL"):
            # OpenAI 호환 서버(NVIDIA Nemotron 등)는 사내 게이트웨이처럼 생각 단계를 끈다(켜 두면 느리고 답이 빌 수 있다)
            kwargs.setdefault("extra_body", {"chat_template_kwargs": {"enable_thinking": False}})
        return ChatOpenAI(api_key=_required("OPENAI_API_KEY"), **kwargs)

    elif provider == "samsung":
        from langchain_openai import ChatOpenAI
        from config.samsung import llm_config
        samsung = llm_config()
        kwargs.setdefault("model", samsung["model"])
        return ChatOpenAI(
            # 사내 게이트웨이는 x-dep-ticket으로 인증한다. SDK 필수값만 채운다.
            api_key="samsung-gateway",
            base_url=samsung["base_url"],
            default_headers=samsung["headers"],
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False,
                }
            },
            **kwargs,
        )

    raise ValueError(f"지원하지 않는 LLM_PROVIDER: {provider!r}. 'openai' 또는 'samsung'을 사용하세요.")
