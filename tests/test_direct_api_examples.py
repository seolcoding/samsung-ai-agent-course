"""Run the introductory API examples with fake clients and no network."""

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


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": "test answer"}}]}


class FakeStream:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        pass

    def __iter__(self):
        yield types.SimpleNamespace(type="response.output_text.delta", delta="test")


class FakeResponses:
    def create(self, **_kwargs):
        return types.SimpleNamespace(output_text="test answer", output=[])

    def stream(self, **_kwargs):
        return FakeStream()


class DirectApiExamplesTests(unittest.TestCase):
    def setUp(self):
        self.requests = types.ModuleType("requests")
        self.calls = []

        def post(url, **kwargs):
            self.calls.append((url, kwargs))
            return FakeResponse()

        self.requests.post = post

        self.openai = types.ModuleType("openai")
        self.clients = []

        def openai_client(**kwargs):
            self.clients.append(kwargs)
            return types.SimpleNamespace(responses=FakeResponses())

        self.openai.OpenAI = openai_client

        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda: None

        modules = patch.dict(
            sys.modules,
            {"requests": self.requests, "openai": self.openai, "dotenv": dotenv},
        )
        modules.start()
        self.addCleanup(modules.stop)

    def run_example(self, relative_path, values):
        with patch.dict(os.environ, values, clear=True), contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(ROOT / relative_path), run_name="__main__")

    def test_raw_request_selects_external_and_internal_endpoint(self):
        for prefix in ("src/raw/Chapter01", "src/solution/Chapter01"):
            path = f"{prefix}/01-llm-api/01_requests.py"
            self.run_example(
                path,
                {
                    "LLM_PROVIDER": "openai",
                    "OPENAI_MODEL": "test-public-model",
                    "OPENAI_API_KEY": "test-key",
                },
            )
            url, options = self.calls[-1]
            self.assertEqual(url, "https://api.openai.com/v1/chat/completions")
            self.assertEqual(options["json"]["model"], "test-public-model")
            self.assertNotIn("include_reasoning", options["json"])
            self.assertEqual(options["headers"]["Authorization"], "Bearer test-key")

            self.run_example(
                path,
                {
                    "LLM_PROVIDER": "openai",
                    "OPENAI_MODEL": "gpt-6-luna",
                    "OPENAI_API_KEY": "test-key",
                },
            )
            _, luna_options = self.calls[-1]
            self.assertNotIn("temperature", luna_options["json"])
            self.assertEqual(luna_options["json"]["reasoning_effort"], "none")

            self.run_example(
                path,
                {
                    "LLM_PROVIDER": "samsung",
                    "api_base_url": "https://internal.example.invalid/v1/",
                    "model": "test-internal-model",
                    "credential_key": "test-ticket",
                    "send_system_name": "test-system",
                    "user_id": "test-user",
                },
            )
            url, options = self.calls[-1]
            self.assertEqual(url, "https://internal.example.invalid/v1/chat/completions")
            self.assertEqual(options["json"]["model"], "test-internal-model")
            self.assertFalse(options["json"]["include_reasoning"])
            self.assertEqual(options["headers"]["x-dep-ticket"], "test-ticket")

    def test_openai_sdk_example_does_not_overwrite_key(self):
        for prefix in ("src/raw/Chapter01", "src/solution/Chapter01"):
            path = f"{prefix}/01-llm-api/02_openai.py"
            values = {
                "LLM_PROVIDER": "openai",
                "OPENAI_MODEL": "test-public-model",
                "OPENAI_API_KEY": "test-key",
            }
            with patch.dict(os.environ, values, clear=True), contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(ROOT / path), run_name="__main__")
                self.assertEqual(os.environ["OPENAI_API_KEY"], "test-key")
            self.assertEqual(self.clients[-1], {"api_key": "test-key"})


if __name__ == "__main__":
    unittest.main()
