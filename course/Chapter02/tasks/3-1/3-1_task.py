"""3-1 과제: 약관 검색 도구 Agent

실행(저장소 맨 위에서):
    uv run --env-file .env python course/Chapter02/tasks/3-1/3-1_task.py

할 일과 프롬프트 힌트는 같은 폴더의 README.md에 있습니다.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# 약관 PDF(노트북 폴더의 data)
PDF_PATH = Path(__file__).resolve().parents[2] / "notebooks" / "data" / "meritz_pet_insurance.pdf"


# ✍️ 목표 1: config.check로 설정을 점검합니다(모델·임베딩을 실제로 한 번씩 호출). ⛔이 있으면 여기서 멈춥니다.
print("✍️ 목표 1은 아직 비어 있습니다. README.md의 할 일을 봅니다.")


from config.embeddings import get_embeddings  # noqa: E402 — 점검을 먼저 하고 모델을 준비합니다
from config.llm import get_llm  # noqa: E402

llm = get_llm()
embeddings = get_embeddings()


# ✍️ 목표 2: 약관 PDF로 Chroma 검색기(조각 3개)를 만들고 @tool search_policy로 감쌉니다.
print("✍️ 목표 2는 아직 비어 있습니다.")


# ✍️ 목표 3: agent → (tools_condition) → tools → agent로 도는 그래프 policy_agent를 만듭니다.
print("✍️ 목표 3은 아직 비어 있습니다.")


# ✍️ 목표 4: 약관 질문 하나와 인사 하나를 policy_agent로 실행하고, 메시지를 pretty_print()로 출력합니다.
print("✍️ 목표 4는 아직 비어 있습니다.")
