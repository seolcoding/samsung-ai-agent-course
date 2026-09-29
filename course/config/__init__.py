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
import sys

from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv(usecwd=True) or find_dotenv()  # 찾지 못하면 빈 문자열


def _load_env(path):
    """.env를 UTF-8로 읽는다. 옛 메모장이 cp949로 저장했다면 그 방식으로 다시 읽고 알려 준다."""
    try:
        load_dotenv(path or None, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            load_dotenv(path, encoding="cp949")
        except UnicodeDecodeError as e:
            raise RuntimeError(
                f"{path}를 읽을 수 없습니다(UTF-8도 cp949도 아님). VS Code로 열어 오른쪽 아래 인코딩을 눌러 'UTF-8로 저장'을 고릅니다."
            ) from e
        # stdout이 아니라 stderr로 낸다(stdio 방식 MCP 서버가 config를 불러와도 통신을 깨지 않게).
        print(
            f"[주의] {path}가 UTF-8이 아니라 cp949로 저장되어 있어 그 방식으로 읽었습니다. "
            "VS Code로 열어 오른쪽 아래 인코딩을 눌러 'UTF-8로 저장'을 고릅니다.",
            file=sys.stderr,
        )


_load_env(ENV_FILE)

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
