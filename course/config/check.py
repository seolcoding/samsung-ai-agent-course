"""연결 설정 점검. 키·토큰 값은 출력하지 않고, 이름이 있는지만 본다.

실행(저장소 맨 위):
    uv run python -m config.check            설정 점검
    uv run python -m config.check --live     실제로 모델·임베딩을 한 번씩 호출해 본다(요청 1~2회)
    uv run python -m config.check --json     AI 도우미가 읽기 좋은 JSON으로 출력
    uv run python -m config.check --langfuse Langfuse 키(2부 관측 실습·캡스톤)도 본다
노트북:
    from config.check import check_env
    check_env()                              # LLM만 본다
    check_env(["EMBED_PROVIDER", "RAG_PROVIDER"])   # 임베딩·RAGaaS도 본다
    check_env(["LANGFUSE"])                         # Langfuse(2부 관측 실습)도 본다

결과 표시: 🟢 문제없음, ⛔ 고쳐야 함, ⚠️ 확인 필요(동작은 할 수 있음)
"""

import importlib.util
import json
import os
import re
import sys
from pathlib import Path

import config

# 연결 방식마다 .env에 있어야 하는 이름
REQUIRED = {
    "LLM_PROVIDER": {
        "samsung": ["api_base_url", "model", "credential_key", "send_system_name", "user_id"],
        "openai": ["OPENAI_API_KEY", "OPENAI_MODEL"],
    },
    "EMBED_PROVIDER": {
        "samsung": ["embedding_api_url", "embedding_x_dep_ticket"],
        "openai": ["OPENAI_API_KEY", "OPENAI_EMBEDDING_MODEL"],
    },
    "RAG_PROVIDER": {
        "samsung": ["search_url", "rag_credential_key", "rag_api_key"],
        "mock": [],
    },
    # 연결 방식이 하나뿐인 설정(2부 관측 실습·캡스톤)
    "LANGFUSE": {
        "on": ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL"],
    },
}
ALIAS = {"LANGFUSE_BASE_URL": "LANGFUSE_HOST"}  # 예전 이름도 받는다
ROOT = Path(__file__).resolve().parents[2]  # course/config/check.py → 저장소 맨 위
_SECRET = re.compile(r"(sk-[A-Za-z0-9_-]{4})[A-Za-z0-9_-]+|([A-Za-z0-9_-]{6})[A-Za-z0-9_-]{20,}")


def _mask(text):
    """오류 메시지 속 키처럼 보이는 긴 문자열을 가린다."""
    return _SECRET.sub(lambda m: (m.group(1) or m.group(2)) + "…(가림)", str(text))[:300]


def _item(status, name, detail, fix=""):
    return {"status": status, "name": name, "detail": detail, "fix": fix}


def _env_encoding(path):
    """설정 파일이 어떻게 저장되었는지 본다. BOM 없는 UTF-8이 아니면 윈도우에서 문제가 생길 수 있다."""
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-bom"
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        return "other"
    return "utf-8"


