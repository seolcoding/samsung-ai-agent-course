"""Streamlit 챗봇을 브라우저 없이 확인한다(grade-task 스킬용).

실행(저장소 맨 위):
    uv run --env-file .env python .agents/skills/grade-task/scripts/check_streamlit.py <앱 파일> --stage N

--stage N이면 챗봇 N단계의 정해진 순서(선택 상자 바꾸기, 질문, 버튼 누르기)대로 앱을 움직인다.
단계마다 새로 생긴 채팅 메시지, 실행 기록 상자(expander), 화면의 버튼을 출력한다.
앱이 print한 터미널 기록(예: "[노드 순서] agent → tools → agent")도 그 사이에 그대로 나온다.
--stage가 없으면 예전처럼 질문 두 개와 "대화 지우기"만 확인한다.
"""
import argparse
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

TIMEOUT = 300  # 한 번 실행을 기다리는 시간(초). 첫 임베딩은 느릴 수 있다

POLICY_Q = "반려견이 수술을 받으면 수술비도 보장되나요?"
# 단계별 순서: ("select", 상자 이름, 값) / ("toggle", 이름, 값) / ("ask", 질문) / ("click", 버튼 이름)
SCENARIOS = {
    1: [
        ("select", "답 말투", "한 문장으로"),
        ("ask", "LLM이 뭐야?"),
    ],
    2: [
        ("select", "답 방식", "대화"),
        ("ask", "내 이름은 민수야. 기억해 줘."),
        ("ask", "내 이름이 뭐야?"),
        ("select", "답 방식", "계산기 도구"),
        ("ask", "1234 곱하기 5678은 얼마야?"),
        ("select", "답 방식", "정리 카드"),
        ("ask", "재택근무의 장단점을 정리해 줘."),
    ],
    3: [
        ("select", "답 방식", "약관 질문"),
        ("select", "검색 방식", "로컬 Chroma"),
        ("ask", POLICY_Q),
        ("ask", "삼성전자의 오늘 주가는 얼마야?"),
        ("select", "검색 방식", "사내 RAGaaS"),
        ("ask", POLICY_Q),
    ],
    4: [
        ("select", "답 방식", "에이전트"),
        ("ask", "안녕! 내 이름은 민수야."),
        ("ask", POLICY_Q),
        ("ask", "내 이름이 뭐야?"),
        ("toggle", "도구 실행 전 승인 받기", True),
        ("ask", "반려견 입원비도 보장되나요?"),
        ("click", "승인"),
        ("ask", "반려견 통원 치료비도 보장되나요?"),
        ("click", "거부"),
        ("click", "대화 지우기"),
        ("ask", "내 이름이 뭐야?"),
    ],
    5: [
        ("ask", "안녕! 내 이름은 민수야."),
        ("ask", POLICY_Q),
        ("ask", "내 이름이 뭐야?"),
        ("ask", "1234 곱하기 5678은 얼마야?"),
    ],
}
DEFAULT = [("ask", "파이썬이 뭐야? 한 문장으로 답해 줘."), ("ask", "방금 말한 것을 예시 하나로 설명해 줘."),
           ("click", "대화 지우기")]


def short(text, n=300):
    return str(text).replace("\n", " ")[:n]


def find(elements, label):
    return next((e for e in elements if e.label == label), None)


def report(at, seen):
    """이번 실행에서 새로 생긴 채팅 메시지와 실행 기록 상자, 화면의 버튼을 출력한다."""
    msgs = list(at.chat_message)
    for m in msgs[seen:]:
        print(f"   💬 {m.name}: {short(' '.join(md.value for md in m.markdown))}")
    for e in at.expander:
        body = " ".join(c.value for c in e.code) or " ".join(md.value for md in e.markdown)
        print(f"   📂 {e.label}: {short(body)}")
    buttons = [b.label for b in at.main.button]
    if buttons:
        print(f"   🔘 화면 버튼: {buttons}")
    print(f"   (채팅 메시지 모두 {len(msgs)}개)")
    return len(msgs)


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
    parser = argparse.ArgumentParser()
    parser.add_argument("app")
    parser.add_argument("--stage", type=int, choices=sorted(SCENARIOS))
    opts = parser.parse_args()

    # AppTest는 상대 경로를 이 스크립트 폴더 기준으로 찾으므로 절대 경로로 바꾼다
    at = AppTest.from_file(str(Path(opts.app).resolve()), default_timeout=TIMEOUT).run()
    if at.exception:
        print(f"✖ 앱을 여는 중 오류 | {at.exception[0].message} | 과제 파일을 고친다")
        return 1
    print(f"✔ 앱 열림: 사이드바 선택 상자 {[s.label for s in at.sidebar.selectbox]}, "
          f"토글 {[t.label for t in at.sidebar.toggle]}, 버튼 {[b.label for b in at.sidebar.button]}")

    seen, problems = 0, 0
    for action in SCENARIOS.get(opts.stage, DEFAULT):
        problem = step(at, action)
        if problem:
            print(f"\n✖ {action} 건너뜀 | {problem}")
            problems += 1
            continue
        if at.exception:
            print(f"✖ 실행 중 오류 | {at.exception[0].message} | 과제 파일을 고친다")
            return 1
        seen = report(at, seen) if action[0] != "click" or action[1] != "대화 지우기" else report(at, 0)
    print(f"\n✔ 끝: 건너뛴 동작 {problems}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
