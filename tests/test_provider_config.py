"""Provider selection checks that do not call external APIs."""

import importlib
import os
import sys
import types
import unittest
from unittest.mock import patch


class CaptureClient:
    def __init__(self, **kwargs):
        self.options = kwargs


class ProviderConfigTests(unittest.TestCase):
    def setUp(self):
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda: None

        langchain_openai = types.ModuleType("langchain_openai")
        langchain_openai.ChatOpenAI = CaptureClient
        langchain_openai.OpenAIEmbeddings = CaptureClient

        langchain_core = types.ModuleType("langchain_core")
        langchain_core.__path__ = []
        embeddings = types.ModuleType("langchain_core.embeddings")
        embeddings.Embeddings = type("Embeddings", (), {})

        self.module_patch = patch.dict(
            sys.modules,
            {
                "dotenv": dotenv,
                "langchain_openai": langchain_openai,
                "langchain_core": langchain_core,
                "langchain_core.embeddings": embeddings,
            },
        )
        self.module_patch.start()
        self.addCleanup(self.module_patch.stop)

        import config.llm
        import config.embeddings

        self.llm = importlib.reload(config.llm)
        self.embeddings = importlib.reload(config.embeddings)

    def test_external_clients_use_selected_models_and_preserve_key(self):
        values = {
            "LLM_PROVIDER": "openai",
            "EMBED_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "test-chat-model",
            "OPENAI_EMBEDDING_MODEL": "test-embedding-model",
        }
        with patch.dict(os.environ, values, clear=True):
            llm = self.llm.get_llm()
            embedder = self.embeddings.get_embeddings()
            self.assertEqual(llm.options["model"], "test-chat-model")
            self.assertEqual(llm.options["api_key"], "test-key")
            self.assertEqual(embedder.options["model"], "test-embedding-model")
            self.assertEqual(os.environ["OPENAI_API_KEY"], "test-key")

    def test_internal_client_uses_gateway_settings_without_changing_openai_key(self):
        values = {
            "LLM_PROVIDER": "samsung",
            "model": "test-internal-model",
            "api_base_url": "https://internal.example.invalid",
            "credential_key": "test-ticket",
            "send_system_name": "test-system",
            "user_id": "test-user",
            "OPENAI_API_KEY": "existing-key",
        }
        with patch.dict(os.environ, values, clear=True):
            llm = self.llm.get_llm()
            self.assertEqual(llm.options["model"], "test-internal-model")
            self.assertEqual(llm.options["base_url"], values["api_base_url"])
            self.assertEqual(llm.options["default_headers"]["x-dep-ticket"], "test-ticket")
            self.assertEqual(os.environ["OPENAI_API_KEY"], "existing-key")

    def test_luna_supports_chat_completions_tool_calls(self):
        values = {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "gpt-6-luna",
        }
        with patch.dict(os.environ, values, clear=True):
            llm = self.llm.get_llm()
            self.assertEqual(llm.options["reasoning_effort"], "none")
            self.assertIs(llm.options["use_responses_api"], False)
            overridden = self.llm.get_llm(reasoning_effort="low")
            self.assertEqual(overridden.options["reasoning_effort"], "low")

    def test_missing_or_unknown_provider_settings_fail_clearly(self):
        with patch.dict(os.environ, {"LLM_PROVIDER": "openai"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_MODEL"):
                self.llm.get_llm()
        with patch.dict(os.environ, {"LLM_PROVIDER": "unknown"}, clear=True):
            with self.assertRaisesRegex(ValueError, "LLM_PROVIDER"):
                self.llm.get_llm()
        with patch.dict(os.environ, {"EMBED_PROVIDER": "openai"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
                self.embeddings.get_embeddings()


if __name__ == "__main__":
    unittest.main()
