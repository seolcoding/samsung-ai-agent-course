"""1~8단계 실행 함수와 녹화 재생을 외부 API 없이 확인한다(가짜 임베딩·가짜 모델)."""

import json
from pathlib import Path
import sys
import unittest

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.vectorstores import InMemoryVectorStore

from backend import (RECORDINGS, Context, MemorySaver, keyword_search, recording_key, run_advanced_rag,
                     run_langgraph, run_lcel_chain, run_naive_rag, run_prompt_template, run_replay,
                     run_tool_calling)
from lesson import COMMON_QUESTION, MEMORY_ASK, MEMORY_TELL, RUN_STAGES, STAGES

OPTS = {"role": "도우미", "style": "짧은 문단", "top_k": 2, "chunk_size": 600}
DOCS = [Document(page_content="보험금은 청구서류 접수일부터 3영업일 이내에 지급합니다.", metadata={"page": 28, "chunk_id": 1}),
        Document(page_content="청약은 보험증권을 받은 날부터 15일 이내에 철회할 수 있습니다.", metadata={"page": 24, "chunk_id": 2}),
        Document(page_content="보험료 납입연체로 해지된 계약은 3년 이내에 부활을 청약할 수 있습니다.", metadata={"page": 27, "chunk_id": 3})]


class FakeStore(InMemoryVectorStore):
    """Chroma처럼 get()으로 전체 청크를 돌려준다."""

    def get(self, include=None):
        return {"documents": [d.page_content for d in DOCS], "metadatas": [d.metadata for d in DOCS]}


def store():
    return FakeStore.from_documents(DOCS, DeterministicFakeEmbedding(size=16))


def fake_llm(*texts):
    return GenericFakeChatModel(messages=iter([AIMessage(content=t) for t in texts or ["3영업일 이내입니다. [PDF 28쪽]"]]))


def ctx(llm, history=None, **kwargs):
    return Context(settings={"mode": "openai", "model": "fake"}, opts=OPTS, llm=llm,
                   store_factory=store, history=history or [], **kwargs)


def collect(events):
    events = list(events)
    answer = "".join(e["text"] for e in events if e["type"] == "token")
    steps = {e["name"]: e["data"] for e in events if e["type"] == "step"}
    sources = [s for e in events if e["type"] == "sources" for s in e["data"]]
    return answer, steps, sources


class FakeToolModel:
    """bind_tools 후 정해진 응답을 차례로 돌려준다."""

    def __init__(self, replies):
        self.replies, self.inputs = iter(replies), []

    def bind_tools(self, tools):
        self.tool_names = [t.name for t in tools]
        return self

    def invoke(self, messages):
        self.inputs.append(list(messages))
        return next(self.replies)


HISTORY = [{"role": "user", "content": MEMORY_TELL}, {"role": "assistant", "content": "콩이를 기억할게요."}]


