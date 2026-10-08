"""Keep text I/O identical on macOS (UTF-8) and Korean Windows (cp949 default)."""

import ast
import builtins
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def open_as_cp949(real_open):
    """Make text-mode open() without an encoding behave like Korean Windows."""

    def wrapper(file, mode="r", buffering=-1, encoding=None, *args, **kwargs):
        if "b" not in mode and encoding is None:
            encoding = "cp949"
        return real_open(file, mode, buffering, encoding, *args, **kwargs)

    return wrapper


def calls_without_encoding(tree):
    """Return (line, name) of text-mode open/read_text/write_text/TextLoader calls with no encoding."""
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute):
            name = node.func.attr if node.func.attr in ("read_text", "write_text") else None
        else:
            name = getattr(node.func, "id", None) if getattr(node.func, "id", None) in ("open", "TextLoader") else None
        if name is None or any(keyword.arg == "encoding" for keyword in node.keywords):
            continue
        mode = None
        if name == "open" and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
            mode = node.args[1].value
        for keyword in node.keywords:
            if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
                mode = keyword.value.value
        if mode and "b" in str(mode):
            continue
        found.append((node.lineno, name))
    return found


def notebook_code(path):
    """Yield (cell index, source) of code cells with IPython magics removed."""
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "code":
            continue
        lines = "".join(cell["source"]).splitlines()
        if lines and lines[0].startswith("%%"):
            lines = lines[1:]
        yield index, "\n".join(line for line in lines if not line.lstrip().startswith(("%", "!")))


def load_widgets(chapter):
    path = ROOT / "course" / chapter / "assets" / "widgets.py"
    spec = importlib.util.spec_from_file_location(f"widgets_{chapter}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_config_with(settings_bytes):
    """Import config in a folder whose settings file was saved as the given bytes."""
    with tempfile.TemporaryDirectory() as folder:
        Path(folder, ".env").write_bytes(settings_bytes)
        env = {key: value for key, value in os.environ.items() if key != "FIRST"}
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            [sys.executable, "-c", "import os, config; print(os.environ.get('FIRST'))"],
            cwd=folder, env=env, capture_output=True, check=False,
        )


class EncodingTests(unittest.TestCase):
    def test_text_files_are_opened_as_utf8(self):
        problems = []
        sources = sorted(ROOT.glob("course/**/*.py")) + sorted((ROOT / "dev/tests").glob("*.py"))
        for path in sources:
            if "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            problems += [f"{path.relative_to(ROOT)}:{line} {name}" for line, name in calls_without_encoding(tree)]
        for path in sorted(ROOT.glob("course/Chapter*/notebooks/*.ipynb")):
            for index, source in notebook_code(path):
                try:
                    tree = ast.parse(source)
                except SyntaxError:
                    continue
                problems += [f"{path.name} cell {index} {name}" for _, name in calls_without_encoding(tree)]
        self.assertEqual(problems, [], "pass encoding='utf-8': Korean Windows defaults to cp949")

    def test_show_quiz_reads_every_quiz_as_utf8_when_default_is_cp949(self):
        for chapter in ("Chapter01", "Chapter02"):
            widgets = load_widgets(chapter)
            for path in sorted((ROOT / "course" / chapter / "assets" / "quizzes").rglob("*.json")):
                if not isinstance(json.loads(path.read_text(encoding="utf-8")), list):
                    continue  # ordering quizzes are read by show_order_quiz
                with self.subTest(quiz=path.relative_to(ROOT).as_posix()):
                    with patch("builtins.open", open_as_cp949(builtins.open)), contextlib.redirect_stdout(io.StringIO()):
                        widgets.show_quiz(str(path))

    def test_config_check_prints_emoji_when_stdout_is_cp949(self):
        env = {**os.environ, "PYTHONIOENCODING": "cp949"}
        result = subprocess.run(
            [sys.executable, "-m", "config.check", "--json"], cwd=ROOT, env=env, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        self.assertIn("items", json.loads(result.stdout.decode("utf-8")))

    def test_config_reads_settings_saved_by_other_editors(self):
        body = "# 한글 설명\nFIRST=alpha\n"
        saved_as = {
            "utf-8": body.encode("utf-8"),
            "utf-8 with BOM": b"\xef\xbb\xbf" + body.encode("utf-8"),
            "cp949 (old Notepad)": body.encode("cp949"),
        }
        for name, data in saved_as.items():
            with self.subTest(saved_as=name):
                result = import_config_with(data)
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
                self.assertEqual(result.stdout.decode("utf-8").strip(), "alpha")

    def test_config_explains_settings_it_cannot_read(self):
        result = import_config_with(b"\xff\xfe" + "FIRST=alpha\n".encode("utf-16-le"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("UTF-8로 저장", result.stderr.decode("utf-8", "replace"))

    def test_check_notices_settings_not_saved_as_plain_utf8(self):
        from config.check import _env_encoding

        saved_as = {
            "utf-8": "한글".encode("utf-8"),
            "utf-8-bom": b"\xef\xbb\xbf" + "한글".encode("utf-8"),
            "other": "한글".encode("cp949"),
        }
        with tempfile.TemporaryDirectory() as folder:
            for expected, data in saved_as.items():
                path = Path(folder, expected)
                path.write_bytes(data)
                self.assertEqual(_env_encoding(path), expected)

    @unittest.skipUnless(shutil.which("git"), "needs git to list the tracked files")
    def test_tracked_env_files_are_plain_ascii(self):
        """Comments in .env files are English, so an ANSI or UTF-8 save gives the same bytes."""
        listing = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
        names = [name for name in listing.decode("utf-8").split("\0") if name and Path(name).name.startswith(".env")]
        self.assertIn(".env.sample", names)
        for name in names:
            with self.subTest(file=name):
                self.assertTrue((ROOT / name).read_bytes().isascii(), "write .env comments in English (ASCII only)")


if __name__ == "__main__":
    unittest.main()
