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
# TODO: @mcp.tool(), @mcp.resource(), @mcp.prompt() 데코레이터로 기능을 정의한다.
mcp = FastMCP('AI 강의 튜토리얼 서버')


# ── Tool: LLM이 호출할 수 있는 함수 ──────────────────────────────────────────
@mcp.tool()
def get_current_time() -> str:
    """현재 날짜와 시간을 반환한다."""
    return datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')

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

# TODO: MCP 서버 모드 정의
if __name__ == '__main__':
    if '--stdio' in sys.argv:
        # stdio 모드: Claude Code, Cursor 등 MCP Host와 직접 연결
        mcp.run(transport='stdio')
    else:
        print('MCP 서버 시작: http://localhost:8000/sse')
        print('종료하려면 Ctrl+C')
        # HTTP/SSE 모드: 02_mcp_client.py에서 localhost:8000으로 연결
        mcp.run(transport='sse', host='0.0.0.0', port=8000)        
