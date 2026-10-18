"""Streamlit 과제 앱을 브라우저 없이 확인한다(grade-task 스킬용).

실행(저장소 맨 위): uv run --env-file .env python .agents/skills/grade-task/scripts/check_streamlit.py <앱 파일>
질문 두 개를 보낸 뒤와 사이드바 "대화 지우기" 버튼을 누른 뒤의 채팅 메시지를 출력한다.
"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

QUESTIONS = ["파이썬이 뭐야? 한 문장으로 답해 줘.", "방금 말한 것을 예시 하나로 설명해 줘."]
TIMEOUT = 120  # 모델 호출을 기다리는 시간(초)


def show(at, title):
    msgs = at.chat_message
    print(f"✔ {title}: 채팅 메시지 {len(msgs)}개")
    for m in msgs:
        text = " ".join(md.value for md in m.markdown)[:80].replace("\n", " ")
        print(f"   - {m.name}: {text}")


def main(path):
    # AppTest는 상대 경로를 이 스크립트 폴더 기준으로 찾으므로 절대 경로로 바꾼다
    at = AppTest.from_file(str(Path(path).resolve()), default_timeout=TIMEOUT).run()
    if at.exception:
        print(f"✖ 앱을 여는 중 오류 | {at.exception[0].message} | 과제 파일을 고친다")
        return 1
    for q in QUESTIONS:
        if not at.chat_input:
            print("✖ 질문 입력창을 찾지 못함 | st.chat_input이 없음 | 과제 파일을 고친다")
            return 1
        at.chat_input[0].set_value(q).run()
        if at.exception:
            print(f"✖ 질문 처리 중 오류 | {at.exception[0].message} | 과제 파일을 고친다")
            return 1
    show(at, "질문 2개 뒤")
    roles = [b for b in at.sidebar.selectbox]
    print(f"✔ 사이드바 선택 상자 {len(roles)}개: {[s.label for s in roles]}")
    clear = [b for b in at.sidebar.button if "지우" in b.label]
    if not clear:
        print("✖ 사이드바에서 '대화 지우기' 버튼을 찾지 못함")
        return 1
    clear[0].click().run()
    show(at, "'대화 지우기' 뒤")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
