"""Chapter01 2-3 강의 노트북을 조립한다. 슬라이드·설명·퀴즈만 담고 실습 코드는 넣지 않는다(실습은 2-3_rag_streamlit_LAB).

실행(프로젝트 루트): uv run python dev/builders/build_lecture_2_3.py
입력: dev/builders/2-3_cells.json(설명·퀴즈·강사용 메모, C 수준)
출력: course/Chapter01/notebooks/2-3_rag_streamlit_LEC.ipynb (출력 없음), 퀴즈 파일 course/assets/quizzes/2-3/
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
OUT = COURSE / "Chapter01" / "notebooks" / "2-3_rag_streamlit_LEC.ipynb"


def build():
    text = json.loads((HERE / "2-3_cells.json").read_text(encoding="utf-8"))
    nb = Notebook(COURSE / "assets" / "quizzes" / "2-3", "../../assets/quizzes/2-3")

    def v(key):  # 설명 셀과 그 강사용 메모
        nb.md(text[key])
        nb.meta(text.get(key + "__meta"))

    def slides(*pages):
        nb.code(f'show_slides("2-3", {list(pages)})')

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

    nb.h(2, "1. Streamlit")
    nb.h(3, "1.1 Streamlit 소개")
    slides(3, 4)
    v("p4")
    quiz("q11")
    nb.h(3, "1.2 Python 코드 기반 웹 UI")
    slides(5)
    v("p5")
    quiz("q12")

    nb.h(2, "2. Streamlit 앱 기본 구성")
    nb.h(3, "2.1 title과 caption")
    slides(6, 7, 8)
    v("p8")
    nb.h(3, "2.2 cache_resource")
    slides(9)
    v("p9")
    quiz("q22")

    nb.h(2, "3. 채팅 인터페이스 구성")
    nb.h(3, "3.1 session_state")
    slides(10, 11)
    v("p11")
    quiz("q31")
    nb.h(3, "3.2 chat_message와 chat_input")
    slides(12)
    v("p12")
    quiz("q32")
    nb.h(3, "3.3 write_stream")
    slides(13)
    v("p13")
    quiz("q33")

    nb.h(2, "4. 정리 퀴즈")
    nb.quiz_file("final", text["final"])
    nb.md(text["closing"])
    nb.finish(OUT)


if __name__ == "__main__":
    build()
