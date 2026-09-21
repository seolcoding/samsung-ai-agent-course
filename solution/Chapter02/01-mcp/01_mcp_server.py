"""
MCP 서버 만들기 (FastMCP)

커스텀 MCP 서버를 직접 만들어 실행한다.
02_mcp_client.py가 이 서버에 연결해 도구를 사용한다.

실행:
  python 01_mcp_server.py            # HTTP/SSE 모드 (기본, 포트 8000)
  python 01_mcp_server.py --stdio    # stdio 모드 (Claude Code 등 MCP Host 연결용)

Claude Code에 등록하는 방법 (stdio):
  claude mcp add tutorial-server -- python /절대경로/01_mcp_server.py --stdio
"""

import sys
from datetime import datetime

from fastmcp import FastMCP

# FastMCP: Anthropic MCP SDK 위에서 동작하는 고수준 래퍼.
# @mcp.tool(), @mcp.resource(), @mcp.prompt() 데코레이터로 기능을 정의한다.
    # 데코레이터 형식으로 사용
    # 어떠한 기능을 가진 함수 -> 현재시간, bmi 계산해주는 어떤 기능
        # file system -> READ, Write, Delete -> MCP서버가 MCP 호스트에 등록되어 있어서!
# 지금 만든 'AI 강의 튜토리얼 서버' 라는 하나의 서버는 -> 다양한 도구들을 보유 할 수 있을 것이다.
    # 예를 들어, slack 이라는 메신저 MCP 서버를 부착한다
        # DM을 보내기, 읽기, 파일 읽기, 스레드 읽기, 내가 보낸 메시지 삭제하기
            # 메시지를 오늘부터 최근 한달 사이의 특정 유저와 보낸 DM 전체 조회 후, 요약
            # 메시지 읽기 기능 -> 날짜별로 조회
                # 그렇게 조회해 온 메시지들을 모아서 리스트 형식으로 LLM에게 전달하면 요약해 줌
mcp = FastMCP('AI 강의 튜토리얼 서버')


# ── Tool: LLM이 호출할 수 있는 함수 ──────────────────────────────────────────
# 이렇게 mcp.tool로 도구화 -> 기존의 langchain에서 함수를 도구화 하는 방법과 동일한 방법

@mcp.tool()
def get_current_time() -> str:
    """현재 날짜와 시간을 반환한다."""
    # 도구에 대한 설명을 작성해 두면 -> 나중에 MCP Client의 LLM이 
    # 도구 호출시 호출할 근거 판단용으로 사용된다.
    return datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')


# 도구화 될 함수의 인자의 타입힌트는 -> Agent가 도구를 호출할 떄, 삽입할 인자의 값을 결정
@mcp.tool()
def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """체중(kg)과 키(cm)로 BMI를 계산한다."""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        category = '저체중'
    elif bmi < 23:
        category = '정상'
    elif bmi < 25:
        category = '과체중'
    else:
        category = '비만'
    return {'bmi': round(bmi, 1), 'category': category}


_tasks: list[dict] = []


@mcp.tool()
def add_task(title: str, priority: int = 1) -> str:
    """할 일 목록에 새 항목을 추가한다. priority는 1(낮음)~3(높음)."""
    task = {'id': len(_tasks) + 1, 'title': title, 'priority': priority, 'done': False}
    _tasks.append(task)
    return f'할 일 추가됨: [{task["id"]}] {title} (우선순위: {priority})'


@mcp.tool()
def list_tasks() -> list[dict]:
    """현재 할 일 목록을 반환한다."""
    return _tasks if _tasks else [{'message': '할 일이 없습니다.'}]


@mcp.tool()
def complete_task(task_id: int) -> str:
    """할 일을 완료 처리한다."""
    for task in _tasks:
        if task['id'] == task_id:
            task['done'] = True
            return f'완료: {task["title"]}'
    return f'ID {task_id}를 찾을 수 없습니다.'


# ── Resource: LLM에게 제공할 데이터/문서 ──────────────────────────────────────

@mcp.resource('config://app-info')
def get_app_info() -> str:
    """이 MCP 서버의 기본 정보를 제공한다."""
    return """
    서버명: AI 강의 튜토리얼 MCP 서버
    버전: 1.0.0
    기능: 시간 조회, BMI 계산, 할 일 관리
    """


# ── Prompt: 자주 쓰는 프롬프트 템플릿 ────────────────────────────────────────

@mcp.prompt()
def task_summary_prompt(user_name: str) -> str:
    """할 일 목록 요약 요청 프롬프트를 생성한다."""
    return f'{user_name}님의 할 일 목록을 우선순위별로 정리하고 오늘 집중해야 할 항목을 추천해줘.'

# ── 실행 ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if '--stdio' in sys.argv:
        # stdio 모드: Claude Code, Cursor 등 MCP Host와 직접 연결
        # 예시를 파이썬 파일로 작성하고 있으므로, MCP Host에 Server를 연결 할 떄 작성하는 설정이
            # command: 'python' 을 직접 실행하는 형식으로 가이드를 줄건데
            # 다른 MCP Server 들은? python으로 안만들어 졌곘죠?
            # Python 외의 다른 언어로도 얼마든지 MCP Server를 구축할 수 있을 것이다.
                # 하물며, 배포 해 둘 수도 있을 것이다.
        # 즉, 코드를 직접 실행시켜서 서버를 연동하는 방식이라면 -> 서버 실행에 필요한 인자 등의 디테일한 설정도 가능
        mcp.run(transport='stdio')
    else:
        # HTTP/SSE 모드: 02_mcp_client.py에서 localhost:8000으로 연결
        print('MCP 서버 시작: http://localhost:8000/sse')
        print('종료하려면 Ctrl+C')
        mcp.run(transport='sse', host='0.0.0.0', port=8000)
