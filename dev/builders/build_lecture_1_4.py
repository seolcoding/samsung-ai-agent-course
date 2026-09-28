"""Chapter01 1-4 강의 노트북을 조립한다. 슬라이드·설명·퀴즈만 담고 실습 코드는 넣지 않는다(실습은 1-4_rag_LAB).

실행(프로젝트 루트): uv run python dev/builders/build_lecture_1_4.py
입력: dev/builders/1-4_cells.json(설명 셀·퀴즈·강사용 메모, C 수준)
출력: course/Chapter01/notebooks/1-4_rag_LEC.ipynb (출력 없음), course/assets/quizzes/1-4/*.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
OUT = COURSE / "Chapter01" / "notebooks" / "1-4_rag_LEC.ipynb"


def build():
    text = json.loads((HERE / "1-4_cells.json").read_text(encoding="utf-8"))
    nb = Notebook(COURSE / "assets" / "quizzes" / "1-4", "../../assets/quizzes/1-4")

    def v(key):  # 설명 셀과 그 강사용 메모
        nb.md(text[key])
        nb.meta(text.get(key + "__meta"))

    def slides(*pages):
        nb.code(f'show_slides("1-4", {list(pages)})')

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

    nb.h(2, "1. Retrieval Augmented Generation")
    nb.h(3, "1.1 Fine-Tuning과의 비교")
    slides(3, 4)
    v("p4")
    slides(5)
    v("p5")
    quiz("q11")
    v("sum11")
    nb.h(3, "1.2 Naive → Advanced → Modular RAG 발전 과정")
    slides(6)
    v("p6")
    slides(7)
    v("p7")
    quiz("q12")
    slides(8)
    v("p8")
    v("sum12")

    nb.h(2, "2. RAG 핵심 모듈")
    nb.h(3, "2.1 Loading, Splitting, Embedding")
    slides(9, 10)
    v("p10")
    quiz("q21")
    slides(11)
    v("p11")
    slides(12)
    v("p12")
    v("sum21")
    nb.h(3, "2.2 Storage, Retrieval, Generation")
    slides(13)
    v("p13")
    slides(14)
    v("p14")
    quiz("q22")
    slides(15)
    v("p15")
    v("sum22")

    nb.h(2, "3. 청킹 전략과 임베딩")
    nb.h(3, "3.1 Fixed-size, Recursive, Semantic Chunking")
    slides(16, 17)
    v("p17")
    slides(18)
    v("p18")
    quiz("q31")
    v("sum31")
    nb.h(3, "3.2 임베딩 모델 선택 기준")
    slides(19)
    v("p19")
    quiz("q32")
    v("sum32")

    nb.h(2, "4. 정리 퀴즈")
    nb.quiz_file("final", text["final"])
    nb.md(text["closing"])
    nb.finish(OUT)


if __name__ == "__main__":
    build()
