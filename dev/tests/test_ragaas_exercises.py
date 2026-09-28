"""Run the M1 RAGaaS exercise and solution in mock mode."""

import contextlib
import io
import os
import runpy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


class FakeChain:
    def __or__(self, _other):
        return self

    def stream(self, inputs):
        yield inputs["context"]


class FakeLoader:
    def __init__(self, _path):
        pass

    def load(self):
        return [types.SimpleNamespace(page_content="모의 PDF 본문")]


class RagExercisesTests(unittest.TestCase):
    def test_student_and_solution_use_mock_without_network(self):
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda: None
        llm = types.ModuleType("config.llm")
        llm.get_llm = FakeChain
        requests = types.ModuleType("requests")
        requests.post = lambda *_args, **_kwargs: self.fail("network request attempted")

        community = types.ModuleType("langchain_community")
        community.__path__ = []
        loaders = types.ModuleType("langchain_community.document_loaders")
        loaders.PDFMinerLoader = FakeLoader

        core = types.ModuleType("langchain_core")
        core.__path__ = []
        parsers = types.ModuleType("langchain_core.output_parsers")
        parsers.StrOutputParser = FakeChain
        prompts = types.ModuleType("langchain_core.prompts")
        prompts.ChatPromptTemplate = types.SimpleNamespace(
            from_messages=lambda _messages: FakeChain()
        )

        modules = {
            "dotenv": dotenv,
            "config.llm": llm,
            "requests": requests,
            "langchain_community": community,
            "langchain_community.document_loaders": loaders,
            "langchain_core": core,
            "langchain_core.output_parsers": parsers,
            "langchain_core.prompts": prompts,
        }
        for prefix in ("src/raw/Chapter01", "src/solution/Chapter01"):
            with self.subTest(prefix=prefix):
                output = io.StringIO()
                with patch.dict(sys.modules, modules), patch.dict(
                    os.environ, {"RAG_PROVIDER": "mock"}, clear=True
                ), contextlib.redirect_stdout(output):
                    runpy.run_path(
                        str(ROOT / prefix / "03-rag/05_ragaas.py"),
                        run_name="__main__",
                    )
                self.assertIn("RAGaaS 모드: mock", output.getvalue())
                self.assertIn("[MOCK RAGaaS]", output.getvalue())


if __name__ == "__main__":
    unittest.main()
