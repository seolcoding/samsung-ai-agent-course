"""Chapter02 4-1 강의 노트북을 조립한다. 슬라이드·설명·퀴즈만 담고 실습 코드는 넣지 않는다(실습은 4-1_harness_LAB).

실행(프로젝트 루트): uv run python dev/builders/build_lecture_4_1.py
입력: dev/builders/4-1_cells.json(설명 셀·퀴즈·강사용 메모, C 수준)
출력: course/Chapter02/notebooks/4-1_harness_LEC.ipynb (출력 없음), course/Chapter02/assets/quizzes/4-1/*.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
OUT = COURSE / "Chapter02" / "notebooks" / "4-1_harness_LEC.ipynb"


def build():
    text = json.loads((HERE / "4-1_cells.json").read_text(encoding="utf-8"))
    nb = Notebook(COURSE / "Chapter02" / "assets" / "quizzes" / "4-1", "../assets/quizzes/4-1")

    def v(key):  # 설명 셀과 그 강사용 메모
        nb.md(text[key])
        nb.meta(text.get(key + "__meta"))

    def slides(*pages):
        nb.code(f'show_slides("4-1", {list(pages)})')

    def quiz(key):
        nb.quiz_file(key, [text[key]])

    nb.md(text["title"])
    nb.meta(text.get("title__meta"))
    nb.code(
        "import sys\n\nsys.path.insert(0, '..')  # 챕터 폴더의 assets 도구를 불러오기 위한 경로\n\n"
        "from assets.widgets import show_quiz, show_slides, slide_setup\n\n"
        "slide_setup()  # 슬라이드 뷰어(PDF.js)를 불러옵니다. 슬라이드가 비어 보이면 이 셀을 다시 실행합니다."
    )
    slides(1, 2)
    v("intro")

    nb.h(2, "1. 하네스 엔지니어링의 등장")
    nb.h(3, "1.1 모델 성능 중심 접근의 한계")
    slides(3, 4)
    v("p4")
    quiz("q11")
    nb.h(3, "1.2 장시간 자율 실행의 요구")
    slides(5)
    v("p5")
    quiz("q12")
    nb.h(3, "1.3 세 가지 엔지니어링의 초점")
    slides(6)
    v("p6")
    quiz("q13")

    nb.h(2, "2. 하네스 엔지니어링이란?")
    nb.h(3, "2.1 AI가 일하는 환경을 설계하는 관점")
    slides(7, 8)
    v("p8")
    quiz("q21")
    nb.h(3, "2.2 위임을 위한 제어 구조")
    slides(9)
    v("p9")
    quiz("q22")
    nb.h(3, "2.3 하네스 설계의 기본 순서")
    slides(10)
    v("p10")
    quiz("q23")

    nb.h(2, "3. Building Effective Agents")
    nb.h(3, "3.1 단순하게 시작하라")
    slides(11, 12)
    v("p12")
    quiz("q31")
    nb.h(3, "3.2 Workflow와 Agent")
    slides(13, 14, 15)
    v("p15")
    quiz("q32")

    nb.h(2, "4. SKILL.md 작성 원칙")
    nb.h(3, "4.1 Skill의 역할")
    slides(16, 17)
    v("p17")
    quiz("q41")
    nb.h(3, "4.2 SKILL.md의 기본 구조")
    slides(18)
    v("p18")
    quiz("q42")
    nb.h(3, "4.3 좋은 SKILL.md의 작성 기준과 순서")
    slides(19, 20)
    v("p20")
    quiz("q43")

    nb.h(2, "5. 정리와 create_deep_agent")
    nb.h(3, "5.1 정리")
    slides(21)
    v("p21")
    nb.h(3, "5.2 create_deep_agent 소개")
    slides(22)
    v("p22")
    quiz("q52")

    nb.h(2, "6. 정리 퀴즈")
    nb.quiz_file("final", text["final"])
    nb.md(text["closing"])
    nb.finish(OUT)


if __name__ == "__main__":
    build()
