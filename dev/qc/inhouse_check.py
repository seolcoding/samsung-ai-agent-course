"""사내망(강의장) 점검 — 3·4일차(M2)가 사내 환경에 기대는 것을 이 파일 하나로 실제로 불러 본다.

실행 (저장소 맨 위, .env의 COURSE_ENV=samsung):
    uv run --env-file .env python dev/qc/inhouse_check.py          전부(10분 안팎, LLM 요청 30회 안팎)
    uv run --env-file .env python dev/qc/inhouse_check.py 3 7      번호만 골라서 다시
study로 받은 PC(dev/ 없음)에서는 이 파일만 저장소 맨 위에 받아서 실행한다:
    curl.exe -o inhouse_check.py https://raw.githubusercontent.com/seolcoding/samsung-ai-agent-course/dev/dev/qc/inhouse_check.py
    uv run --env-file .env python inhouse_check.py

결과: 단계마다 🟢(됨) / ⛔(안 됨) / ❔(판단 못 함)와 한 줄 설명, 맨 끝에 표. 같은 표를 inhouse_check_result.txt에도 쓴다.
키·토큰 값은 출력하지 않는다. 서버(8000·8001)는 이 파일이 띄우고 끈다. 먼저 켜 둔 서버가 있으면 끄고 실행한다.
⛔인 실습은 수업에서 그 셀을 건너뛰고 사외 결과("무슨 일이 생기나")로 설명한다(dev/docs/2026-10-19_강의장_점검표.md).
"""

import truststore

truststore.inject_into_ssl()  # 사내망 HTTPS(Langfuse 등)는 회사 인증서를 거친다. 다른 import보다 먼저 둔다

import asyncio  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import socket  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from contextlib import contextmanager  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Literal  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in [HERE, *HERE.parents] if (p / "course" / "config").is_dir())  # dev/qc/ 또는 저장소 맨 위
COURSE = ROOT / "course"
NB = COURSE / "Chapter02" / "notebooks"
CAPSTONE = COURSE / "Chapter02" / "capstone"
LOGS = Path(tempfile.gettempdir()) / "inhouse_check"  # 서버 로그
CHILD_ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}  # 윈도우(cp949)에서도 서버·캡스톤 출력이 깨지지 않게

