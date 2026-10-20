"""Chapter02 4-3 캡스톤 안내 노트북을 조립한다. 코드 빈칸은 없다.
수강생은 course/Chapter02/capstone/ 폴더의 starter.py를 AI와 함께 채우고 터미널에서 실행한다.
이 노트북은 주제 고르기, 구조도, 단계별 체크리스트(프롬프트 힌트·🟢/⛔·정답 보기), 실행 명령, 정답 비교 방법을 담는다.

실행(프로젝트 루트): uv run python dev/builders/build_capstone_guide.py
입력: course/Chapter02/code/solution/06-capstone/solution.py (정답 보기·정답 코드 셀의 원천. 읽기만 한다)
출력: course/Chapter02/notebooks/4-3_capstone_LAB.ipynb (출력 없음) + 강사본 dev/instructor/Chapter02/

정답 코드는 원본 solution.py에서 두 곳만 바꿔 보여 준다(capstone/ 폴더 구성에 맞춤).
  1. 맨 위 설명의 실행 명령 → capstone/ 폴더 명령
  2. Writer skill 경로 'skills/sds-report-writer/' → 'skills/writer/'
     (deepagents는 skills=[...]를 "skill 폴더들이 든 상위 폴더"로 읽는다. 원본 경로는 SKILL.md가 바로 든 폴더라
      skill을 하나도 찾지 못한다. capstone/은 skills/researcher/research/SKILL.md, skills/writer/sds-report-writer/SKILL.md 구조)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbkit import Notebook  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
COURSE = ROOT / "course"
SOLUTION = COURSE / "Chapter02" / "code" / "solution" / "06-capstone" / "solution.py"
OUT = COURSE / "Chapter02" / "notebooks" / "4-3_capstone_LAB.ipynb"

RUN_SERVER = "uv run python course/Chapter02/capstone/mcp_server.py"
RUN_STARTER = "uv run python course/Chapter02/capstone/starter.py"
RUN_SOLUTION = "uv run python course/Chapter02/capstone/solution.py"
# 사내망에서 Langfuse(HTTPS)는 회사 인증서를 거친다. starter.py와 같은 두 줄을 맨 위 import보다 먼저 둔다
TRUSTSTORE = ("import truststore\n\n"
              "truststore.inject_into_ssl()  # PC에 등록된 인증서(회사 인증서 포함)를 믿게 합니다. Langfuse보다 먼저 둡니다(지우지 않습니다)\n\n")


def solution_source():
    """원본 정답을 capstone/ 폴더 구성에 맞게 세 곳만 바꾼다. 바꿀 곳을 못 찾으면 멈춘다(조용히 틀리지 않게)."""
    src = SOLUTION.read_text(encoding="utf-8")
    head_old = src[src.index("사전 준비:"): src.index('"""', 10)]
    head_new = (f"실행 (저장소 맨 위에서, 터미널 두 개):\n"
                f"  터미널 A: {RUN_SERVER}   ← MCP 서버 먼저\n"
                f"  터미널 B: {RUN_SOLUTION}\n")
    swaps = [(head_old, head_new), ("skills=['skills/sds-report-writer/']", "skills=['skills/writer/']")]
    for old, new in swaps:
        assert src.count(old) == 1, f"정답 코드에서 바꿀 곳을 찾지 못함: {old[:40]!r}"
        src = src.replace(old, new)
    first, end = "from deepagents import create_deep_agent", "\nload_dotenv()"
    assert src.count(first) == 1 and src.count(end) == 1, "정답 코드에서 import 구획을 찾지 못함"
    a, e = src.index(first), src.index(end)
    block = [ln if not ln.startswith(("import ", "from "))
             else ln.replace("# noqa: ", "# noqa: E402,", 1) if "# noqa: " in ln else ln + "  # noqa: E402"
             for ln in src[a:e].split("\n")]
    return src[:a] + TRUSTSTORE + "\n".join(block) + src[e:]


def between(lines, start, end):
    """start가 든 줄부터 end가 든 줄 앞까지. 끝의 빈 줄만 뺀다.
    들여쓰기는 원본 그대로 둔다(main()·evaluate_report 안의 코드는 4칸). starter.py에서 그 코드가 들어갈 자리와 같다."""
    a = next(k for k, ln in enumerate(lines) if start in ln)
    e = next(k for k in range(a + 1, len(lines)) if end in lines[k])
    body = lines[a:e]
    while body and not body[-1].strip():
        body.pop()
    return "\n".join(body)


def answer(*blocks):
    code = "\n\n".join(f"```python\n{b}\n```" for b in blocks)
    return f"<details><summary>정답 보기</summary>\n\n{code}\n\n</details>"


def criteria(ok, bad):
    return "**성공 기준**\n\n" + "\n".join([f"- 🟢 {x}" for x in ok] + [f"- ⛔ {x}" for x in bad])


# ── 구조도(인라인 SVG, 외부 주소 없음) ─────────────────────────────────────────
def _box(x, y, w, h, title, sub="", fill="#e8f0fe", stroke="#4a74c9", rx=8):
    t = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
         f'<text x="{x + w / 2}" y="{y + (h / 2 - 4 if sub else h / 2 + 5)}" text-anchor="middle" font-size="14" font-weight="bold">{title}</text>')
    if sub:
        t += f'<text x="{x + w / 2}" y="{y + h / 2 + 13}" text-anchor="middle" font-size="11" fill="#444">{sub}</text>'
    return t


def _note(x, y, w, h, text):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#f6f6f6" stroke="#999"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 + 4}" text-anchor="middle" font-size="11">{text}</text>')


def _arrow(d, label="", lx=0, ly=0, dash=False):
    style = ' stroke-dasharray="4 3"' if dash else ""
    t = f'<path d="{d}" fill="none" stroke="#555" stroke-width="1.5"{style} marker-end="url(#cap-arr)"/>'
    if label:
        t += f'<text x="{lx}" y="{ly}" font-size="11" fill="#333">{label}</text>'
    return t


