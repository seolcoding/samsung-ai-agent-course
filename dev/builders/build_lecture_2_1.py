"""Chapter01 2-1 강의 노트북을 조립한다. 슬라이드·설명·퀴즈만 담고 실습 코드는 넣지 않는다(실습은 2-1_langgraph_LAB).

실행(프로젝트 루트): uv run python dev/builders/build_lecture_2_1.py
입력: dev/builders/2-1_cells.json(설명 셀·퀴즈·강사용 메모, C 수준)
출력: course/Chapter01/notebooks/2-1_langgraph_LEC.ipynb (출력 없음)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
OUT = COURSE / "Chapter01" / "notebooks" / "2-1_langgraph_LEC.ipynb"


def build():
    text = json.loads((HERE / "2-1_cells.json").read_text(encoding="utf-8"))
    nb = Notebook(COURSE / "Chapter01" / "assets" / "quizzes" / "2-1", "../assets/quizzes/2-1")

    def v(key):  # 설명 셀과 그 강사용 메모
        nb.md(text[key])
        nb.meta(text.get(key + "__meta"))

    def slides(*pages):
        nb.code(f'show_slides("2-1", {list(pages)})')

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

    nb.h(2, "1. LangGraph의 필요성")
    nb.h(3, "1.1 Cyclic Graph와 반복 추론")
    slides(3, 4)
    v("p4")
    quiz("q11")
    v("sum11")
    nb.h(3, "1.2 LangChain과 LangGraph 비교")
    slides(5)
    v("p5")
    quiz("q12")
    v("sum12")

    nb.h(2, "2. 그래프 구성 요소")
    nb.h(3, "2.1 Node, Edge, State")
    slides(6, 7)
    v("p7")
    slides(8)
    v("p8")
    quiz("q21")
    v("sum21")
    nb.h(3, "2.2 State Schema: TypedDict와 Pydantic")
    slides(9)
    v("p9")
    quiz("q22")
    v("sum22")
    nb.h(3, "2.3 Reducer")
    slides(10)
    v("p10")
    quiz("q23")
    v("sum23")

    nb.h(2, "3. 안정적인 Agent 실행")
    nb.h(3, "3.1 Checkpointer와 상태 영속화")
    slides(11, 12)
    v("p12")
    quiz("q31")
    v("sum31")
    nb.h(3, "3.2 Human-in-the-loop")
    slides(13)
    v("p13")
    slides(14)
    v("p14")
    quiz("q32")
    v("sum32")

    nb.h(2, "4. 정리 퀴즈")
    nb.quiz_file("final", text["final"])
    nb.md(text["closing"])
    nb.finish(OUT)


if __name__ == "__main__":
    build()
