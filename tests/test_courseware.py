"""강의에서 실패하면 안 되는 승인·근거·화면 계약. 외부 API를 호출하지 않는다."""

import unittest
from pathlib import Path
from uuid import uuid4

from langgraph.types import Command
from streamlit.testing.v1 import AppTest

from courseware.capstone import build_capstone, evaluate_report
from courseware.knowledge import answer_from_documents, retrieve


class ApprovalTests(unittest.IsolatedAsyncioTestCase):
    async def start(self, topic="RAG 검색"):
        graph = build_capstone()
        config = {"configurable": {"thread_id": str(uuid4())}}
        pending = await graph.ainvoke({"topic": topic, "trace": []}, config)
        return graph, config, pending

    async def test_approval_writes_and_evaluates(self):
        graph, config, pending = await self.start()
        self.assertTrue(pending.get("__interrupt__"))
        self.assertFalse(pending["writer_executed"])
        done = await graph.ainvoke(Command(resume={"approved": True}), config)
        self.assertTrue(done["writer_executed"])
        self.assertTrue(done["evaluation"]["citation_validity"])
        self.assertEqual(done["evaluation"]["structure"], 1)
        self.assertEqual(done["next"], "FINISH")

    async def test_rejection_never_calls_writer(self):
        graph, config, _ = await self.start()
        done = await graph.ainvoke(Command(resume={"approved": False}), config)
        self.assertFalse(done["writer_executed"])
        self.assertEqual(done["report"], "")
        self.assertNotIn("supervisor:writer", done["trace"])

    async def test_no_evidence_needs_neither_approval_nor_writer(self):
        _, _, done = await self.start("구내식당 오늘 메뉴")
        self.assertFalse(done.get("__interrupt__"))
        self.assertFalse(done["writer_executed"])
        self.assertEqual(done["evidence"], [])

    async def test_truthy_string_is_not_approval(self):
        graph, config, _ = await self.start()
        with self.assertRaises(ValueError):
            await graph.ainvoke(Command(resume={"approved": "false"}), config)
        self.assertFalse(graph.get_state(config).values["writer_executed"])

    async def test_new_threads_do_not_inherit_approval(self):
        graph, config, _ = await self.start()
        await graph.ainvoke(Command(resume={"approved": True}), config)
        other = {"configurable": {"thread_id": str(uuid4())}}
        pending = await graph.ainvoke({"topic": "MCP 도구", "trace": []}, other)
        self.assertTrue(pending.get("__interrupt__"))
        self.assertFalse(pending["writer_executed"])


class EvidenceTests(unittest.TestCase):
    def test_unrelated_question_is_not_answered(self):
        response = answer_from_documents("구내식당 메뉴")
        self.assertEqual(response["sources"], [])
        self.assertEqual(response["answer"], "문서에서 확인할 수 없습니다.")

    def test_fabricated_source_is_reported(self):
        result = evaluate_report("내용 [D1] [D999]", retrieve("RAG 검색", 1))
        self.assertFalse(result["citation_validity"])
        self.assertEqual(result["unknown_citations"], ["D999"])


class ScreenTests(unittest.TestCase):
    def test_approve_and_reject_from_widgets(self):
        source = Path(__file__).resolve().parents[1] / "src/courseware/app.py"
        for decision in (True, False):
            with self.subTest(approved=decision):
                screen = AppTest.from_file(str(source), default_timeout=30).run()
                screen.radio[0].set_value("승인 후 보고서").run()
                screen.button[0].click().run()
                self.assertTrue(screen.session_state["pending"])
                label = "승인하고 작성" if decision else "거절하고 중단"
                next(b for b in screen.button if b.label == label).click().run()
                self.assertFalse(screen.exception)
                self.assertIs(screen.session_state["result"]["writer_executed"], decision)


if __name__ == "__main__":
    unittest.main()