def diagram():
    parts = [
        '<rect x="0" y="0" width="880" height="420" rx="10" fill="#ffffff" stroke="#ddd"/>',
        _box(20, 175, 80, 40, "START", fill="#eeeeee", stroke="#888", rx=20),
        _box(150, 170, 150, 50, "Supervisor", "다음 차례 결정"),
        _box(400, 40, 160, 50, "Researcher", "자료 수집"),
        _note(400, 96, 160, 26, "skill: skills/researcher/"),
        '<rect x="620" y="20" width="245" height="90" rx="6" fill="#f6f6f6" stroke="#999"/>',
        '<text x="632" y="42" font-size="12" font-weight="bold">Researcher 도구</text>',
        '<text x="632" y="64" font-size="11">search_web · rag_search(RAGaaS)</text>',
        '<text x="632" y="84" font-size="11">MCP: list_docs · read_doc · search_docs</text>',
        _box(400, 170, 160, 50, "⏸ 사용자 승인", "y: 재개 · n: 중단", fill="#fff4e5", stroke="#e0a030"),
        _note(620, 132, 160, 26, "skill: skills/writer/"),
        _box(620, 170, 160, 50, "Writer", "보고서 초안"),
        _box(400, 280, 160, 40, "END", fill="#eeeeee", stroke="#888", rx=20),
        _box(150, 350, 150, 50, "점수 출력", "막대 · 종합 점수", fill="#eef7ee", stroke="#4a9a5a"),
        _box(400, 350, 160, 50, "LLM Judge", "4항목 0.0~1.0 채점", fill="#eef7ee", stroke="#4a9a5a"),
        _box(620, 350, 160, 50, "Langfuse Score", "항목별 점수 기록", fill="#eef7ee", stroke="#4a9a5a"),
        _arrow("M100,195 L148,195"),
        _arrow("M300,178 L398,60", "리서치 전", 262, 130),
        _arrow("M400,80 L306,184"),
        _arrow("M300,195 L398,195", "리서치 후", 318, 188),
        _arrow("M560,195 L618,195", "y", 584, 188),
        _arrow("M560,65 L618,65", dash=True),
        _arrow("M700,220 L700,250 L260,250 L260,222", "초안 후 Supervisor로 복귀", 420, 244),
        _arrow("M195,220 L195,300 L398,300", "초안까지 끝", 250, 294),
        _arrow("M480,320 L480,348"),
        _arrow("M560,375 L618,375"),
        _arrow("M400,375 L302,375"),
    ]
    svg = ('<svg viewBox="0 0 880 420" width="100%" style="max-width:880px;font-family:sans-serif" role="img" '
           'aria-label="캡스톤 구조도">'
           '<defs><marker id="cap-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
           '<path d="M0,0 L10,5 L0,10 z" fill="#555"/></marker></defs>' + "".join(parts) + "</svg>")
    return f"<div style='color:#222'>{svg}</div>"


# ── 수강생 글 ─────────────────────────────────────────────────────────────────
TITLE = """# [LAB] 캡스톤: 리서치 자동화 멀티 에이전트 시스템

주제를 넣으면 Agent가 자료를 모으고, 사람이 결과를 확인해 승인하면 보고서를 쓰고, 마지막에 보고서 품질을 점수로 매기는 프로그램을 완성합니다.
이 노트북에는 채울 코드가 없습니다. 코드는 `capstone/` 폴더의 `capstone/starter.py`를 AI와 함께 고치고, 터미널에서 실행합니다. 이 노트북은 순서와 확인 기준을 알려 주는 안내서입니다."""

TITLE_META = """| 항목 | 내용 |
|---|---|
| 원본 코드 | `course/Chapter02/code/raw/06-capstone/starter.py`(TODO 11개), 정답 `course/Chapter02/code/solution/06-capstone/` |
| 수강생 작업 폴더 | `course/Chapter02/capstone/` — starter.py(원본 기반, 사용자 결정 5에 따라 Agent·노드·그래프 생성을 `main()` 안으로 옮김), mcp_server.py·skills/(정답에서), data/(원본), README.md |
| 빌더 | `dev/builders/build_capstone_guide.py`. 정답 보기는 빌드할 때 원본 정답 파일에서 잘라 넣는다(두 곳 바꿈: 실행 명령, Writer skill 경로) |
| 실행 확인 | 2026-09-28 사외(OpenAI)로 capstone 구성(mcp_server + 바꾼 정답) 실행: y → 보고서·점수(종합 0.93), n → `취소됐습니다.` 한 번 실행 약 40~50초 |"""

HOW = f"""1. 맨 위 **환경 점검** 두 셀(접힌 코드 셀)을 실행해 설정을 확인합니다.
2. 1~4장에서 무엇을 만드는지, 폴더에 무엇이 있는지 봅니다.
3. 5장대로 터미널 A에서 MCP 서버를 켭니다.
4. 6장의 단계를 차례로 진행합니다. 단계마다 **할 일** → **프롬프트 힌트**를 보고 AI에게 지시를 직접 씀 → AI가 고친 코드를 읽고 받아들일지 판단 → 접힌 "정답 보기"와 비교합니다.
5. 7장대로 터미널 B에서 실행하고, 🟢/⛔ 성공 기준으로 결과를 스스로 판단합니다.
6. 8장에서 정답과 비교하고, 9장의 평가 기준을 확인합니다.

AI에게 파일을 보여 줄 때는 `capstone/starter.py`를 열어 두고 지시합니다. 한 번에 한 단계만 시키면 결과를 검토하기 쉽습니다."""

INTRO = """만들 것은 **리서치 자동화 보고서 작성 Multi-Agent 시스템**입니다. 흐름은 여섯 단계입니다.

1. 사용자가 주제를 입력합니다.
2. Supervisor가 Researcher 실행을 결정합니다.
3. Researcher가 웹 검색, RAGaaS, MCP 문서 검색으로 자료를 모읍니다.
4. 사용자가 리서치 결과를 확인하고 보고서 작성을 승인합니다.
5. Writer가 보고서 초안을 작성합니다.
6. 최종 보고서를 평가하고 결과를 출력합니다.

4일 동안 배운 기술이 모두 들어갑니다. LangGraph 멀티 에이전트(Supervisor), 사람 승인(Human-in-the-loop), MCP 서버, RAGaaS, Deep Agents의 Skill, Langfuse 추적과 점수입니다."""

