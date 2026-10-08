"""Chapter01 1-2 강의 노트북을 조립한다. 슬라이드·설명·퀴즈만 담고 실습 코드는 넣지 않는다(실습은 1-2_llm_api_LAB).

실행(프로젝트 루트): uv run python dev/builders/build_lecture_1_2.py
입력: dev/builders/1-2_cells_common.json(공통 셀·퀴즈), 1-2_cells_C.json(설명 셀, C 수준)
출력: course/Chapter01/notebooks/1-2_llm_api_LEC.ipynb (출력 없음)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
OUT = COURSE / "Chapter01" / "notebooks" / "1-2_llm_api_LEC.ipynb"
# p9 예시의 토큰 목록. 2.1 퀴즈의 정답(목록 길이)을 여기서 계산한다.
P9_TOKENS = ["Lang", "Chain", "으로", " AI", " Agent", "를", " 만든", "다", "."]
P9_SENTENCE = "LangChain으로 AI Agent를 만든다."


def build():
    common = json.loads((HERE / "1-2_cells_common.json").read_text(encoding="utf-8"))
    text = json.loads((HERE / "1-2_cells_C.json").read_text(encoding="utf-8"))
    nb = Notebook(COURSE / "Chapter01" / "assets" / "quizzes" / "1-2", "../assets/quizzes/1-2")

    def v(key):  # 설명 셀과 그 강사용 메모
        nb.md(text[key])
        nb.meta(text.get(key + "__meta"))

    def slides(*pages):
        nb.code(f'show_slides("1-2", {list(pages)})')

    def quiz(key):
        nb.quiz_file(key, [common[key]])

    nb.md(common["title"])
    nb.meta(common.get("title__meta", "").replace("{VERSION}", "C"))
    nb.code(
        "import json\nimport sys\n\nsys.path.insert(0, '..')  # 챕터 폴더의 assets 도구를 불러오기 위한 경로\n\n"
        "from assets.widgets import show_order_quiz, show_quiz, show_slides, slide_setup\n\n"
        "slide_setup()  # 슬라이드 뷰어(PDF.js)를 불러옵니다. 슬라이드가 비어 보이면 이 셀을 다시 실행합니다."
    )
    slides(1, 2)
    v("intro")

    nb.h(2, "1. LLM의 학습과 추론")
    nb.h(3, "1.1 사전 학습과 Instruction Tuning")
    nb.md(common["q11_lead"])
    quiz("q11")
    slides(3, 4)
    v("p4")
    slides(5)
    v("p5")
    v("sum11")
    nb.h(3, "1.2 다음 토큰 예측과 생성 과정")
    slides(6)
    v("p6")
    nb.md("**먼저 예측해 봅니다.** 다음 쪽을 보기 전에, 요청을 보내고 응답을 받기까지의 순서를 맞혀 보세요.")
    (nb.quiz_dir / "order12.json").parent.mkdir(parents=True, exist_ok=True)
    (nb.quiz_dir / "order12.json").write_text(json.dumps(common["order12"], ensure_ascii=False, indent=1), encoding="utf-8")
    nb.code('show_order_quiz(**json.load(open("../assets/quizzes/1-2/order12.json", encoding="utf-8")))')
    slides(7)
    v("p7")
    v("sum12")

    nb.h(2, "2. Tokenization")
    nb.h(3, "2.1 토큰의 의미")
    slides(8, 9)
    v("p9")
    n, words = len(P9_TOKENS), len(P9_SENTENCE.split())
    nb.quiz_file("q21", [{
        "question": f'슬라이드 예시에서 "{P9_SENTENCE}"는 몇 개의 토큰으로 나뉘었나요?',
        "type": "multiple_choice",
        "answers": [
            {"answer": f"{words}개", "correct": False, "feedback": "띄어쓰기로 나눈 단어 수입니다. 토큰 수와는 다릅니다."},
            {"answer": f"{n - 2}개", "correct": False, "feedback": "한 단어가 둘로 나뉜 곳을 다시 세어 보세요."},
            {"answer": f"{n}개", "correct": True, "feedback": "예시 목록의 항목 수입니다. 토큰은 단어의 일부나 조사로도 나뉩니다."},
            {"answer": f"{n + 3}개", "correct": False, "feedback": "슬라이드 예시 목록에 든 항목만 셉니다."},
        ],
    }])
    v("sum21")
    nb.h(3, "2.2 토큰 수와 비용")
    slides(10)
    v("p10")
    slides(11)
    v("p11")
    quiz("q22")
    v("sum22")

    nb.h(2, "3. Context Window")
    nb.h(3, "3.1 Context Window")
    slides(12, 13, 14)
    v("p14")
    v("sum31")
    nb.h(3, "3.2 입력 품질과 출력 품질")
    slides(15, 16)
    v("p16")
    v("sum32")

    nb.h(2, "4. LLM API의 대화 구조")
    nb.h(3, "4.1 System, User, Assistant 역할")
    slides(17, 18)
    v("p18")
    quiz("q41")
    v("sum41")
    nb.h(3, "4.2 모델 파라미터의 영향")
    slides(19)
    v("p19")
    quiz("q42")
    v("sum42")

    nb.h(2, "5. 정리 퀴즈")
    nb.quiz_file("final", common["final"])
    nb.md(common["closing"])
    nb.finish(OUT)


if __name__ == "__main__":
    build()
