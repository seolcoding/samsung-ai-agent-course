"""연결 설정 패키지(모델·임베딩·RAGaaS).

불러오기만 하면(import config, from config.llm import get_llm 등) 다음을 한다.
1. 저장소 맨 위의 .env를 읽는다(지금 폴더에서 위로 올라가며 처음 만나는 .env).
2. .env의 COURSE_ENV에 맞춰 연결 방식을 정한다.
     COURSE_ENV=samsung  사내(삼성 인트라넷): LLM·임베딩·RAGaaS 모두 사내 API
     COURSE_ENV=out      사외: LLM·임베딩은 OpenAI, RAGaaS는 모의 응답(mock)
   .env에 LLM_PROVIDER·EMBED_PROVIDER·RAG_PROVIDER를 직접 적었다면 그 값이 우선한다.

설정이 제대로 되었는지는 config.check로 확인한다.
    uv run python -m config.check          (노트북에서는 from config.check import check_env; check_env())
"""

import os

from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv(usecwd=True) or find_dotenv()  # 찾지 못하면 빈 문자열
load_dotenv(ENV_FILE or None)

# COURSE_ENV 값 → 연결 방식. 사외를 뜻하는 다른 이름도 받는다.
MODES = {
    "samsung": {"LLM_PROVIDER": "samsung", "EMBED_PROVIDER": "samsung", "RAG_PROVIDER": "samsung"},
    "out": {"LLM_PROVIDER": "openai", "EMBED_PROVIDER": "openai", "RAG_PROVIDER": "mock"},
}
ALIASES = {"사내": "samsung", "intranet": "samsung", "사외": "out", "external": "out", "openai": "out"}

MODE = os.getenv("COURSE_ENV", "").strip().lower()
MODE = ALIASES.get(MODE, MODE)
for _name, _value in MODES.get(MODE, {}).items():
    os.environ.setdefault(_name, _value)  # .env에 직접 적은 PROVIDER가 있으면 건드리지 않는다