sys.path.insert(0, str(COURSE))
os.chdir(ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")
import config  # noqa: E402,F401  .env의 COURSE_ENV(사내/사외)에 맞춰 연결 방식을 채운다
from config.check import _mask, report  # noqa: E402
from config.llm import get_llm  # noqa: E402


# ── 도움 함수 ──────────────────────────────────────────────────────────────────

def port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


@contextmanager
def server(path: Path, port: int):
    """서버 파일을 터미널에서 띄우듯 따로 실행하고, 끝나면 끈다."""
    if port_open(port):
        raise RuntimeError(f"포트 {port}를 이미 쓰는 프로그램이 있음 → 앞 서버 터미널에서 Ctrl+C로 끄고 다시 실행")
    LOGS.mkdir(exist_ok=True)
    log = LOGS / f"server_{port}.log"
    with open(log, "w", encoding="utf-8") as f:
        p = subprocess.Popen([sys.executable, str(path)], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, env=CHILD_ENV)
        try:
            for _ in range(60):
                if port_open(port):
                    break
                if p.poll() is not None:
                    raise RuntimeError(f"서버가 켜지자마자 끝남(로그 {log})")
                time.sleep(1)
            else:
                raise RuntimeError(f"60초 안에 서버가 켜지지 않음(로그 {log})")
            yield
        finally:
            p.terminate()
            try:
                p.wait(10)
            except subprocess.TimeoutExpired:
                p.kill()


def text_of(content) -> str:
    """메시지·도구 결과의 content(글 또는 조각 목록)를 글로."""
    if isinstance(content, str):
        return content
    return " ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)


# ── 점검 (번호, 이름, 영향받는 실습, 함수). 함수는 (상태, 설명)을 돌려준다 ─────────────────

def check_settings():
    items = report(["LLM_PROVIDER", "EMBED_PROVIDER", "RAG_PROVIDER", "LANGFUSE", "MCP_KEYS"])
    bad = [f"{i['name']}" for i in items if i["status"] == "⛔"]
    env = os.getenv("COURSE_ENV", "").strip().lower()
    if bad:
        return "⛔", "빠진 설정: " + ", ".join(bad) + " → uv run python -m config.check"
    if env != "samsung":
        return "❔", f"COURSE_ENV={env or '(없음)'} — 사내 점검이 아님(.env를 samsung으로)"
    return "🟢", "COURSE_ENV=samsung, LLM·임베딩·RAGaaS·Langfuse 이름 모두 있음"


def check_llm():
    answer = get_llm().invoke("한 단어로만 답하세요: 안녕").content
    return "🟢", f"응답 받음({len(text_of(answer))}자)"


def check_tool_calling():
    from langchain_core.messages import HumanMessage, ToolMessage
    from langchain_core.tools import tool

    @tool
    def multiply(a: int, b: int) -> int:
        """두 정수를 곱한다."""
        return a * b

    llm = get_llm().bind_tools([multiply])
    question = HumanMessage(content="도구를 써서 37 곱하기 43을 계산해 줘.")
    first = llm.invoke([question])
    calls = getattr(first, "tool_calls", []) or []
    if not calls:
        return "⛔", f"도구를 부르지 않고 바로 답함: {text_of(first.content)[:60]!r}"
    result = multiply.invoke(calls[0]["args"])
    final = llm.invoke([question, first, ToolMessage(content=str(result), tool_call_id=calls[0]["id"])])
    ok = "1591" in text_of(final.content).replace(",", "")
    return ("🟢" if ok else "❔"), f"{calls[0]['name']}({calls[0]['args']}) 호출 → 최종 답에 1591 {'있음' if ok else '없음'}"


def check_structured_output():
    from pydantic import BaseModel

    class RouteDecision(BaseModel):  # 캡스톤 Supervisor와 같은 모양
        next: Literal["researcher", "writer", "END"]
        reason: str

    r = get_llm().with_structured_output(RouteDecision).invoke(
        "리서치도 보고서 초안도 아직 없습니다. 다음 차례(researcher, writer, END)를 고르고 이유를 한 문장으로.")
    if not isinstance(r, RouteDecision):
        return "⛔", f"객체가 아닌 {type(r).__name__}로 받음"
    return "🟢", f"RouteDecision(next={r.next!r}) 객체로 받음"


def check_embeddings():
    import math

    from config.embeddings import get_embeddings

    ko, en, ja, other = get_embeddings().embed_documents([
        "고양이가 소파 위에서 잔다", "The cat is sleeping on the sofa", "猫がソファの上で寝ている", "오늘 주식 시장이 크게 떨어졌다"])

    def cos(a, b):
        return sum(x * y for x, y in zip(a, b)) / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

    s_en, s_ja, s_other = cos(ko, en), cos(ko, ja), cos(ko, other)
    ok = min(s_en, s_ja) > s_other
    return ("🟢" if ok else "⛔"), f"{len(ko)}차원, 한-영 {s_en:.2f} · 한-일 {s_ja:.2f} · 다른 뜻 {s_other:.2f}" + ("" if ok else " (다국어로 안 보임)")


def check_ragaas():
    from config.ragaas import post_ragaas

    provider = os.getenv("RAG_PROVIDER", "samsung").strip().lower()
    index_name = os.getenv("index_name") or "mock-check"
    payload = {"index_name": index_name, "permission_groups": ["rag-public"], "query_text": "반려동물 수술비 보장",
               "num_result_doc": 3, "fields_exclude": ["v_merge_title_content"]}
    hits = post_ragaas("retrieve-rrf", payload).json()["hits"]["hits"]
    if provider == "mock":
        return "❔", "RAG_PROVIDER=mock(사외 모의 응답) — 사내 점검이 아님"
    if not hits:
        return "⛔", f"인덱스 {index_name}에서 결과 0개"
    first = hits[0]["_source"]["merge_title_content"].replace("\n", " ")
    return "🟢", f"결과 {len(hits)}개, 첫 글: {first[:40]}…"


def check_mcp_apis():
    from config.check import _live_mcp

    if not (os.getenv("DART_API_KEY", "").strip() and os.getenv("TAVILY_API_KEY", "").strip()):
        return "❔", "TAVILY_API_KEY·DART_API_KEY가 .env에 없음 → 강사 키를 넣고 다시(DART는 강사 키, Tavily는 수강생 각자)"
    items = _live_mcp()
    bad = [i for i in items if i["status"] != "🟢"]
    detail = " · ".join(f"{i['name']} {i['status']} {i['detail']}" for i in items)
    return ("⛔" if bad else "🟢"), detail + (" → 막힌 쪽은 수업에서 [모의 DART]·Tavily 없이 진행" if bad else "")


def check_mcp():
    from langchain_mcp_adapters.client import MultiServerMCPClient

    async def run():  # 3-2 LAB과 같은 연결: 터미널에 띄운 DART 서버(SSE) + 키가 있으면 Tavily 공식 원격 MCP
        client = MultiServerMCPClient({"dart": {"transport": "sse", "url": "http://localhost:8002/sse"}})
        tools = await client.get_tools()
        names = {t.name for t in tools}
        want = {"get_company_info", "get_recent_disclosures", "get_financial_summary"}
        if not want <= names:
            return "⛔", f"DART 서버 도구가 다름: {sorted(names)}"
        msg = await get_llm().bind_tools(tools).ainvoke("삼성전자 대표이사가 누구야? 도구로 확인해 줘.")
        calls = getattr(msg, "tool_calls", []) or []
        if not calls:
            return "⛔", f"DART 도구 {len(names)}개는 받았지만 LLM이 도구를 부르지 않음"
        out = text_of(await {t.name: t for t in tools}[calls[0]["name"]].ainvoke(calls[0]["args"]))
        tavily = "Tavily 키 없음"
        if os.getenv("TAVILY_API_KEY", "").strip():
            try:
                conn = {"transport": "streamable_http", "url": "https://mcp.tavily.com/mcp/",  # 3-2 LAB과 같은 연결(키는 머리말)
                        "headers": {"Authorization": f"Bearer {os.environ['TAVILY_API_KEY'].strip()}"}}
                t_tools = await asyncio.wait_for(MultiServerMCPClient({"tavily": conn}).get_tools(), 20)
                tavily = f"Tavily MCP 도구 {len(t_tools)}개 🟢"
            except Exception as e:  # noqa: BLE001
                tavily = f"Tavily MCP ⛔ {type(e).__name__}"
        mock = out.startswith("[모의 DART]")
        status = "❔" if mock or "⛔" in tavily else "🟢"
        return status, f"{calls[0]['name']} 호출 → {out[:30]!r}{' (모의 응답)' if mock else ''} · {tavily}"

    with server(NB / "dart_mcp_server.py", 8002):
        return asyncio.run(run())


def check_a2a():
    import uuid

    import a2a.types as t
    import httpx
    from a2a.client.base_client import BaseClient
    from a2a.client.card_resolver import A2ACardResolver
    from a2a.client.client import ClientConfig
    from a2a.client.transports.jsonrpc import JsonRpcTransport
    from a2a.utils.constants import PROTOCOL_VERSION_1_0, VERSION_HEADER

    base = "http://127.0.0.1:8001"

    async def run():  # 3-3 LAB처럼 친구 셋의 Agent Card를 받고, 메시에게 한 번 물어본다
        async with httpx.AsyncClient(headers={VERSION_HEADER: PROTOCOL_VERSION_1_0}, timeout=60.0) as http:
            cards = {f: await A2ACardResolver(http, f"{base}/{f}").get_agent_card() for f in ("messi", "ronaldo", "mbappe")}
            card = cards["messi"]
            client = BaseClient(card, ClientConfig(), JsonRpcTransport(http, card, f"{base}/messi/"), [])
            req = t.SendMessageRequest(message=t.Message(
                role=t.Role.ROLE_USER, parts=[t.Part(text="목요일 저녁에 축구할 시간 있어?")], message_id=str(uuid.uuid4())))
            async for response in client.send_message(req):
                if response.HasField("message"):
                    return cards, "".join(p.text for p in response.message.parts if p.text)
        return cards, ""

    with server(NB / "a2a_server.py", 8001):
        start = time.time()
        cards, answer = asyncio.run(run())
        sec = time.time() - start
    names = ", ".join(c.name for c in cards.values())
    if not answer:
        return "⛔", f"Agent Card 3개({names})는 받았지만 메시의 답이 비어 있음"
    return ("🟢" if sec < 60 else "❔"), f"카드 3개({names}), 메시 답 {len(answer)}자 {sec:.0f}초: {answer[:30]!r}"


def check_memory_format():
    from langchain_core.messages import HumanMessage, SystemMessage

    system = ("너는 친절한 AI 어시스턴트야.\n\n사용자에 대해 알고 있는 정보:\n없음\n\n"
              "대화 중 사용자의 중요한 정보(이름, 취미, 직업 등)가 나오면,\n\"[기억 저장: <내용>]\" 형식으로 메시지 앞에 표시해줘.")
    content = text_of(get_llm().invoke([SystemMessage(content=system),
                                        HumanMessage(content="안녕! 내 이름은 홍길동이고 취미는 등산이야.")]).content)
    ok = "[기억 저장:" in content
    return ("🟢" if ok else "⛔"), ("`[기억 저장: …]` 형식을 지킴" if ok else f"형식을 안 지킴(Store에 저장 안 됨): {content[:50]!r}")


def check_sqlite():
    import sqlite3
    from typing import Annotated

    from langchain_core.messages import AIMessage, HumanMessage
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langgraph.graph import START, StateGraph
    from langgraph.graph.message import add_messages
    from typing_extensions import TypedDict

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    builder = StateGraph(State)
    builder.add_node("echo", lambda s: {"messages": [AIMessage(content="ok")]})  # LLM 없이 저장만 본다
    builder.add_edge(START, "echo")
    db = NB / "_inhouse_check.db"  # 3-4 LAB의 checkpoints.db와 같은 폴더
    conn = sqlite3.connect(db, check_same_thread=False)
    try:
        app = builder.compile(checkpointer=SqliteSaver(conn))
        cfg = {"configurable": {"thread_id": "inhouse-check"}}
        app.invoke({"messages": [HumanMessage(content="hi")]}, config=cfg)
        n = len(list(app.get_state_history(cfg)))
    finally:
        conn.close()
        db.unlink(missing_ok=True)
    return ("🟢" if n else "⛔"), f"노트북 폴더에 sqlite 체크포인트 {n}개 저장·읽기"


def check_deep_agent():
    from deepagents import create_deep_agent
    from deepagents.backends import FilesystemBackend
    from langchain_core.messages import HumanMessage
    from langgraph.checkpoint.memory import MemorySaver

    agent = create_deep_agent(  # 4-1과 같은 짜임. 스킬은 캡스톤 Writer의 SDS 보고서 스킬을 쓴다
        model=get_llm(), tools=[], backend=FilesystemBackend(root_dir=str(CAPSTONE), virtual_mode=True),
        skills=["skills/writer/"], system_prompt="보고서는 스킬 양식을 그대로 따른다.", checkpointer=MemorySaver())
    result = agent.invoke({"messages": [HumanMessage(content="'사내 AI 교육 효과'를 주제로 아주 짧은 보고서를 써 줘.")]},
                          config={"configurable": {"thread_id": "inhouse-check"}, "recursion_limit": 40})
    msgs = result["messages"]
    read = any("SKILL.md" in json.dumps(c.get("args", {}), ensure_ascii=False)
               for m in msgs for c in (getattr(m, "tool_calls", None) or []))
    sds = "[SDS-AI-RPT" in text_of(msgs[-1].content)
    status = "🟢" if read and sds else "⛔" if not read else "❔"
    return status, f"스킬 파일 읽음 {'🟢' if read else '⛔'} · SDS 양식 {'🟢' if sds else '⛔'} (도구 호출 {sum(len(getattr(m, 'tool_calls', None) or []) for m in msgs)}번)"


def check_langfuse():
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langfuse import get_client
    from langfuse.langchain import CallbackHandler

    langfuse = get_client()
    if not langfuse.auth_check():
        return "⛔", "Langfuse 인증 실패 → .env의 LANGFUSE_ 값 세 개"
    handler = CallbackHandler()
    chain = ChatPromptTemplate.from_messages([("human", "{q}")]) | get_llm() | StrOutputParser()
    chain.invoke({"q": "RAG를 한 문장으로 설명해줘"}, config={"callbacks": [handler]})
    tid = handler.last_trace_id
    if not tid:
        return "⛔", "trace_id가 없음(CallbackHandler가 기록하지 못함)"
    langfuse.create_score(trace_id=tid, name="inhouse-check", value=1.0)
    langfuse.flush()
    names, scores = [], []
    for _ in range(12):  # 기록은 늦게 도착한다(최대 60초, 4-2 과제 확인 코드와 같은 조회 API)
        try:
            names = [o.name for o in langfuse.api.observations.get_many(trace_id=tid, limit=50).data]
            scores = [s.name for s in langfuse.api.scores_v3.get_many_v3(trace_id=tid).data]
        except Exception as e:  # noqa: BLE001 — 조회 API가 막혀도 기록 자체는 됐을 수 있다
            return "❔", f"인증·전송은 됨, 조회 API 실패({type(e).__name__}) → 대시보드에서 trace {tid} 직접 확인"
        if names and "inhouse-check" in scores:
            return "🟢", f"trace·점수가 Langfuse에 도착(trace {tid[:8]}…)"
        time.sleep(5)
    return "❔", f"60초 안에 조회되지 않음 → 대시보드에서 trace {tid} 직접 확인"


def check_capstone():
    head = "%%writefile ../capstone/solution.py"  # 4-3 LAB 8.2 셀. 정답 공개 전에는 강사본에만 있다(study 클론에는 없음)
    cells = [c for f in (NB / "4-3_capstone_LAB.ipynb", ROOT / "dev/instructor/Chapter02/4-3_capstone_LAB.ipynb") if f.exists()
             for c in json.loads(f.read_text(encoding="utf-8"))["cells"]]
    cell = next(("".join(c["source"]) for c in cells if c["cell_type"] == "code" and "".join(c["source"]).startswith(head)), None)
    if cell is None:
        return "❔", "정답 코드가 없는 클론(study) — 캡스톤 정답은 dev 클론에서 점검한다"
    sol = CAPSTONE / "_inhouse_check_solution.py"  # 4-3 LAB 8.2 셀의 정답 코드. solution.py는 건드리지 않는다
    sol.write_text(cell[len(head):].lstrip("\n"), encoding="utf-8")
    try:
        with server(CAPSTONE / "mcp_server.py", 8001):
            start = time.time()
            run = subprocess.run([sys.executable, str(sol)], cwd=ROOT, input="y\n", capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=420, env=CHILD_ENV)
            sec = time.time() - start
    finally:
        sol.unlink(missing_ok=True)
    out = run.stdout + run.stderr
    seen = {"MCP 도구": "MCP 도구 로드" in out, "SDS 보고서": "[SDS-AI-RPT" in out, "종합 점수": "종합 점수" in out}
    detail = " · ".join(f"{k} {'🟢' if v else '⛔'}" for k, v in seen.items()) + f" ({sec:.0f}초)"
    if all(seen.values()):
        return "🟢", detail
    last = next((ln for ln in reversed(out.strip().splitlines()) if ln.strip()), "")
    return "⛔", f"{detail}, 마지막 줄: {_mask(last)[:80]}"


CHECKS = [
    (1, "설정 이름(.env)", "전체", check_settings),
    (2, "LLM 호출", "전체", check_llm),
    (3, "도구 호출(bind_tools)", "3-1·3-2·3-3·4-1·캡스톤", check_tool_calling),
    (4, "구조화 출력", "캡스톤 Supervisor·Judge", check_structured_output),
    (5, "사내 임베딩(다국어)", "3-1 5장 RAG", check_embeddings),
    (6, "RAGaaS 검색", "캡스톤 rag_search", check_ragaas),
    (7, "Tavily·DART 사내망 연결", "3-2", check_mcp_apis),
    (8, "DART MCP 서버(8002)+Tavily MCP", "3-2 실전", check_mcp),
    (9, "A2A 친구 에이전트(8001) 요청", "3-3", check_a2a),
    (10, "[기억 저장: …] 형식", "3-4 Store", check_memory_format),
    (11, "SQLite 체크포인트", "3-4 SqliteSaver", check_sqlite),
    (12, "Deep Agent 스킬", "4-1·캡스톤", check_deep_agent),
    (13, "Langfuse trace·점수", "4-2·캡스톤", check_langfuse),
    (14, "캡스톤 정답 전체(y)", "4-3", check_capstone),
]


def main():
    want = {int(a) for a in sys.argv[1:] if a.isdigit()}
    todo = [c for c in CHECKS if not want or c[0] in want]
    rows = []
    for k, (n, name, labs, fn) in enumerate(todo, 1):
        print(f"✔ [{k}/{len(todo)}] {n}. {name} ({labs}) …", flush=True)
        start = time.time()
        try:
            status, detail = fn()
        except Exception as e:  # noqa: BLE001 — 어떤 오류든 이 단계의 결과로 적고 다음 단계로 간다
            status, detail = "⛔", f"{type(e).__name__}: {_mask(e)[:150]}"
        rows.append((n, name, labs, status, detail))
        print(f"   {status} {detail} [{time.time() - start:.0f}초]\n", flush=True)

    lines = [f"사내망 점검 결과 {time.strftime('%Y-%m-%d %H:%M')} (COURSE_ENV={os.getenv('COURSE_ENV', '')})", "",
             "| 번호 | 점검 | 실습 | 결과 | 설명 |", "|---|---|---|---|---|"]
    lines += [f"| {n} | {name} | {labs} | {status} | {detail} |" for n, name, labs, status, detail in rows]
    bad = [str(r[0]) for r in rows if r[3] == "⛔"]
    lines += ["", f"⛔ {len(bad)}개" + (f": {', '.join(bad)}번 → 그 번호만 다시: uv run --env-file .env python {Path(sys.argv[0]).as_posix()} {' '.join(bad)}" if bad else " — 모두 통과")]
    print("\n".join(lines))
    Path("inhouse_check_result.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n✔ 결과를 inhouse_check_result.txt에도 썼습니다")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
