"""RAGaaS mock and internal request shape, without a network call."""

import ast
import importlib
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class RagProviderTests(unittest.TestCase):
    def setUp(self):
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda: None
        requests = types.ModuleType("requests")
        self.calls = []

        class Response:
            def raise_for_status(self):
                pass

        def post(url, **kwargs):
            self.calls.append((url, kwargs))
            return Response()

        requests.post = post
        modules = patch.dict(sys.modules, {"dotenv": dotenv, "requests": requests})
        modules.start()
        self.addCleanup(modules.stop)

        import config.ragaas

        self.ragaas = importlib.reload(config.ragaas)

    def test_mock_search_uses_no_network_and_marks_its_content(self):
        with patch.dict(os.environ, {"RAG_PROVIDER": "mock"}, clear=True):
            response = self.ragaas.post_ragaas(
                "retrieve-rrf", {"query_text": "보장 범위"}
            )
            self.assertEqual(response.status_code, 200)
            content = response.json()["hits"]["hits"][0]["_source"]["merge_title_content"]
            self.assertIn("[MOCK RAGaaS]", content)
            self.assertIn("보장 범위", content)
            self.assertEqual(self.calls, [])

    def test_internal_request_includes_both_auth_headers(self):
        values = {
            "RAG_PROVIDER": "samsung",
            "search_url": "https://internal.example.invalid/",
            "rag_credential_key": "test-ticket",
            "rag_api_key": "test-api-key",
        }
        with patch.dict(os.environ, values, clear=True):
            self.ragaas.post_ragaas("retrieve-rrf", {"query_text": "test"})
        url, options = self.calls[0]
        self.assertEqual(
            url, "https://internal.example.invalid/dsllmrag/elastic/v2/retrieve-rrf"
        )
        self.assertEqual(options["headers"]["x-dep-ticket"], "test-ticket")
        self.assertEqual(options["headers"]["api-key"], "test-api-key")
        self.assertEqual(options["timeout"], 30)

    def test_internal_missing_settings_fail_before_network(self):
        with patch.dict(os.environ, {"RAG_PROVIDER": "samsung"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "search_url"):
                self.ragaas.post_ragaas("retrieve-rrf", {"query_text": "test"})
        self.assertEqual(self.calls, [])

    def test_capstone_search_marks_mock_and_rejects_missing_internal_index(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "src/solution/Chapter02/06-capstone/solution.py"
        )
        tree = ast.parse(source.read_text())
        function = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "rag_search"
        )
        function.decorator_list = []
        namespace = {"os": os, "post_ragaas": self.ragaas.post_ragaas}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), namespace)

        with patch.dict(os.environ, {"RAG_PROVIDER": "mock"}, clear=True):
            result = namespace["rag_search"]("AI Agent")
            self.assertIn("[MOCK RAGaaS]", result)
        with patch.dict(os.environ, {"RAG_PROVIDER": "samsung"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "index_name"):
                namespace["rag_search"]("AI Agent")


if __name__ == "__main__":
    unittest.main()
