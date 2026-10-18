"""Streamlit 챗봇을 브라우저 없이 확인한다(grade-task 스킬용).

실행(저장소 맨 위):
    uv run --env-file .env python .agents/skills/grade-task/scripts/check_streamlit.py course/Chapter01/tasks/1-4_task.py --task 1-4

--task <번호>면 그 챗봇 과제의 정해진 순서(선택 상자 바꾸기, 질문, 버튼 누르기)대로 앱을 움직인다.
동작마다 새로 생긴 채팅 메시지(말풍선의 ⚠️ 오류·caption 포함), 실행 기록 상자(expander), 화면의 버튼,
사이드바 "✅ 과제 확인" 결과(🟢/⛔/❔)를 출력한다. 앱이 print한 터미널 기록과 traceback도 그 사이에 그대로 나온다.
한 동작에서 오류가 나면(앱이 멈추거나 말풍선에 ⚠️가 나오면) 오류를 출력하고 다음 동작으로 넘어간다.
--task가 없으면 질문 두 개와 "대화 지우기"만 확인한다.
"""
import argparse
import sys
from pathlib import Path

from streamlit import config
from streamlit.testing.v1 import AppTest

config.set_option("logger.enableRich", False)  # 앱 오류를 색 없는 보통 traceback으로 출력한다

TIMEOUT = 300  # 한 번 실행을 기다리는 시간(초). 첫 임베딩은 느릴 수 있다

POLICY_Q = "반려견이 수술을 받으면 수술비도 보장되나요?"
HELPDESK_Q = "노트북이 갑자기 느려졌어요. 먼저 확인할 것 하나만 알려 주세요."
# 과제별 순서: ("select", 상자 이름, 값) / ("toggle", 이름, 값) / ("ask", 질문) / ("click", 버튼 이름)
SCENARIOS = {
    "1-2": [
        ("select", "연결 방식", "requests로 직접"),
        ("ask", HELPDESK_Q),
        ("select", "연결 방식", "LangChain stream"),
        ("ask", HELPDESK_Q),
        ("click", "✅ 과제 확인"),
    ],
    "1-3": [
        ("select", "답 말투", "한 문장으로"),
        ("ask", "내 이름은 민수야. 기억해 줘."),
        ("ask", "내 이름이 뭐야?"),
        ("click", "✅ 과제 확인"),
    ],
    "1-4": [
        ("ask", POLICY_Q),
        ("ask", "삼성전자의 오늘 주가는 얼마야?"),
        ("click", "✅ 과제 확인"),
    ],
    "2-1": [
        ("ask", "안녕! 내 이름은 민수야."),
        ("ask", POLICY_Q),
        ("ask", "내 이름이 뭐야?"),
        ("click", "대화 지우기"),
        ("ask", "내 이름이 뭐야?"),
        ("click", "✅ 과제 확인"),
    ],
}
DEFAULT = [("ask", "파이썬이 뭐야? 한 문장으로 답해 줘."), ("ask", "방금 말한 것을 예시 하나로 설명해 줘."),
           ("click", "대화 지우기")]


def short(text, n=300):
    return str(text).replace("\n", " ")[:n]


def find(elements, label):
    return next((e for e in elements if e.label == label), None)


def message_count(at):
    """대화 기록(st.session_state.messages)에 쌓인 메시지 수. 이 뒤에 그려진 메시지가 이번 동작에서 새로 생긴 것이다."""
    return len(at.session_state["messages"]) if "messages" in at.session_state else 0


def report(at, seen):
    """이번 실행에서 새로 생긴 채팅 메시지와 실행 기록 상자, 화면의 버튼을 출력한다."""
    msgs = list(at.chat_message)
    for m in msgs[seen:]:
        texts = [md.value for md in m.markdown] + [c.value for c in m.caption] + [e.value for e in m.error]
        print(f"   💬 {m.name}: {short(' '.join(texts))}")
    for e in at.expander:
        body = " ".join(c.value for c in e.code) or " ".join(md.value for md in e.markdown)
        print(f"   📂 {e.label}: {short(body)}")
    for md in at.sidebar.markdown:  # "✅ 과제 확인" 결과
        if any(mark in md.value for mark in ("✅", "🟢", "⛔", "❔")):
            print(f"   ✅ {md.value}")
    buttons = [b.label for b in at.main.button]
    if buttons:
        print(f"   🔘 화면 버튼: {buttons}")
    print(f"   (채팅 메시지 모두 {len(msgs)}개)")


def step(at, action):
    kind, *args = action
    if kind == "ask":
        if not at.chat_input:
            return "질문 입력창(st.chat_input)이 없음"
        print(f"\n▶ 질문: {args[0]}")
        at.chat_input[0].set_value(args[0]).run()
    elif kind in ("select", "toggle"):
        elements = at.sidebar.selectbox if kind == "select" else at.sidebar.toggle
        element = find(elements, args[0])
        if element is None:
            return f"사이드바에서 '{args[0]}'을(를) 찾지 못함"
        print(f"\n▶ 사이드바 '{args[0]}' = {args[1]}")
        element.set_value(args[1]).run()
    elif kind == "click":
        button = find(at.button, args[0])
        if button is None:
            return f"'{args[0]}' 버튼을 찾지 못함"
        print(f"\n▶ '{args[0]}' 버튼 누름")
        button.click().run()
    return None


def main():
    sys.stdout.reconfigure(line_buffering=True)  # 파이프로 받아도 앱 오류(stderr)와 출력 순서가 섞이지 않게 한다
    parser = argparse.ArgumentParser()
    parser.add_argument("app")
    parser.add_argument("--task", choices=sorted(SCENARIOS))
    opts = parser.parse_args()

    # AppTest는 상대 경로를 이 스크립트 폴더 기준으로 찾으므로 절대 경로로 바꾼다
    at = AppTest.from_file(str(Path(opts.app).resolve()), default_timeout=TIMEOUT).run()
    if at.exception:
        print(f"✖ 앱을 여는 중 오류 | {at.exception[0].message} | 과제 파일을 고친다")
        return 1
    print(f"✔ 앱 열림: 사이드바 선택 상자 {[s.label for s in at.sidebar.selectbox]}, "
          f"토글 {[t.label for t in at.sidebar.toggle]}, 버튼 {[b.label for b in at.sidebar.button]}")

    problems, errors = 0, 0
    for action in SCENARIOS.get(opts.task, DEFAULT):
        seen = message_count(at)
        problem = step(at, action)
        if problem:
            print(f"\n✖ {action} 건너뜀 | {problem}")
            problems += 1
            continue
        report(at, seen)
        failure = at.exception[0].message if at.exception else next((e.value for e in at.main.error), None)
        if failure:
            print(f"   ✖ 실행 중 오류 | {short(failure, 500)} | 이 동작이 확인하는 목표는 통과로 치지 않는다")
            errors += 1
    print(f"\n✔ 끝: 건너뛴 동작 {problems}개, 오류 난 동작 {errors}개")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