TOPIC = """둘 중 하나를 고릅니다. 어느 쪽이든 6장의 체크리스트를 똑같이 통과해야 합니다.

| | A. 제공 주제 | B. 자유 주제 |
|---|---|---|
| 주제 | "생성형 AI가 바꾸는 소프트웨어 개발의 미래" | 내 업무와 관련된 주제 한 문장 |
| 문서 | `capstone/data/`의 문서 2개 그대로 | `capstone/data/`에 내 주제의 md 문서를 넣음 |
| 보고서 양식 | Writer skill 그대로 | 필요하면 `capstone/skills/writer/` 안의 양식을 내 업무에 맞게 바꿈 |
| 고칠 곳 | `capstone/starter.py`의 TODO | A와 같음 + 맨 아래 `main('…')`의 주제 문장 |

처음이라면 A를 권합니다. A를 끝낸 뒤 B로 바꿔 한 번 더 실행해도 됩니다."""

DIAGRAM_LOOK = """**그림 읽는 법**
- 실선 화살표는 그래프가 실행되는 순서입니다. Supervisor는 매번 "리서치 전 → Researcher, 리서치 후 → (승인) → Writer, 초안까지 끝 → END"를 고릅니다.
- Researcher와 Writer는 일을 마치면 Supervisor로 돌아갑니다.
- ⏸ 사용자 승인은 Writer 바로 앞에서 그래프를 멈추는 자리입니다.
- 점선은 Researcher가 쓰는 도구입니다. 회색 상자는 각 Agent가 읽는 skill 폴더입니다.
- END 뒤에 LLM Judge가 보고서를 채점하고, 점수를 화면과 Langfuse에 남깁니다."""

FOLDER = """`capstone/` 폴더의 파일과 흐름에서의 위치입니다.

| 파일 | 하는 일 | 흐름에서 위치 |
|---|---|---|
| `capstone/starter.py` | 전체 프로그램 뼈대. `TODO` 자리를 채웁니다 | 흐름 1~6 전부 |
| `capstone/mcp_server.py` | `data/`의 문서를 도구 3개로 내주는 MCP 서버. 그대로 씁니다 | 흐름 3(자료 수집) |
| `capstone/skills/researcher/research/SKILL.md` | Researcher 규칙: 도구 쓰는 순서, 리서치 결과 형식(`## 리서치 결과:`) | 흐름 3 |
| `capstone/skills/writer/sds-report-writer/SKILL.md` | Writer 규칙: `[SDS-AI-RPT v2.1]` 보고서 양식, TL;DR 3줄, 현황 분석 표 | 흐름 5 |
| `capstone/data/ai_trends.md`, `capstone/data/llm_market.md` | MCP 서버가 보여 주는 문서 | 흐름 3 |
| `capstone/README.md` | 이 노트북 없이 폴더만 열어도 볼 수 있는 요약 | — |

`capstone/starter.py`에서 Agent, 노드, 그래프는 모두 `main()` 함수 안에 있습니다. MCP 도구를 서버에서 비동기로 받아 와야 Agent를 만들 수 있기 때문입니다."""

SERVER = f"""VS Code 메뉴 **터미널 → 새 터미널**로 터미널을 엽니다(저장소 맨 위 폴더에서 열립니다). 이 터미널을 **터미널 A**라고 하겠습니다. 아래 명령을 붙여 넣고 실행합니다.

```
{RUN_SERVER}
```

이 터미널은 끝날 때까지 닫지 않습니다. 서버 파일은 고치지 않으니 한 번 켜 두면 됩니다. 다 쓴 뒤에는 **Ctrl+C**로 끕니다."""

SERVER_OK = criteria(
    ["터미널 A에 `Uvicorn running on`과 `127.0.0.1:8001`이 든 줄이 나오고, 명령이 끝나지 않고 기다립니다."],
    ["`error while attempting to bind on address`가 든 `ERROR:` 줄이 나오고 명령이 끝납니다(맥은 `address already in use`, Windows는 `[Errno 10048]`) → 8001 포트를 다른 서버(3일차 A2A 서버, 앞서 켠 캡스톤 서버 등)가 쓰고 있습니다. 그 서버를 띄운 터미널에서 **Ctrl+C**로 끄고 다시 실행합니다. 이때도 위쪽에 `Starting MCP server` 줄은 나오니, 마지막 줄로 판단합니다.",
     "환경 점검 셀에서 Langfuse가 ⛔입니다 → `.env`의 Langfuse 값 세 개를 확인합니다. 그대로 진행해도 보고서와 점수는 나오지만 Langfuse에 기록되지 않습니다."])

STEPS_NOTE = """`capstone/starter.py`의 `TODO` 12개를 일곱 단계(6.1~6.7)로 묶었습니다. 6.1~6.7을 모두 채운 뒤 7장에서 한 번에 실행해 확인합니다. 각 단계의 🟢/⛔는 그때 볼 화면입니다.

- 중간에 실행하면 6.5를 채우기 전에는 `Graph must have an entrypoint` 오류로 멈추고, 6.5까지 채웠으면 `MCP 도구 로드: [...]` 한 줄만 나오고 끝납니다. 6.6까지 채웠으면 보고서까지 나오고 점수는 나오지 않습니다. 아직 채우지 않은 단계 때문이니 정상입니다.
- 🟢에 적힌 `🔍 Researcher 실행 중...` 같은 출력 문구는 정답 코드가 출력하는 문구입니다. 내 코드의 문구가 달라도 같은 뜻의 줄이 나오면 통과입니다.
- "정답 보기"의 코드는 `capstone/starter.py`에서 그 코드가 들어갈 자리와 같은 들여쓰기로 보여 줍니다. 옮겨 붙일 때는 바꿀 줄 전체(줄 앞 공백까지)를 지우고 그 자리에 붙여 넣습니다.
- 정답 보기에 함수나 클래스가 통째로 있으면 `capstone/starter.py`에 있던 같은 이름의 빈 함수·클래스도 지웁니다. 같은 이름이 두 번 있으면 뒤에 있는 것이 앞의 것을 덮어씁니다.

단계를 마칠 때마다 AI가 고친 부분을 직접 읽어 봅니다. 모르는 줄이 있으면 그 줄이 무엇을 하는지 AI에게 물어봅니다."""

