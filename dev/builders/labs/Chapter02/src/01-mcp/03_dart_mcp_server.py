"""
DART 공시 MCP 서버 만들기 (FastMCP)

금융감독원 전자공시(OpenDART) API를 MCP 도구로 감싼다. 터미널에서 실행한다.
기본은 HTTP/SSE 모드(포트 8002. 기본 실습 서버가 8000을 쓴다), --stdio를 붙이면 stdio 모드로 실행한다.
.env에 DART_API_KEY가 없거나 DART에 연결되지 않으면 [모의 DART]로 시작하는 연습용 답을 돌려준다.
"""

import os
import sys
from datetime import date, timedelta

import requests
import truststore
from dotenv import load_dotenv
from fastmcp import FastMCP

truststore.inject_into_ssl()  # 사내망 HTTPS는 회사 인증서를 거친다. PC에 등록된 인증서를 믿게 한다
load_dotenv()

# FastMCP: Anthropic MCP SDK 위에서 동작하는 고수준 래퍼.
# @mcp.tool(), @mcp.resource(), @mcp.prompt() 데코레이터로 기능을 정의한다.
mcp = FastMCP("DART 공시 서버")


# ── DART API 호출하기 ──────────────────────────────────────────────────────────
DART_URL = "https://opendart.fss.or.kr/api"
# DART는 회사를 8자리 고유번호(corp_code)로 찾는다. 실습에서 쓸 회사만 사전으로 둔다
COMPANIES = {
    "삼성전자": "00126380",
    "SK하이닉스": "00164779",
    "LG전자": "00401731",
    "현대자동차": "00164742",
    "NAVER": "00266961",
    "카카오": "00258801",
}
MOCK = "[모의 DART] DART_API_KEY가 없거나 DART에 연결하지 못해 연습용 예시를 보여 줍니다. 실제 공시가 아닙니다."


def call_dart(endpoint: str, **params) -> dict | None:
    """DART API를 호출한다. 키가 없거나 DART에 연결하지 못하면 None을 돌려준다(그때 도구는 [모의 DART] 답을 낸다)."""
    key = os.getenv("DART_API_KEY", "").strip()
    if not key:
        return None
    try:
        return requests.get(f"{DART_URL}/{endpoint}", params={"crtfc_key": key, **params}, timeout=10).json()
    except (requests.RequestException, ValueError):
        return None


def find_code(company: str) -> str | None:
    return COMPANIES.get(company.replace(" ", "").replace("(주)", ""))


def unknown(company: str) -> str:
    return f"'{company}'은(는) 이 서버의 회사 사전에 없습니다. 찾을 수 있는 회사: {', '.join(COMPANIES)}"


# ── Tool: LLM이 호출할 수 있는 함수 ──────────────────────────────────────────
@mcp.tool()
def get_company_info(company: str) -> str:
    """회사의 기본 정보(정식 이름, 대표이사, 종목코드, 설립일, 홈페이지)를 DART에서 찾는다."""
    code = find_code(company)
    if code is None:
        return unknown(company)
    data = call_dart("company.json", corp_code=code)
    if data is None:
        return f"{MOCK}\n회사명: {company}(예시) / 대표이사: 홍길동 / 종목코드: 000000 / 설립일: 19690101"
    if data.get("status") != "000":
        return f"DART 응답: {data.get('message')}"
    return (f"회사명: {data['corp_name']} / 대표이사: {data['ceo_nm']} / 종목코드: {data['stock_code']} / "
            f"설립일: {data['est_dt']} / 홈페이지: {data['hm_url']}")


@mcp.tool()
def get_recent_disclosures(company: str, days: int = 30) -> str:
    """회사가 최근 며칠 동안 DART에 낸 공시 목록(날짜, 공시 제목, 제출인)을 찾는다. 기본은 30일."""
    code = find_code(company)
    if code is None:
        return unknown(company)
    end = date.today()
    begin = end - timedelta(days=days)
    data = call_dart("list.json", corp_code=code, bgn_de=begin.strftime("%Y%m%d"),
                     end_de=end.strftime("%Y%m%d"), page_count=10)
    if data is None:
        return f"{MOCK}\n{end} 주요사항보고서(예시) / {begin} 분기보고서(예시)"
    if data.get("status") != "000":
        return f"DART 응답: {data.get('message')}"
    day = lambda d: f"{d[:4]}-{d[4:6]}-{d[6:]}"  # 20261019 → 2026-10-19
    rows = [f"{day(x['rcept_dt'])} {x['report_nm'].strip()} (제출: {x['flr_nm']})" for x in data["list"]]
    return f"{data['list'][0]['corp_name']} 최근 {days}일 공시 {data['total_count']}건 중 최근 {len(rows)}건:\n" + "\n".join(rows)


@mcp.tool()
def get_financial_summary(company: str, year: int) -> str:
    """회사의 한 해 실적(연결 기준 매출액, 영업이익, 당기순이익)을 그해 사업보고서에서 찾는다."""
    code = find_code(company)
    if code is None:
        return unknown(company)
    data = call_dart("fnlttSinglAcnt.json", corp_code=code, bsns_year=str(year), reprt_code="11011")
    if data is None:
        return f"{MOCK}\n{year}년 매출액 100.0조 원 / 영업이익 10.0조 원 / 당기순이익 8.0조 원(예시)"
    if data.get("status") != "000":
        return f"DART 응답: {data.get('message')} ({year}년 사업보고서)"
    lines = []
    for x in data["list"]:
        if x["fs_div"] == "CFS" and x["account_nm"] in ("매출액", "영업이익", "당기순이익(손실)", "당기순이익"):
            now, before = (int(v.replace(",", "")) / 1e12 for v in (x["thstrm_amount"], x["frmtrm_amount"]))
            lines.append(f"{x['account_nm']}: {now:.1f}조 원 (전년 {before:.1f}조 원)")
    return f"{company} {year}년 연결 실적\n" + "\n".join(dict.fromkeys(lines))  # 같은 줄이 두 번 오는 회사가 있다


# ── Resource: LLM에게 제공할 데이터/문서 ──────────────────────────────────────
@mcp.resource("dart://companies")
def list_companies() -> str:
    """이 서버가 찾을 수 있는 회사와 DART 고유번호 목록."""
    return "\n".join(f"{name}: {code}" for name, code in COMPANIES.items())


# ── Prompt: 자주 쓰는 프롬프트 템플릿 ────────────────────────────────────────
@mcp.prompt()
def company_briefing(company: str) -> str:
    """회사 한 곳의 공시 브리핑을 요청하는 프롬프트를 만든다."""
    return f"{company}의 기본 정보, 최근 30일 공시, 지난해 실적을 DART 도구로 확인하고 꼭 알아야 할 점을 세 줄로 정리해줘."


# ── 실행 ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if "--stdio" in sys.argv:
        # stdio 모드: 클라이언트가 이 파일을 직접 실행해 표준 입출력으로 주고받는다(print를 쓰면 통신이 깨진다)
        mcp.run(transport="stdio")
    else:
        print("DART MCP 서버 시작: http://localhost:8002/sse")
        print("DART_API_KEY:", "있음 — 실제 DART를 호출합니다" if os.getenv("DART_API_KEY", "").strip()
              else "없음 — [모의 DART] 연습용 답을 돌려줍니다")
        print("종료하려면 Ctrl+C")
        # HTTP/SSE 모드: 클라이언트가 localhost:8002로 연결
        # 127.0.0.1: 이 PC에서 오는 요청만 받는다. 0.0.0.0이면 다른 PC의 요청도 받는다.
        mcp.run(transport="sse", host="127.0.0.1", port=8002)
