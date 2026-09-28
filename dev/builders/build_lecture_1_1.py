"""Chapter01 1-1 강의 노트북을 조립한다. 슬라이드·설명·퀴즈만 담는다. 원본에 실습 코드가 없어 LAB은 만들지 않는다.

실행(프로젝트 루트): uv run python dev/builders/build_lecture_1_1.py
입력: dev/builders/1-1_cells.json(설명 셀·퀴즈·강사용 메모, C 수준)
출력: course/Chapter01/notebooks/1-1_design_thinking_LEC.ipynb (출력 없음), course/Chapter01/assets/quizzes/1-1/*.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
OUT = COURSE / "Chapter01" / "notebooks" / "1-1_design_thinking_LEC.ipynb"
CURRICULUM_PAGES = [2, 3, 4, 5]  # 커리큘럼 제안서 PDF에서 표가 있는 쪽(1쪽은 표지)


def build():
    text = json.loads((HERE / "1-1_cells.json").read_text(encoding="utf-8"))
    nb = Notebook(COURSE / "Chapter01" / "assets" / "quizzes" / "1-1", "../assets/quizzes/1-1")

    def v(key):  # 설명 셀과 그 강사용 메모
        nb.md(text[key])
        nb.meta(text.get(key + "__meta"))

    def slides(*pages, deck="1-1"):
        nb.code(f'show_slides("{deck}", {list(pages)})')

    def quiz(key):
        nb.quiz_file(key, [text[key]])

    nb.md(text["title"])
    nb.meta(text["title__meta"])
    nb.code(
        "import sys\n\nsys.path.insert(0, '..')  # 챕터 폴더의 assets 도구를 불러오기 위한 경로\n\n"
        "from assets.widgets import show_quiz, show_slides, slide_setup\n\n"
        "slide_setup()  # 슬라이드 뷰어(PDF.js)를 불러옵니다. 슬라이드가 비어 보이면 이 셀을 다시 실행합니다."
    )

    nb.h(2, "1. 과정 소개")
    nb.h(3, "1.1 4일 과정의 구성")
    slides(*CURRICULUM_PAGES, deck="2026-09-03_커리큘럼_제안서")
    v("course")
    nb.h(3, "1.2 이 노트북의 흐름")
    slides(1, 2)
    v("intro")

    nb.h(2, "2. AI와 머신러닝")
    slides(3, 4)
    v("p4")
    nb.quiz_file("q_ai", [{
        "question": "AI, 머신러닝, 딥러닝(LLM)의 관계로 맞는 것은?",
        "type": "multiple_choice",
        "answers": [
            {"answer": "셋은 서로 관계없는 별개의 분야다", "correct": False,
             "feedback": "머신러닝은 AI의 하위 분야이고, 딥러닝도 머신러닝 안에 있습니다."},
            {"answer": "AI 안에 머신러닝, 그 안에 딥러닝이 있다", "correct": True,
             "feedback": "머신러닝은 AI의 하위 분야이고, 딥러닝은 인공 신경망을 쓰는 머신러닝의 하위 분류입니다."},
            {"answer": "머신러닝 안에 AI, 그 안에 딥러닝이 있다", "correct": False,
             "feedback": "포함 관계가 거꾸로입니다. 가장 넓은 것이 AI입니다."},
            {"answer": "딥러닝 안에 AI, 그 안에 머신러닝이 있다", "correct": False,
             "feedback": "딥러닝이 가장 좁은 분야입니다. LLM은 이 딥러닝의 산출물입니다."},
        ],
    }])

    nb.h(2, "3. 머신러닝 예시")
    slides(5, 6)
    v("p6")
    slides(7, 8)
    v("p8")
    nb.quiz_file("q_ml", [{
        "question": "기온으로 아이스크림 판매량을 예측하는 예시에서, 머신러닝의 \"학습\"이 하는 일은?",
        "type": "multiple_choice",
        "answers": [
            {"answer": "사람이 판매 규칙을 하나하나 코드로 적는다", "correct": False,
             "feedback": "머신러닝은 규칙을 직접 프로그래밍하지 않아도 데이터로 동작하게 합니다."},
            {"answer": "새로 들어온 기온 값을 저장해 둔다", "correct": False,
             "feedback": "새 기온은 학습이 끝난 뒤 예측할 때 쓰는 입력입니다."},
            {"answer": "데이터로 a와 b 같은 파라미터를 조정한다", "correct": True,
             "feedback": "가진 데이터를 반복해 넣어 a와 b를 조정하고, 그 결과가 모델이 됩니다."},
            {"answer": "그래프를 그려 사람이 판매량을 읽는다", "correct": False,
             "feedback": "그래프는 관계를 보여 줄 뿐이고, 예측은 조정된 식(모델)이 합니다."},
        ],
    }])

    nb.h(2, "4. LLM")
    nb.h(3, "4.1 LLM은 무엇을 배우는가")
    slides(9, 10)
    v("p10")
    nb.md(text["q_fox_lead"])
    quiz("q_fox")
    slides(11)
    v("p11")
    nb.h(3, "4.2 다음 단어 예측기의 단점")
    slides(12)
    v("p12")
    quiz("q_math")
    nb.h(3, "4.3 Instruction Tuning과 챗봇")
    slides(13, 14)
    v("p14")

    nb.h(2, "5. LLM의 함수 호출")
    slides(15, 16)
    v("p16")
    slides(17)
    v("p17")
    slides(18)
    v("p18")
    quiz("q_fc")
    slides(19)
    v("p19")

    nb.h(2, "6. Agent")
    slides(20)
    v("p20")
    quiz("q_react")

    nb.h(2, "7. LangChain과 LangGraph")
    slides(21, 22)
    v("p22")
    quiz("q_lg")

    nb.h(2, "8. 정리 퀴즈")
    nb.quiz_file("final", text["final"])
    nb.md(text["closing"])
    nb.finish(OUT)


if __name__ == "__main__":
    build()
