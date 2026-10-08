"""The .env.sample template must document every value the code needs, in a form tools can read."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSIGNMENT = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=")
COMMENTED_ASSIGNMENT = re.compile(r"^#\s*([A-Za-z_][A-Za-z0-9_]*)=")
OPTIONAL = {"LLM_PROVIDER", "EMBED_PROVIDER", "RAG_PROVIDER"}


class EnvSampleTests(unittest.TestCase):
    def setUp(self):
        self.lines = (ROOT / ".env.sample").read_text(encoding="utf-8").splitlines()

    def test_every_value_has_a_comment_line_right_above(self):
        for number, line in enumerate(self.lines):
            match = ASSIGNMENT.match(line)
            if match:
                with self.subTest(name=match.group(1)):
                    self.assertTrue(
                        number > 0 and self.lines[number - 1].startswith("#"),
                        "explain the value in a comment right above it",
                    )

    def test_no_comment_follows_an_empty_value(self):
        # "KEY=   # note" is read as the value "# note"
        for line in self.lines:
            with self.subTest(line=line[:40]):
                self.assertIsNone(re.match(r"^[A-Za-z_][A-Za-z0-9_]*=\s+#", line))

    def test_only_the_provider_overrides_are_commented_out_assignments(self):
        # Tools treat "# KEY=value" as an optional setting, so prose must not start that way.
        names = {match.group(1) for line in self.lines if (match := COMMENTED_ASSIGNMENT.match(line))}
        self.assertEqual(names, OPTIONAL)

    def test_every_name_the_check_requires_is_in_the_sample(self):
        from config.check import REQUIRED

        required = {name for kinds in REQUIRED.values() for names in kinds.values() for name in names}
        present = {match.group(1) for line in self.lines if (match := ASSIGNMENT.match(line))}
        self.assertEqual(sorted(required - present), [])


if __name__ == "__main__":
    unittest.main()