# 막혔을 때: 공통 안내(nbkit.SELF_HELP)는 노트북 셀용이라, 터미널에서 한 프로그램을 돌리는 캡스톤에 맞게 따로 둔다
SELF_HELP_CAPSTONE = """**막혔을 때 AI에게 도움받는 프롬프트 힌트** 터미널 B에 나온 오류 메시지 전체와 방금 고친 단계(6.1~6.7 중 어디인지)를 붙여 넣고, 원인과 고칠 곳을 쉬운 말로 알려 달라고 합니다."""


def build():
    sol = solution_source()
    L = sol.splitlines()
    nb = Notebook(COURSE / "Chapter02" / "assets" / "quizzes" / "4-3-lab", "../assets/quizzes/4-3-lab")

    nb.md(TITLE)
    nb.meta(TITLE_META)
    nb.code("from config.check import check_env\n\n# 값은 출력하지 않고, 필요한 설정 이름이 있는지만 봅니다\n"
            'check_env(["EMBED_PROVIDER", "RAG_PROVIDER", "LANGFUSE"])', kind="")
    nb.code("import truststore\n\n"
            "# 파이썬이 PC에 등록된 인증서(회사 인증서 포함)를 믿게 합니다. Langfuse보다 먼저 둡니다\n"
            "truststore.inject_into_ssl()\n\n"
            "from langfuse import get_client  # noqa: E402\n\n"
            "# Langfuse 키가 맞는지 한 번 확인합니다(키 값은 출력하지 않습니다)\n"
            'print("🟢 Langfuse 연결 확인" if get_client().auth_check() else "⛔ Langfuse 연결 실패: .env의 LANGFUSE_ 값 세 개를 확인하세요")',
            kind="")
    nb.md("**볼 지점**\n- \"준비 완료\"와 \"🟢 Langfuse 연결 확인\"이 나오면 다음으로 넘어갑니다.\n"
          "- ⛔가 나오면 ⛔ 줄의 → 안내대로 `.env`를 고친 뒤 다시 실행합니다. 모르겠으면 출력을 AI에게 붙여 넣고 물어봅니다.\n- 키 값은 화면에 나오지 않습니다. 혹시 나오면 셀 출력을 지우고, 다른 곳에 붙여 넣지 않습니다.")
    nb.md(SELF_HELP_CAPSTONE)
    nb.meta("- 사용자 결정 3: Langfuse 키는 `get_client().auth_check()`로 실제 인증까지 확인합니다. 맥 `.env`의 `LANGFUSE_BASE_URL` 줄이 깨져 있어 제작 때는 환경변수로 `https://jp.cloud.langfuse.com`을 주어 확인했습니다.\n"
            "- 캡스톤은 임베딩을 쓰지 않지만 공통 지침대로 `EMBED_PROVIDER`도 점검합니다.")

    nb.h(2, "1. 캡스톤 소개")
    nb.md(INTRO)
    nb.h(3, "1.1 진행 방법")
    nb.md(HOW)

    nb.h(2, "2. 주제 고르기")
    nb.md(TOPIC)
    nb.meta("- 커리큘럼 4.3: \"자유 주제 혹은 스켈레톤 코드 기반 개발 중 선택\".\n"
            "- 자유 주제에서 사내 RAGaaS 인덱스(`index_name`)는 그대로입니다. 사내 인덱스 기본값(펫보험 약관)은 제공 주제와도 맞지 않습니다. 캡스톤용 인덱스가 있는지 강의장에서 확인이 필요합니다(미확인).")

    nb.h(2, "3. 구조도")
    nb.code("from IPython.display import HTML, display\n\n"
            "# 캡스톤 구조도(그림만 그립니다)\n"
            f"display(HTML({diagram()!r}))", kind="")
    nb.md(DIAGRAM_LOOK)

    nb.h(2, "4. 폴더 둘러보기")
    nb.md(FOLDER)
    nb.meta("- 원본 starter는 Agent 생성·그래프 컴파일이 모듈 맨 위에 있어, 그 자리에서는 비동기로 받아 오는 MCP 도구를 넣을 수 없었습니다. 사용자 결정 5에 따라 capstone 복사본은 정답처럼 모두 `main()` 안으로 옮겼습니다.\n"
            "- 복사본에서 바꾼 점: 실행 명령 안내, 쓰지 않는 import(`json`, `requests`) 삭제, `evaluate_report`의 쓰지 않는 Langfuse 변수 3줄을 `main()` 맨 위로 옮김, 오타 \"단계접\" → \"단계별\", 실행 TODO의 `app.invoke` → `app.ainvoke`(노드가 async라 invoke는 오류), MCP 연결 TODO 한 줄 추가(원본은 빈 줄), `RouteDecision`을 정답처럼 스키마 자리로 옮김.\n"
            "- skill 폴더 구조를 바꿨습니다(6.3 강사용 메모).")

    nb.h(2, "5. 준비: MCP 서버 켜기")
    nb.md(SERVER)
    nb.md(SERVER_OK)
    nb.meta("- 서버 시작 문구(사외 확인): FastMCP 배너 → `Starting MCP server 'capstone-filesystem' with transport 'sse' on …:8001/sse` → `Application startup complete.` → `Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)`.\n"
            "- 2026-09-29 리뷰: `read_doc`이 `data/` 밖(`../`·절대 경로)을 읽지 못하게 막고, 바인딩을 `0.0.0.0` → `127.0.0.1`로 바꿨습니다(같은 망의 다른 PC가 수강생 키 파일을 읽을 수 있었음). 원본 `code/solution/06-capstone/mcp_server.py`는 그대로입니다. 맥에서 두 번째 서버는 `[Errno 48] error while attempting to bind on address ('127.0.0.1', 8001): [errno 48] address already in use`로 끝나고, 이때도 `Starting MCP server` 줄은 먼저 나왔습니다. Windows `[Errno 10048]` 문구는 재현하지 않았습니다.\n"
            "- 맥에서는 `0.0.0.0:8001`(A2A 서버처럼)을 다른 프로세스가 잡고 있어도 캡스톤 서버가 `127.0.0.1:8001`에 떴습니다(주소가 더 구체적이라 함께 바인딩됨). Windows 동작은 미확인입니다.\n"
            "- 3-3 A2A 서버(`01_a2a_server.py`)도 8001을 씁니다. 포트는 그대로 두고 앞 서버를 끄도록 안내합니다(사용자 결정 6). 포트 충돌 문구는 위 항목 참고.")

    nb.h(2, "6. 단계별 체크리스트")
    nb.md(STEPS_NOTE)

    # 6.1 도구
    nb.h(3, "6.1 도구 만들기")
    nb.md("**할 일** `capstone/starter.py`의 `# TODO: 사용할 도구를 정의` 아래 `search_web`과, `rag_search` 안의 TODO를 채웁니다. "
          "`search_web`은 실제 검색 대신 정해 둔 검색 결과 몇 줄을 돌려주는 흉내 도구면 충분합니다. `rag_search`는 RAGaaS의 `retrieve-rrf`로 문서를 찾아 본문을 돌려줍니다. "
          "정답 보기를 옮겨 붙일 때는 `@tool` 줄부터 `rag_search`의 TODO 주석 끝까지를 통째로 바꿉니다.\n\n"
          "RAGaaS 요청 값(AI에게 그대로 알려 줍니다): `index_name`(인덱스 이름, `.env`의 `index_name` 값), `permission_groups`(`[\"rag-public\"]`), "
          "`query_text`(검색어), `num_result_doc`(결과 개수, 예: 3), `fields_exclude`(`[\"v_merge_title_content\"]`). "
          "요청은 `config.ragaas`의 `post_ragaas(\"retrieve-rrf\", payload)`로 보내고, 본문은 응답 JSON의 `hits` → `hits` 목록 → `_source` → `merge_title_content`에 있습니다.")
    nb.md("**프롬프트 힌트** 두 도구가 검색어를 받아 글(문자열)을 돌려줘야 한다고 먼저 말합니다. "
          "`rag_search`는 RAGaaS 요청에 넣을 값(인덱스 이름, 검색어, 결과 개수)과 응답에서 꺼낼 본문 필드를 AI에게 알려 줍니다. "
          "`search_web`은 실제 검색 없이 정해 둔 결과를 돌려주면 된다고 덧붙입니다.")
    nb.md(criteria(
        ["7장 실행 뒤 Langfuse에서 먼저 생긴 `LangGraph` trace(Researcher 실행, 7.1 표)를 열면 `rag_search` 도구 결과가 보입니다. 사내망 밖에서는 `[MOCK RAGaaS] 질문: …`으로 시작하는 문장, 사내망에서는 실제 문서 본문입니다.",
         "같은 trace의 마지막 출력(리서치 결과) 맨 아래 `### 출처`에 RAG 검색과 웹 검색이 적혀 있습니다(도구 이름 `rag_search`·`search_web` 대신 \"RAG 검색\"·\"웹 검색\"처럼 한글로 적히기도 합니다). 정답 코드는 터미널에 리서치 결과의 앞 500자만 보여 줍니다."],
        ["도구 결과가 `null`입니다 → 함수 끝에 `return`이 있는지, 뒤에 같은 이름의 빈 함수가 남아 있지 않은지 봅니다.",
         "`KeyError: 'hits'`가 납니다 → 응답에서 본문을 꺼내는 순서를 AI와 다시 확인합니다.",
         "사내망에서 인증 오류(401)가 납니다 → 저장소 맨 위에서 `uv run python -m config.check`로 RAGaaS 키 이름을 확인합니다."]))
    nb.md(answer(between(L, "@tool", "# ── State")))
    nb.meta("- 정답의 `search_web`은 실제 검색이 아니라 정해 둔 네 줄(시장 성장률 등)을 돌려줍니다. 이 숫자가 보고서에 들어갈 수 있습니다.\n"
            "- 사외 `COURSE_ENV=out`이면 `config`가 `RAG_PROVIDER=mock`을 채우고, `post_ragaas`가 네트워크 없이 모의 응답을 돌려줍니다. 정답은 mock일 때 `index_name`이 없어도 `mock-capstone`을 씁니다.\n"
            "- 사외 실행에서 Researcher trace의 도구 호출: `list_docs`, `read_doc`, `search_web` 여러 번, `rag_search` 1회, skill을 읽는 `read_file`.")

    # 6.2 State
    nb.h(3, "6.2 State 채우기")
    nb.md("**할 일** `# TODO: 필요한 필드를 추가하세요.` 아래 `State`에 노드끼리 주고받을 값을 더합니다. `main()` 안의 `initial_state`에도 같은 이름으로 처음 값을 넣습니다.")
    nb.md("**프롬프트 힌트** 노드들이 서로 넘겨받아야 하는 값(주제, 리서치 결과, 보고서 초안, 다음 차례)을 흐름 순서대로 적어 AI에게 보여 줍니다. "
          "`initial_state`에도 같은 이름으로 처음 값을 넣어야 한다고 말합니다.")
    nb.md(criteria(["7장 실행 중에 `KeyError`가 나지 않고 `🔍 Researcher 실행 중...`까지 진행됩니다."],
                   ["`KeyError: 'topic'`처럼 이름 오류가 납니다 → `State`와 `initial_state`의 이름이 노드에서 쓰는 이름과 같은지 봅니다."]))
    nb.md(answer(between(L, "class State(TypedDict)", "# ── Supervisor 라우팅"),
                 between(L, "initial_state = {", "# ── 1단계")))

    # 6.3 MCP + Agent
    nb.h(3, "6.3 MCP 연결과 두 Agent")
    nb.md("**할 일** `main()` 안의 세 TODO를 채웁니다. MCP 서버에 연결해 도구를 받아 오고(`# TODO: MCP 서버에 연결해 …`), "
          "자료조사 skill을 가진 Researcher와 보고서 작성 skill을 가진 Writer를 만듭니다.")
    nb.md("**프롬프트 힌트** MCP 도구는 8001 포트의 서버(`localhost:8001/sse`, SSE 방식)에서 비동기로 받아 온다고 알려 줍니다. "
          "각 Agent에 줄 도구, skill 폴더(`skills/researcher/`, `skills/writer/`), 역할 밖의 일을 하지 않게 하는 system prompt를 AI에게 알려 줍니다. "
          "두 Agent 모두 실행 상태를 기억할 체크포인터를 붙인다고 말합니다.")
    nb.md(criteria(
        ["7장 실행 첫 줄에 `MCP 도구 로드: ['list_docs', 'read_doc', 'search_docs']`가 나옵니다.",
         "리서치 결과가 `## 리서치 결과:`로 시작하고 `### 핵심 발견` 같은 소제목이 있습니다(Researcher skill 형식)."],
        ["`ConnectError: All connection attempts failed`가 납니다 → 5장의 MCP 서버를 먼저 켭니다.",
         "리서치 결과가 `## 리서치 결과:` 형식이 아닙니다 → skill 폴더를 못 찾은 것입니다. skill 경로는 `SKILL.md`가 든 폴더의 한 단계 위(`skills/researcher/`)를 가리켜야 합니다.",
         "`await` 관련 오류가 납니다 → MCP 도구를 받아 오는 줄과 Agent를 만드는 줄이 `main()` 안에 있는지 봅니다."]))
    nb.md(answer(between(L, "mcp_client = MultiServerMCPClient", "# ── LangGraph 노드 정의")))
    nb.meta("- **원본 정답의 조용한 결함:** 원본 정답은 `skills=['skills/researcher/']`, `skills=['skills/sds-report-writer/']`로 SKILL.md가 바로 든 폴더를 가리킵니다. deepagents 0.7.18은 skills 경로를 \"skill 폴더들이 든 상위 폴더\"로 읽어서 skill을 하나도 찾지 못합니다. 원본 그대로 실행하면 오류 없이 돌지만 리서치 결과·보고서가 skill 양식을 따르지 않습니다(2026-09-28 사외 실행으로 확인).\n"
            "- capstone 폴더는 `skills/researcher/research/SKILL.md`, `skills/writer/sds-report-writer/SKILL.md`로 한 단계 넣고, Writer 경로를 `skills/writer/`로 바꿨습니다. 정답 보기와 8장 정답 코드도 이 경로입니다. 이렇게 바꾼 뒤 `## 리서치 결과:` 형식과 `[SDS-AI-RPT v2.1]` 양식이 나오는 것을 확인했습니다.\n"
            "- skill 폴더 이름을 `research`로 맞춰 \"name과 폴더 이름이 다르다\"는 deepagents 경고도 없앴습니다.")

    # 6.4 nodes
    nb.h(3, "6.4 노드 만들기")
    nb.md("**할 일** `# TODO: Supervisor 노드 정의`, `# TODO: Researcher 노드 정의`, `# TODO: Writer 노드 정의` 아래 세 함수의 `pass`를 채웁니다. "
          "정답 보기를 옮겨 붙일 때는 `supervisor_llm` 줄부터 `writer_node`의 `pass`까지를 통째로 바꿉니다.")
    nb.md("**프롬프트 힌트** Supervisor에게 지금 상황(주제, 리서치 완료 여부, 초안 완료 여부)을 알려 주고, 세 선택지(researcher, writer, END)를 언제 고르는지 먼저 정리해 AI에게 줍니다. "
          "Researcher·Writer 노드는 Agent 실행 결과의 마지막 메시지를 State의 어느 값에 넣는지 말합니다. "
          "두 노드는 비동기(`async`)이고 Langfuse 추적 설정을 함께 넘기며, 시작할 때 `🔍 Researcher 실행 중...`·`✍️  Writer 실행 중...`을 출력한다고 덧붙입니다.")
    nb.md(criteria(["7장 실행에서 `🔍 Researcher 실행 중...`과 `✍️  Writer 실행 중...`이 한 번씩만 나옵니다."],
                   ["같은 Agent가 되풀이해 실행됩니다 → 터미널 B에서 **Ctrl+C**로 멈춥니다. Supervisor가 받는 상황 글에 리서치·초안 완료 여부가 들어 있는지, "
                    "두 노드가 결과를 State 값으로 돌려주는지(정답은 `return {'research_result': …}`·`return {'draft': …}`) 봅니다.",
                    "Writer가 리서치 결과 없이 글을 씁니다 → Writer 노드가 State의 리서치 결과를 지시에 넣는지 봅니다.",
                    "`KeyError: ''`가 납니다 → Supervisor 노드가 다음 차례를 돌려주지 않은 것입니다. `pass`만 있는 같은 이름의 빈 함수가 뒤에 남아 있지 않은지 봅니다."]))
    nb.md(answer(between(L, "supervisor_llm = get_llm()", "def route(")))

    # 6.5 graph + approval
    nb.h(3, "6.5 그래프 조립과 승인 지점")
    nb.md("**할 일** `# TODO: 그래프 조립` 아래에 노드 사이 연결을 넣고, 바로 아래 `app = builder.compile()`에 Writer 앞에서 멈추는 설정을 더합니다.")
    nb.md("**프롬프트 힌트** 노드 사이 연결(시작 → Supervisor, Supervisor의 세 갈래, 각 Agent 뒤 Supervisor로 복귀)을 그림처럼 말로 적어 AI에게 줍니다. "
          "Writer 실행 전에 멈춰야 한다는 조건과, 멈춘 상태를 기억할 장치가 필요하다는 점을 함께 말합니다.")
    nb.md(criteria(["7장 실행에서 리서치 결과가 나온 뒤 `보고서 작성을 시작할까요? (y/n):`에서 멈춥니다."],
                   ["멈추지 않고 곧장 Writer까지 갑니다 → `compile()`에 체크포인터와 Writer 앞 중단 설정이 있는지 봅니다.",
                    "`KeyError: 'END'` 같은 갈림길 오류가 납니다 → Supervisor의 세 선택지가 모두 연결되어 있는지 봅니다."]))
    nb.md(answer(between(L, "builder.add_edge(START", "config = {'configurable'")))

    # 6.6 run + resume
    nb.h(3, "6.6 실행과 재개")
    nb.md("**할 일** `main()` 맨 아래 `# TODO: app.ainvoke로 실행하고 단계별 진행 상황 출력`을 채웁니다. 리서치까지 실행 → 결과 보여 주기 → 터미널에서 승인 입력 → Writer부터 이어서 실행 → 보고서 출력 순서입니다.")
    nb.md("**프롬프트 힌트** 리서치까지 실행 → 결과 보여 주기 → `y/n` 입력 받기 → 재개의 순서를 AI에게 알려 줍니다. "
          "재개할 때는 같은 `thread_id`로, 새 입력 없이 이어서 실행한다고 말합니다. "
          "`n`이면 안내 문구를 출력하고 끝낸다고 덧붙입니다.")
    nb.md(criteria(["`y`를 입력하면 `--- 2단계: 보고서 작성 ---` 뒤에 `[SDS-AI-RPT v2.1]`로 시작하는 보고서가 나옵니다. TL;DR이 세 줄(①②③)이고 현황 분석에 표가 있습니다.",
                    "`n`을 입력하면 `취소됐습니다.`가 나오고 끝납니다. 한 번 실행에서는 한쪽만 볼 수 있으니, 다른 쪽은 한 번 더 실행해 확인합니다."],
                   ["승인한 뒤 아무것도 나오지 않습니다 → 재개할 때 같은 `thread_id`와 빈 입력(`None`)으로 실행하는지 봅니다. Writer 노드가 `draft`를 돌려주는지도 봅니다.",
                    "`No synchronous function provided` 오류가 납니다 → 노드가 비동기라 `invoke` 대신 `ainvoke`로 실행합니다.",
                    "보고서가 `[SDS-AI-RPT v2.1]` 양식이 아닙니다 → 6.3의 Writer skill 경로를 봅니다.",
                    "`y`를 넣었는데 `취소됐습니다.`가 나옵니다 → 한글 입력 상태라 `ㅛ`가 들어갔거나, `yes`나 빈 Enter를 넣은 것입니다. 정답 코드는 `y` 한 글자만 승인으로 봅니다. 영문 입력으로 바꾸고 다시 실행합니다."]))
    nb.md(answer(between(L, "# ── 1단계", "# ── 3단계")))

    # 6.7 evaluation
    nb.h(3, "6.7 보고서 평가")
    nb.md("**할 일** `evaluate_report` 함수의 `# TODO: 평가를 진행하고 Langfuse에 점수를 기록`을 채우고, `main()`에서 보고서를 출력한 뒤 이 함수로 채점해 점수를 보여 줍니다.")
    nb.md("**프롬프트 힌트** 네 평가 항목(Relevance, Faithfulness, Completeness, Clarity)의 뜻과 0.0~1.0 점수 범위를 AI에게 그대로 알려 주고, 근거 없이 높은 점수를 주지 않게 하라고 말합니다. "
          "점수는 채점한 호출의 trace에 항목 이름으로 하나씩 남긴다고 말합니다. "
          "화면에는 항목별 막대와 점수·근거를 출력하고, 그 아래에 평균을 `종합 점수`로 출력한다고 덧붙입니다.")
    nb.md(criteria(["관련성·근거충실도·완성도·명확성 네 줄에 막대(`█░`), 점수, 근거가 나오고 마지막에 `종합 점수`가 나옵니다.",
                    "Langfuse에 채점 trace가 생기고 relevance·faithfulness·completeness·clarity 점수 네 개가 붙습니다(찾는 법은 7장)."],
                   ["`'NoneType' object has no attribute 'relevance'` 오류가 납니다 → `evaluate_report` 끝에 평가 결과를 돌려주는 `return`이 있는지 봅니다.",
                    "점수는 나오는데 Langfuse에 없습니다 → 환경 점검 셀의 Langfuse 결과와, 프로그램 끝에서 기록을 내보내는지(`flush`) 봅니다.",
                    "네 점수가 모두 1.0입니다 → Judge 지시에 엄격하게 채점하라는 조건이 있는지 봅니다."]))
    nb.md(answer(between(L, "evaluation: ReportEvaluation =", "# ── 메인 함수"),
                 between(L, "# ── 3단계", "if __name__")))

    nb.h(2, "7. 전체 실행")
    nb.md(f"""VS Code 메뉴 **터미널 → 새 터미널**로 터미널을 하나 더 엽니다(**터미널 B**). 터미널이 둘이 되면 터미널 창 오른쪽에 목록이 생기고, 눌러서 A와 B를 오갑니다. 터미널 A의 MCP 서버는 켜 둔 채로, 터미널 B에서 실행합니다.

```
{RUN_STARTER}
```

1. `MCP 도구 로드: [...]`가 나오고 `🔍 Researcher 실행 중...`으로 리서치가 시작됩니다.
2. 리서치 결과(앞부분)가 나온 뒤 `보고서 작성을 시작할까요? (y/n):`에서 멈춥니다. 결과를 읽어 봅니다.
3. 영문 입력 상태에서 `y`를 입력하고 Enter를 누르면 보고서 작성과 평가가 이어집니다. `n`이면 여기서 끝납니다. 한글 입력 상태의 `ㅛ`나 빈 Enter도 취소로 처리됩니다.
4. 보고서와 네 항목 점수, `종합 점수`가 나오면 끝입니다. 한 번 실행에 1분 안팎이 걸립니다.

프로그램이 끝나면 멈춰 둔 상태도 사라집니다. `y`와 `n`의 결과를 둘 다 보려면 한 번 더 실행합니다. 코드를 고친 뒤에도 터미널 B에서 같은 명령으로 다시 실행합니다. 터미널 A의 서버는 다시 켤 필요가 없습니다.""")
    nb.h(3, "7.1 Langfuse에서 내 실행 찾기")
    nb.md("""Langfuse 대시보드의 Traces 목록은 최근 실행이 위에 옵니다. 방금 실행한 시각의 trace 세 개를 찾습니다.

| trace 이름 | 무엇 | 볼 것 |
|---|---|---|
| `LangGraph` (먼저 생긴 것) | Researcher 실행 | 도구 호출(`list_docs`, `read_doc`, `rag_search`, `search_web`)과 그 결과 |
| `LangGraph` (나중에 생긴 것) | Writer 실행 | skill 파일을 읽고 보고서를 쓴 과정 |
| `RunnableSequence` | LLM Judge 채점 | **Scores**에 relevance·faithfulness·completeness·clarity 네 점수 |

같은 Langfuse 프로젝트를 여럿이 함께 쓰면 다른 사람의 trace도 섞여 보입니다. 실행한 시각으로 내 것을 고릅니다.""")
    nb.md(criteria(["`y`로 끝까지 실행한 뒤, 방금 실행한 시각에 위 세 trace가 있고 채점 trace에 점수 네 개가 붙어 있습니다."],
                   ["trace가 하나도 없습니다 → 환경 점검 셀의 Langfuse 결과를 다시 봅니다. ⛔이면 `.env`의 Langfuse 값을 고치고 7장을 다시 실행합니다."]))
    nb.meta("- trace 이름은 2026-09-28 사외 실행으로 확인했습니다(Researcher·Writer: `LangGraph`, Judge: `RunnableSequence`). 원본 코드는 trace 이름·태그를 붙이지 않으므로 시각으로 찾습니다. Supervisor 호출은 추적 설정이 없어 trace가 없습니다.\n"
            "- 채점 trace에 score 네 개가 보이는지는 Langfuse 조회 API 제한으로 자동 확인하지 못했습니다(미확인). 수업 전에 대시보드에서 직접 확인합니다.\n"
            "- 강의장 사내 게이트웨이에서 Supervisor·Judge의 구조화 출력(`with_structured_output`)과 Deep Agent의 도구 호출은 미검증입니다. 사내 Langfuse 구성도 미정입니다.\n"
            "- 사외 실행 시간: 약 40~50초(y), 약 25초(n).")

    nb.h(2, "8. 정답과 비교하기")
    nb.h(3, "8.1 AI에게 차이 리뷰받기")
    nb.md("6장의 단계마다 접힌 \"정답 보기\"를 펼쳐 내 코드와 비교합니다. 다르다고 틀린 것은 아닙니다. 차이가 결과에 어떤 영향을 주는지가 중요합니다.")
    nb.md("**프롬프트 힌트** 정답 보기 코드와 내 코드의 같은 부분을 함께 AI에게 보여 주고, 다른 점과 그 차이가 실행 결과에 주는 영향만 설명해 달라고 합니다. "
          "코드는 고치지 말라고 덧붙입니다.")
    nb.md(criteria(["AI가 차이마다 \"결과에 영향 있음/없음\"과 이유를 설명하고, 내 파일은 바뀌지 않았습니다."],
                   ["AI가 내 코드를 정답으로 바꿔 버렸습니다 → 되돌리고, 고치지 말라는 조건을 지시 맨 앞에 둡니다."]))
    nb.h(3, "8.2 정답 코드 실행해 점수 비교하기")
    nb.md(f"""내 코드를 먼저 완성한 뒤에 합니다. 아래 셀을 실행하면 `capstone/solution.py`에 정답 코드 전체가 만들어집니다. 셀에 보이는 코드가 정답 전체입니다. 터미널 A의 서버는 켜 둔 채 터미널 B에서 실행합니다.

```
{RUN_SOLUTION}
```

내 실행과 정답 실행의 네 항목 점수와 근거를 나란히 놓고 봅니다. 점수는 같은 코드로도 실행할 때마다 조금씩 달라집니다. 한두 번의 차이보다 **근거 글**에서 무엇이 부족하다고 했는지를 비교합니다.""")
    # 정답 코드 셀: 보이게 둔다(출력 문구에 ✍️가 있어, 숨기면 QC가 "빈칸 셀이 숨겨짐"으로 본다)
    nb.code("%%writefile ../capstone/solution.py\n" + sol.rstrip("\n"), visible=True, kind="")
    nb.md(criteria(["정답 실행에서도 `[SDS-AI-RPT v2.1]` 보고서와 네 항목 점수가 나옵니다. 내 점수의 근거와 정답 점수의 근거를 비교해 차이 한 가지를 말할 수 있습니다."],
                   ["`error while attempting to bind on address` 또는 연결 오류가 납니다 → 5장의 서버 안내를 다시 봅니다."]))
    nb.meta("- 정답 코드 셀은 원본 정답에 세 곳만 바꿨습니다(실행 명령 설명, Writer skill 경로, 맨 위 truststore 두 줄 — 사내망 Langfuse용, starter.py와 같음). 사외 실행 종합 점수 0.90(원본 skill 경로), 0.93(바꾼 경로).\n"
            "- `capstone/solution.py`는 `.gitignore` 대상이라 제작 저장소에 남지 않습니다.")

    nb.h(2, "9. 평가 기준")
    nb.md("""1. **체크리스트 통과:** 6장의 일곱 단계를 모두 통과합니다(7장 실행에서 각 단계의 🟢를 확인).
2. **보고서 품질:** LLM Judge 네 항목으로 평가합니다. 각 항목 0.0~1.0 점수와 채점 근거, 평균 점수가 나오고 Langfuse Score로 기록됩니다.

| 항목 | 화면 이름 | 보는 것 |
|---|---|---|
| Relevance | 관련성 | 주제와 관련 있는가 |
| Faithfulness | 근거충실도 | 리서치 근거에 충실한가 |
| Completeness | 완성도 | 보고서 구성이 완성되어 있는가 |
| Clarity | 명확성 | 문장과 구조가 명확한가 |

**일찍 끝났다면(선택):** 터미널의 `y/n` 승인을 Streamlit 화면의 버튼으로 바꿔 봅니다. 또는 2장의 B(자유 주제)로 바꿔 한 번 더 실행합니다.

다 쓴 뒤에는 터미널 A에서 **Ctrl+C**로 MCP 서버를 끕니다. 터미널 B의 프로그램은 점수를 출력하면 저절로 끝납니다.""")
    nb.meta("- 사용자 결정 4: 배점은 슬라이드의 Judge 평가 4항목 + 체크리스트만. 받은 zip README의 배점 표(Supervisor 30 / HITL 25 / MCP 20 / Streamlit UI 15 / skills 10)는 흐름이 현재 슬라이드·코드와 달라 옮기지 않았습니다. Streamlit은 조기 완료자 선택 과제.")
    nb.finish(OUT)


if __name__ == "__main__":
    build()
