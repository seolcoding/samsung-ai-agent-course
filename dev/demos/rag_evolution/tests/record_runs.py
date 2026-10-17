"""OpenAI로 단계별 예시 질문을 실제 실행해 녹화 재생용 data/recorded_runs.json을 만든다.

실제 API를 호출한다(비용 발생). 인증 값은 출력·저장하지 않는다.
단계마다 예시 질문을 위에서부터 한 대화로 이어서 실행한다(3단계부터는 이전 대화를 기억한다).
프로젝트 루트에서: uv run --env-file .env python dev/demos/rag_evolution/tests/record_runs.py [단계 번호...]
"""

import datetime
import json
from pathlib import Path
import sys

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from backend import RECORDINGS, MemorySaver, build_store, load_recordings, recording_key, resolve_settings, run_live
from lesson import RUN_STAGES, STAGES

OPTS = {"role": "동물보험 안내 도우미", "style": "짧은 문단", "top_k": 3, "chunk_size": 600}


def merged(events: list) -> list:
    """연속된 답변 글자 이벤트를 하나로 합쳐 파일을 줄인다."""
    result = []
    for event in events:
        if event["type"] == "token" and result and result[-1]["type"] == "token":
            result[-1] = {"type": "token", "text": result[-1]["text"] + event["text"]}
        else:
            result.append(event)
    return result


def main(stages: list[int]):
    settings = resolve_settings("OpenAI 실행")
    store = build_store(settings, OPTS["chunk_size"])
    data = load_recordings()
    data["meta"] = {"recorded_at": datetime.date.today().isoformat(), "model": settings["model"],
                    "embedding": settings["embed_model"], **OPTS}
    jobs = [(n, q) for n in stages for q in STAGES[n]["examples"]]
    wanted = {recording_key(n, q) for n in RUN_STAGES for q in STAGES[n]["examples"]}
    data["runs"] = {key: run for key, run in data["runs"].items() if key in wanted}   # 빠진 예시는 지운다
    failures, history, memory, current = 0, [], None, None
    for index, (stage, question) in enumerate(jobs, start=1):
        if stage != current:                       # 단계가 바뀌면 새 대화
            current, history, memory = stage, [], MemorySaver()
        try:
            events = merged(list(run_live(stage, question, settings, OPTS, lambda: store,
                                          history=history, memory=memory, thread_id=f"record-{stage}")))
        except Exception as exc:
            failures += 1
            print(f"✖ [{index}/{len(jobs)}] {stage}단계 {question} | {type(exc).__name__} | 설정·연결 확인 후 다시 실행", flush=True)
            continue
        answer = "".join(e["text"] for e in events if e["type"] == "token")
        history += [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]
        data["runs"][recording_key(stage, question)] = {"stage": stage, "question": question, "opts": OPTS, "events": events}
        metrics = next(e["data"] for e in events if e["type"] == "metrics")
        pages = sorted({s.get("page") for e in events if e["type"] == "sources" for s in e["data"] if s.get("page")})
        tools = [e["data"]["name"] for e in events if e["type"] == "step" and e["name"] == "도구 호출 요청"]
        review = next((e["data"].get("status") for e in events if e["type"] == "review"), "-")
        print(f"✔ [{index}/{len(jobs)}] {stage}단계 · {question}\n"
              f"    LLM {metrics['llm_calls']}회 · {metrics['seconds']}초 · 도구 {tools} · 근거 쪽 {pages} · 검토 {review}\n"
              f"    {answer[:200]!r}", flush=True)
        RECORDINGS.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"녹화 {len(jobs) - failures}/{len(jobs)}건 · {RECORDINGS}")


if __name__ == "__main__":
    main([int(arg) for arg in sys.argv[1:]] or list(RUN_STAGES))