class StageTests(unittest.TestCase):
    def test_prompt_template_fills_role_and_style_without_history(self):
        _, steps, _ = collect(run_prompt_template("질문", ctx(fake_llm("답"), HISTORY)))
        prompt = steps["완성된 프롬프트"]
        self.assertIn("너는 도우미다", prompt[0]["content"])
        self.assertEqual(len(prompt), 2, "2단계는 이전 대화를 보내지 않는다")

    def test_lcel_chain_sends_history(self):
        answer, steps, _ = collect(run_lcel_chain(MEMORY_ASK, ctx(fake_llm("콩이입니다."), HISTORY)))
        self.assertEqual(answer, "콩이입니다.")
        self.assertEqual(steps["체인과 함께 보낸 이전 대화"]["history"][0], {"role": "human", "content": MEMORY_TELL})

    def test_tool_calling_reads_pdf_page_and_returns_tool_message(self):
        call = AIMessage(content="", tool_calls=[{"name": "insurance_pdf_page", "args": {"page": 28}, "id": "c1", "type": "tool_call"}])
        model = FakeToolModel([call, AIMessage(content="3영업일 [PDF 28쪽]")])
        answer, _, sources = collect(run_tool_calling(COMMON_QUESTION, ctx(model, HISTORY)))
        self.assertIn("insurance_pdf_page", model.tool_names)
        self.assertNotIn("insurance_search", model.tool_names)
        self.assertEqual(model.inputs[0][1], ("human", MEMORY_TELL), "이전 대화가 함께 간다")
        self.assertEqual(model.inputs[-1][-1].type, "tool")
        self.assertEqual(sources[0]["page"], 28)
        self.assertEqual(answer, "3영업일 [PDF 28쪽]")

    def test_tool_calling_loop_limit_raises(self):
        call = AIMessage(content="", tool_calls=[{"name": "cost_sum", "args": {"amounts": [1]}, "id": "c1", "type": "tool_call"}])
        with self.assertRaises(RuntimeError):
            list(run_tool_calling("반복", ctx(FakeToolModel([call] * 20))))

    def test_langgraph_checkpointer_remembers_between_turns(self):
        memory = MemorySaver()
        first = FakeToolModel([AIMessage(content="기억할게요.")])
        collect(run_langgraph(MEMORY_TELL, ctx(first, memory=memory, thread_id="t1")))
        second = FakeToolModel([AIMessage(content="콩이입니다.")])
        answer, steps, _ = collect(run_langgraph(MEMORY_ASK, ctx(second, memory=memory, thread_id="t1")))
        self.assertEqual(answer, "콩이입니다.")
        self.assertEqual(steps["checkpointer가 기억하는 메시지"]["count"], 3)
        sent = [m.content for m in second.inputs[0]]
        self.assertIn(MEMORY_TELL, sent)
        self.assertEqual(sum(m.type == "system" for m in second.inputs[0]), 1, "system은 한 번만")
        other = FakeToolModel([AIMessage(content="모릅니다.")])
        _, steps, _ = collect(run_langgraph(MEMORY_ASK, ctx(other, memory=memory, thread_id="t2")))
        self.assertEqual(steps["checkpointer가 기억하는 메시지"]["count"], 0, "다른 thread_id는 새 대화")

    def test_naive_rag_retrieves_and_cites(self):
        answer, steps, sources = collect(run_naive_rag("보험금 지급 기간", ctx(fake_llm())))
        self.assertIn("[PDF 28쪽]", answer)
        self.assertEqual(len(sources), 2)
        self.assertEqual(len(steps["④ 검색 결과"]["pages"]), 2)

    def test_keyword_search_prefers_exact_terms(self):
        self.assertEqual(keyword_search(DOCS, "부활 청약", 1)[0].metadata["page"], 27)

    def test_advanced_rag_rewrites_merges_and_reranks(self):
        llm = fake_llm('["보험료 납입연체 해지", "계약 부활"]', '{"1": 3, "2": 0, "3": 1}', "3년 이내 부활 가능 [PDF 27쪽]")
        answer, steps, sources = collect(run_advanced_rag("보험료 깜빡하면?", ctx(llm)))
        self.assertEqual(steps["① Query Rewrite"]["queries"], ["보험료 깜빡하면?", "보험료 납입연체 해지", "계약 부활"])
        self.assertEqual(len(steps["② Hybrid Search 후보 (RRF 상위 8)"]["pages"]), 3)
        self.assertEqual(len(sources), 2, "0점은 빠지고 top_k=2까지")
        self.assertIn("[PDF 27쪽]", answer)

    def test_advanced_rag_falls_back_when_rerank_is_not_json(self):
        llm = fake_llm("검색어 아님", "또 아님", "점수 아님", "또 아님", "답")  # 형식 오류면 한 번 더 묻는다
        _, steps, sources = collect(run_advanced_rag("질문", ctx(llm)))
        self.assertEqual(steps["① Query Rewrite"]["queries"], ["질문"])
        self.assertIn("③ Re-ranking 실패 → RRF 순서 사용", steps)
        self.assertEqual(len(sources), 2)

    def test_advanced_rag_retries_and_extracts_json_from_prose(self):
        llm = fake_llm("검색어입니다", '검색어: ["계약 부활"]', '점수는 {"1": 3, "2": 0, "3": 0} 입니다', "답")
        _, steps, sources = collect(run_advanced_rag("질문", ctx(llm)))
        self.assertEqual(steps["① Query Rewrite"]["queries"], ["질문", "계약 부활"])
        self.assertEqual(len(sources), 1)


class ReplayTests(unittest.TestCase):
    def runs(self):
        return json.loads(RECORDINGS.read_text(encoding="utf-8"))["runs"]

    def test_every_example_question_has_a_successful_recording(self):
        runs = self.runs()
        for stage in RUN_STAGES:
            for question in STAGES[stage]["examples"]:
                with self.subTest(stage=stage, question=question):
                    record = runs[recording_key(stage, question)]
                    self.assertTrue("".join(e["text"] for e in record["events"] if e["type"] == "token").strip())
                    self.assertTrue(any(e["type"] == "metrics" for e in record["events"]))
            self.assertIn(recording_key(stage, COMMON_QUESTION), runs, "비교 화면용 공통 질문")

    def test_replay_matches_recording_and_unknown_question_fails(self):
        record = self.runs()[recording_key(1, COMMON_QUESTION)]
        recorded = "".join(e["text"] for e in record["events"] if e["type"] == "token")
        self.assertEqual("".join(e["text"] for e in run_replay(1, COMMON_QUESTION, delay=0) if e["type"] == "token"), recorded)
        with self.assertRaises(LookupError):
            list(run_replay(1, "녹화하지 않은 질문", delay=0))


if __name__ == "__main__":
    unittest.main()
