"""노트북에서 MCP 서버를 stdio 방식으로 띄울 때 쓰는 도움 함수(3-2 실습)."""

from pathlib import Path


def stdio_errors_to_file(path="mcp_stdio_server.log"):
    """stdio로 띄운 서버의 오류 출력(stderr)을 노트북 화면 대신 파일로 받게 한다. 받는 파일의 경로를 돌려준다.

    MCP SDK는 서버의 stderr를 sys.stderr에 잇는다. Windows 노트북의 sys.stderr는 진짜 파일이 아니라(fileno가 없음)
    서버 프로그램을 띄우지 못하고 `io.UnsupportedOperation: fileno`로 멈춘다. 진짜 파일을 주면 Windows에서도 뜬다.
    macOS·Linux에서도 해가 없다(서버 로그가 화면 대신 파일로 간다).
    """
    import mcp.client.stdio

    log = open(path, "a", encoding="utf-8")  # 커널이 끝날 때까지 열어 둔다
    mcp.client.stdio.stdio_client.__wrapped__.__defaults__ = (log,)  # stdio_client(server, errlog=sys.stderr)의 기본값
    return Path(path).resolve()
