"""Chapter01 1-3 강의 노트북을 조립한다. 슬라이드·설명·퀴즈만 담고 실습 코드는 넣지 않는다(실습은 1-3_langchain_LAB).

실행(프로젝트 루트): uv run python dev/builders/build_lecture_1_3.py
입력: dev/builders/1-3_cells.json(설명 셀 C 수준, 퀴즈, `<key>__meta` 강사용 메모)
출력: course/Chapter01/notebooks/1-3_langchain_LEC.ipynb (출력 없음), 퀴즈 파일 course/assets/quizzes/1-3/
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
OUT = COURSE / "Chapter01" / "notebooks" / "1-3_langchain_LEC.ipynb"


def build():
    text = json.loads((HERE / "1-3_cells.json").read_text(encoding="utf-8"))
    nb = Notebook(COURSE / "assets" / "quizzes" / "1-3", "../../assets/quizzes/1-3")

    def v(key):  # 설명 셀과 그 강사용 메모
        nb.md(text[key])
        nb.meta(text.get(key + "__meta"))

    def slides(*pages):
        nb.code(f'show_slides("1-3", {list(pages)})')

    def quiz(key):
        nb.quiz_file(key, [text[key]])

    nb.md(text["title"])
    nb.meta(text.get("title__meta"))
    nb.code(
        "import sys\n\nsys.path.insert(0, '../..')  # course/assets 도구를 불러오기 위한 경로\n\n"
        "from assets.widgets import show_quiz, show_slides, slide_setup\n\n"
        "slide_setup()  # 슬라이드 뷰어(PDF.js)를 불러옵니다. 슬라이드가 비어 보이면 이 셀을 다시 실행합니다."
    )
    slides(1, 2)
    v("intro")

    nb.h(2, "1. LCEL과 Runnable")
    nb.h(3, "1.1 LCEL의 설계 철학")
    slides(3, 4)
    v("p4")
    slides(5)
    v("p5")
    quiz("q11")
    nb.md(text["sum11"])
    nb.h(3, "1.2 Runnable 인터페이스")
    slides(6)
    v("p6")
    slides(7)
    v("p7")
    quiz("q12")
    nb.md(text["sum12"])

    nb.h(2, "2. Tool Calling")
    nb.h(3, "2.1 Tool Schema와 도구 선택")
    slides(8, 9)
    v("p9")
    quiz("q21")
    nb.md(text["sum21"])
    nb.h(3, "2.2 응답 파싱과 실행 흐름")
    slides(10)
    v("p10")
    slides(11)
    v("p11")
    quiz("q22")
    nb.md(text["sum22"])

    nb.h(2, "3. 구조화된 출력과 메모리")
    nb.h(3, "3.1 Output Parser와 Pydantic")
    slides(12, 13)
    v("p13")
    quiz("q31")
    nb.md(text["sum31"])
    nb.h(3, "3.2 Buffer, Summary, VectorStoreRetriever Memory")
    slides(14)
    v("p14")
    quiz("q32")
    nb.md(text["sum32"])

    nb.h(2, "4. 정리 퀴즈")
    nb.quiz_file("final", text["final"])
    nb.md(text["closing"])
    nb.finish(OUT)


if __name__ == "__main__":
    build()
