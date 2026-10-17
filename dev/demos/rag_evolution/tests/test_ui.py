"""실제 앱 화면을 API 없이(녹화 재생) 확인한다: 페이지·예시 질문·비교·설정 유지·기록 분리."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from lesson import COMMON_QUESTION, MEMORY_ASK, MEMORY_TELL, RUN_STAGES, STAGES

SLUGS = {n: lesson["slug"] for n, lesson in STAGES.items()}


class AppUiTests(unittest.TestCase):
    def new_app(self):
        app = AppTest.from_file(str(APP / "app.py"), default_timeout=30)
        app.session_state["mode"] = "녹화 재생"
        app.run()
        self.assert_no_crash(app)
        return app

    def assert_no_crash(self, app):
        self.assertFalse(app.exception, [exc.message for exc in app.exception])

    def open_page(self, app, stage):
        app.switch_page(f"app_pages/{SLUGS[stage]}.py").run()
        self.assert_no_crash(app)

    def ask_example(self, app, stage, question=COMMON_QUESTION):
        with patch("backend.time.sleep"):
            app.pills(key=f"examples_{stage}").set_value(question).run()
        self.assert_no_crash(app)
        return app.session_state["runs"][-1]

    def test_overview_and_every_stage_replays_the_common_question(self):
        app = self.new_app()
        self.assertTrue(app.title)
        for stage in RUN_STAGES:
            with self.subTest(stage=stage):
                self.open_page(app, stage)
                run = self.ask_example(app, stage)
                self.assertEqual((run["stage"], run["question"]), (stage, COMMON_QUESTION))
                self.assertTrue(run["answer"])
                if stage >= 4:
                    self.assertTrue(run["sources"], "4단계부터 보험 PDF 근거를 남긴다")
                self.assertNotIn("error", run)
                self.assertIsNone(app.pills(key=f"examples_{stage}").value)
                self.assertEqual(len(app.chat_message), 2)
        self.open_page(app, 9)
        self.assertEqual(len(app.dataframe[0].value), 8)

    def test_compare_page_runs_missing_stages_at_once(self):
        app = self.new_app()
        self.open_page(app, 9)
        with patch("backend.time.sleep"):
            [b for b in app.button if "한 번에" in b.label][0].click().run()
        self.assert_no_crash(app)
        self.assertEqual(sorted(run["stage"] for run in app.session_state["runs"]), list(RUN_STAGES))
        self.assertEqual(len(app.dataframe[0].value), 8)
        self.open_page(app, 1)
        self.assertFalse(app.chat_message, "비교 화면에서 실행한 것은 단계 대화에 섞이지 않는다")
        self.open_page(app, 9)
        self.assertEqual(len(app.dataframe[0].value), 8, "다른 페이지에 다녀와도 비교 결과는 남는다")

    def test_unrecorded_question_warns_instead_of_failing_silently(self):
        app = self.new_app()
        self.open_page(app, 1)
        with patch("ui.run_replay", side_effect=LookupError("녹화된 결과가 없는 질문입니다.")):
            run = self.ask_example(app, 1)
        self.assertEqual(run["error"], "녹화 없음")
        self.assertTrue(app.warning)

    def test_memory_example_and_clear_chat(self):
        app = self.new_app()
        self.open_page(app, 3)
        self.ask_example(app, 3, MEMORY_TELL)
        run = self.ask_example(app, 3, MEMORY_ASK)
        self.assertIn("콩", run["answer"], "3단계는 녹화에서도 강아지 이름을 기억한다")
        self.assertEqual(len(app.chat_message), 4)
        app.button(key="clear_3").click().run()
        self.assertFalse(app.chat_message)

    def test_settings_persist_across_pages_and_history_is_per_connection(self):
        app = self.new_app()
        self.open_page(app, 1)
        self.ask_example(app, 1)
        self.assertEqual(len(app.chat_message), 2)
        app.session_state["mode"] = "OpenAI 실행"
        app.run()
        self.assertFalse(app.chat_message, "연결이 바뀌면 다른 대화 기록을 보여 준다")
        self.open_page(app, 6)
        app.slider(key="top_k").set_value(5).run()
        self.open_page(app, 7)
        self.assertEqual(app.slider(key="top_k").value, 5)
        app.session_state["mode"] = "녹화 재생"
        app.run()
        self.open_page(app, 1)
        self.assertEqual(len(app.chat_message), 2)
        self.assertFalse(self.new_app().session_state["runs"])

    def test_photo_is_shown_once_with_attribution(self):
        app = self.new_app()
        self.open_page(app, 4)
        photo = {"image_url": "https://example.org/cat.jpg", "source_url": "https://example.org/cat",
                 "author": "테스트 저작자", "license": "CC BY", "license_url": "https://example.org/license"}
        events = [{"type": "photo", "data": photo},
                  {"type": "token", "text": "고양이 설명\n![고양이](https://example.org/cat.jpg)"}]
        with patch("ui.run_replay", return_value=iter(events)):
            run = self.ask_example(app, 4)
        self.assertEqual(run["photos"], [photo])
        self.assertNotIn("![", run["answer"])
        self.assertEqual(len(app.get("image")), 1)
        self.assertTrue(any("테스트 저작자" in caption.value for caption in app.caption))

    def test_review_format_failure_is_shown_as_error(self):
        app = self.new_app()
        self.open_page(app, 8)
        events = [{"type": "token", "text": "초안"},
                  {"type": "review", "data": {"status": "error", "feedback": "형식 오류", "rewrites": 0}}]
        with patch("ui.run_replay", return_value=iter(events)):
            run = self.ask_example(app, 8)
        self.assertEqual(run["error"], "검토 응답 형식 오류")
        self.assertTrue(app.error)


if __name__ == "__main__":
    unittest.main()
