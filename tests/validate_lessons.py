"""의미 번호·첨부·출력·시간 배정과 새 커널 실행을 확인한다."""

import argparse
import re
import sys
from pathlib import Path

import nbformat
from jupyter_client.manager import KernelManager
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="외부 API 없는 기본 모드를 새 커널에서 실행")
    parser.add_argument("--companions", action="store_true", help="courseware의 동반 노트북도 검사")
    args = parser.parse_args()
    timing = (ROOT / "docs/INSTRUCTOR_TIMING.md").read_text()
    allocations = re.findall(r"^\| (\d+\.\d+\.\d+) \| (\d+)분", timing, re.M)
    expected = {section for section, _ in allocations}
    assert len(expected) == 63
    for day in range(1, 5):
        assert sum(int(minutes) for section, minutes in allocations if section.startswith(f"{day}.")) == 480
    paths = sorted((ROOT / "lessons").glob("day[0-9][0-9].ipynb"))
    assert len(paths) == 4
    seen = set()
    if args.companions:
        paths += sorted((ROOT / "src/courseware").glob("*.ipynb"))
    for index, path in enumerate(paths, 1):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        sections = notebook.metadata.course.get("sections", [])
        seen.update(sections)
        for cell in notebook.cells:
            if cell.cell_type == "code":
                assert not cell.outputs and cell.execution_count is None, f"저장된 출력: {path} {cell.id}"
            if cell.cell_type == "markdown":
                for name in re.findall(r"attachment:([^\s)]+)", cell.source):
                    assert name in cell.get("attachments", {}), f"첨부 누락: {path} {name}"
                if cell.get("attachments"):
                    assert all(label in cell.source for label in ["그림 ", "보면서 확인:", "표현 범위:"])
                    assert (ROOT / cell.metadata.asset_source).is_file()
                if sections:
                    assert not re.search(r"(?<![\d.])\d+\s*분(?:\s|[~～–-]|$)", cell.source), f"학습자 시간 표시: {path}"
        if sections:
            headings = re.findall(r"^### (\d+\.\d+\.\d+) ", "\n".join(c.source for c in notebook.cells), re.M)
            assert headings == sections
        if args.execute:
            manager = KernelManager()
            # venv Python의 symlink를 resolve하면 base Python으로 바뀌므로 유지한다.
            manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
            try:
                NotebookClient(notebook, km=manager, timeout=120,
                               resources={"metadata": {"path": str(path.parent)}}).execute()
            finally:
                if manager.has_kernel:
                    manager.shutdown_kernel(now=True)
            output = ROOT / "docs/_build" / ("courseware" if path.parent.name == "courseware" else "lessons")
            output.mkdir(parents=True, exist_ok=True)
            nbformat.write(notebook, output / path.name)
            html, _ = HTMLExporter().from_notebook_node(notebook)
            (output / f"{path.stem}.html").write_text(html, encoding="utf-8")
        print(f"✔ [{index}/{len(paths)}] {path.relative_to(ROOT)} — 검증 완료", flush=True)
    assert seen == expected, f"의미 번호 불일치: {seen ^ expected}"
    print("✔ 63개 의미 번호 · 13개 블록 · 일차별 480분 검산 완료")


if __name__ == "__main__":
    main()
