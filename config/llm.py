import os
import uuid

from dotenv import load_dotenv

load_dotenv()

os.environ['OPENAI_API_KEY'] = 'api_key'

def get_llm(**kwargs):
    """
    LLM_PROVIDER 환경변수에 따라 LLM 인스턴스를 반환한다.
    - openai (기본값): OpenAI ChatOpenAI
    - samsung: 삼성 사내 LLM (아래 주석 블록 활성화)
    """
    provider = os.getenv("LLM_PROVIDER", "samsung")

    # OpenAI 모델을 LangChain으로 불러오는 방법.
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        # OpenAI SDK와 유사하게 API Key는 환경변수에서 가져오므로
        # 모델만 설정하면 됩니다.
        kwargs.setdefault("model", os.getenv("OPENAI_MODEL", "gpt-5-mini"))
        return ChatOpenAI(**kwargs)

    # 삼성 사내 LLM 설정. 사내 망에서만 동작함.
    elif provider == "samsung":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("model"),
            base_url=os.getenv("api_base_url"),
            default_headers={
                "x-dep-ticket": os.getenv("credential_key"),
                "Send-System-Name": os.getenv("send_system_name"),
                "User-Id": os.getenv("user_id"),
                "User-Type": "AD_ID",
                "Prompt-Msg-Id": str(uuid.uuid4()),
                "Completion-Msg-Id": str(uuid.uuid4()),
            },
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False,
                }
            },
        )