def report(groups=("LLM_PROVIDER",), live=False):
    """점검 결과를 목록으로 돌려준다. 값은 담지 않는다."""
    items = []

    # 1. 파이썬과 가상환경
    ok_py = sys.version_info >= (3, 12)
    items.append(_item("🟢" if ok_py else "⛔", "파이썬", f"{sys.version.split()[0]}",
                       "" if ok_py else "저장소 맨 위에서 uv sync --extra notebooks 후 커널을 .venv로 고른다"))
    in_venv = Path(sys.prefix).resolve() == (ROOT / ".venv").resolve()
    items.append(_item("🟢" if in_venv else "⚠️", "커널(가상환경)", sys.prefix,
                       "" if in_venv else "VS Code 커널을 저장소의 .venv로 고른다"))

    # 2. .env
    env_file = config.ENV_FILE
    items.append(_item("🟢" if env_file else "⛔", ".env 파일", env_file or "찾지 못함",
                       "" if env_file else ".env.sample을 저장소 맨 위에 .env로 복사한다"))
    saved = _env_encoding(env_file) if env_file else "utf-8"
    if saved != "utf-8":  # 정상일 때는 줄을 늘리지 않는다
        detail = ("UTF-8(BOM 있음). 노트북은 읽지만 uv run --env-file은 값을 읽지 못한다" if saved == "utf-8-bom"
                  else "UTF-8이 아님(cp949 등). 지금은 cp949로 읽지만 다른 도구는 읽지 못할 수 있다")
        items.append(_item("⚠️", ".env 저장 방식", detail, "VS Code로 .env를 열고 오른쪽 아래 인코딩을 눌러 'UTF-8로 저장'을 고른다"))

    # 3. 실행 환경(COURSE_ENV)
    raw_mode = os.getenv("COURSE_ENV", "")
    if config.MODE in config.MODES:
        items.append(_item("🟢", "실행 환경(COURSE_ENV)", f"{config.MODE} ({'사내' if config.MODE == 'samsung' else '사외'})"))
    elif raw_mode:
        items.append(_item("⛔", "실행 환경(COURSE_ENV)", f"알 수 없는 값: {raw_mode}", "samsung(사내) 또는 out(사외)으로 적는다"))
    else:
        items.append(_item("⚠️", "실행 환경(COURSE_ENV)", "없음. 각 PROVIDER 값(없으면 samsung)을 그대로 쓴다",
                           ".env 맨 위에 COURSE_ENV=samsung 또는 COURSE_ENV=out을 적는다"))

    # 4. 연결 방식별 필요한 이름
    for group in groups:
        kind = "on" if group == "LANGFUSE" else os.getenv(group, "samsung").strip().lower()
        need = REQUIRED[group].get(kind)
        if need is None:
            items.append(_item("⛔", group, f"알 수 없는 값: {kind}", f"{' 또는 '.join(REQUIRED[group])} 중 하나"))
            continue
        missing = [n for n in need if not os.getenv(n, "").strip() and not os.getenv(ALIAS.get(n, ""), "").strip()]
        odd = [n for n in need if os.getenv(n, "").lstrip().startswith("#")]  # 빈 값 뒤 주석이 값으로 읽힌 경우
        if missing or odd:
            detail = f"{kind} — 빠진 이름: {', '.join(missing)}" if missing else f"{kind}"
            if odd:
                detail += f" / 값이 '#'로 시작함(주석이 값으로 읽힘): {', '.join(odd)}"
            items.append(_item("⛔", group, detail, ".env에서 이 이름들의 값을 채운다(설명은 윗줄에)"))
        else:
            items.append(_item("🟢", group, f"{kind} — 필요한 이름 {len(need)}개 있음"))

    # 5. 패키지
    mods = ["dotenv", "langchain_openai", "openai", "requests"] + (["langfuse"] if "LANGFUSE" in groups else [])
    for mod in mods:
        found = importlib.util.find_spec(mod) is not None
        items.append(_item("🟢" if found else "⛔", f"패키지 {mod}", "설치됨" if found else "없음",
                           "" if found else "저장소 맨 위에서 uv sync --extra notebooks"))

    # 6. 실제 호출(선택)
    if live:
        items += _live(groups)
    return items


def _live(groups):
    out = []
    try:
        from config.llm import get_llm

        answer = get_llm().invoke("한 단어로만 답하세요: 안녕").content
        out.append(_item("🟢", "LLM 호출", f"응답 받음({len(str(answer))}자)"))
    except Exception as e:  # noqa: BLE001 — 어떤 오류든 보고한다
        out.append(_item("⛔", "LLM 호출", f"{type(e).__name__}: {_mask(e)}", "course/agent_docs/troubleshooting.md의 'LLM·API 호출' 표"))
    if "EMBED_PROVIDER" in groups:
        try:
            from config.embeddings import get_embeddings

            dim = len(get_embeddings().embed_query("테스트"))
            out.append(_item("🟢", "임베딩 호출", f"벡터 {dim}차원"))
        except Exception as e:  # noqa: BLE001
            out.append(_item("⛔", "임베딩 호출", f"{type(e).__name__}: {_mask(e)}", "course/agent_docs/troubleshooting.md"))
    return out


def check_env(groups=(), live=False):
    """점검 결과를 사람이 읽기 좋게 출력하고, 막히는 것이 없으면 True를 돌려준다. LLM은 늘 본다."""
    groups = ["LLM_PROVIDER", *[g for g in groups if g != "LLM_PROVIDER"]]
    items = report(groups, live)
    for i in items:
        print(f"{i['status']} {i['name']}: {i['detail']}" + (f"\n     → {i['fix']}" if i["fix"] and i["status"] != "🟢" else ""))
    blocked = [i for i in items if i["status"] == "⛔"]
    print()
    if blocked:
        print(f"준비가 덜 되었습니다. 고칠 곳 {len(blocked)}개가 있습니다. 위 ⛔ 줄의 → 안내대로 고친 뒤 다시 실행합니다. 모르겠으면 이 출력을 AI에게 붙여 넣고 물어봅니다.")
    else:
        print("준비 완료: 실습에 필요한 설정이 모두 있습니다.")
    return not blocked


if __name__ == "__main__":
    # 출력을 파이프·파일로 받아도(AI 도우미가 --json을 붙잡는 경우 등) 윈도우 cp949에서 이모지가 깨지지 않게 한다.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    args = sys.argv[1:]
    groups = ["LLM_PROVIDER", "EMBED_PROVIDER", "RAG_PROVIDER"]  # 명령으로 실행하면 전부 본다
    if "--langfuse" in args:  # 2부 관측 실습·캡스톤
        groups.append("LANGFUSE")
    if "--json" in args:
        items = report(groups, live="--live" in args)
        print(json.dumps({"ok": not any(i["status"] == "⛔" for i in items), "items": items}, ensure_ascii=False, indent=1))
    else:
        sys.exit(0 if check_env(groups, live="--live" in args) else 1)
