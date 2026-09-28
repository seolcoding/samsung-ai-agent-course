"""강의·실습 노트북 빌더가 함께 쓰는 셀 조립 도구.

- 제목은 노트북 안에서 1부터 번호를 매긴다. 제목 옆에 (슬라이드) (퀴즈) (코드) (예제) (과제) 표시를 작게 붙이고,
  맨 위에 같은 표시를 단 목차를 만든다(finish에서 셀 종류를 보고 자동으로 계산).
- 교안 도구를 부르는 코드 셀은 입력 칸을 접는다(source_hidden). 수강생이 직접 쓰는 셀만 보인다.
- 강사용 메모는 절마다 한 상자로 모아 접어 둔다. 수강생본에서는 빼고 강사본(dev/instructor/)에만 둔다.
- 코드 셀은 ruff format(한 줄 88자, 큰따옴표)으로 정돈해 읽기 쉽게 한다. 문법 오류인 셀은 그대로 둔다.
- 수강생 글에는 "(p6)" 같은 쪽 인용을 넣지 않는다. 퀴즈는 4지선다·정답 1개이고 문제는 파일로 둔다.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import nbformat as nbf

TAG_ORDER = ["슬라이드", "퀴즈", "코드", "예제", "과제"]


def tags_of(cell):
    """셀 하나가 어떤 종류인지 돌려준다(목차·제목 옆 표시용)."""
    src = cell.source
    if "lab_kind" in cell.metadata:  # 실습 노트북: 빌더가 정한 종류(예제·과제, 준비 코드는 빈 값)
        kind = cell.metadata["lab_kind"]
        return {kind} if kind else set()
    if cell.cell_type == "code":
        if "show_slides(" in src:
            return {"슬라이드"}
        if "show_quiz(" in src or "show_order_quiz(" in src:
            return {"퀴즈"}
        if not cell.metadata.get("jupyter", {}).get("source_hidden"):  # 수강생에게 보이는 셀
            if "✍" in src:
                return {"과제"}  # 빈칸을 채우는 셀
            return {"퀴즈"} if "예측" in src else {"코드"}
        if any(k in src for k in ("show_checklist(", "show_criteria(", "slide_setup(", "make_blank(")):
            return set()
        return {"코드"}
    return set()


def fmt(src):
    """코드를 ruff format으로 정돈한다. ruff가 없으면 멈추고, 문법 오류인 코드는 그대로 돌려준다."""
    ruff = shutil.which("ruff")
    if ruff is None:
        raise SystemExit("✖ 코드 정돈 실패 | ruff가 없음 | `brew install ruff` 또는 `uv tool install ruff`로 설치한다")
    done = subprocess.run([ruff, "format", "--line-length", "88", "-"], input=src, capture_output=True, text=True)
    return done.stdout.rstrip("\n") if done.returncode == 0 else src


QUIET_CALLS = {"load_dotenv", "add_edge", "add_node", "add_conditional_edges", "set_entry_point"}


def quiet(src):
    """셀 마지막 줄이 값을 돌려주는 준비 호출(load_dotenv(), add_edge(...) 등)이면 끝에 ;를 붙여
    `True`, `<StateGraph ...>` 같은 쓸모없는 출력을 숨긴다."""
    import ast

    try:
        last = ast.parse(src).body[-1]
    except (SyntaxError, IndexError):
        return src
    if isinstance(last, ast.Expr) and isinstance(last.value, ast.Call):
        f = last.value.func
        if (getattr(f, "attr", None) or getattr(f, "id", None)) in QUIET_CALLS:
            lines = src.split("\n")
            k = last.end_lineno - 1
            lines[k] = lines[k].rstrip() + ";"
            return "\n".join(lines)
    return src


class Notebook:
    def __init__(self, quiz_dir, quiz_ref):
        self.cells, self.pending = [], []
        self.quiz_dir, self.quiz_ref = Path(quiz_dir), quiz_ref  # 파일 위치와 노트북에서 부를 상대 경로

    def flush(self):
        if self.pending:
            body = "\n\n---\n\n".join(self.pending)
            cell = nbf.v4.new_markdown_cell("<details><summary>강사용 메모</summary>\n\n" + body + "\n\n</details>")
            cell.metadata["tags"] = ["강사용"]
            self.cells.append(cell)
            self.pending.clear()

    def md(self, src):
        assert not re.search(r"\(p\d+", src), f"수강생 글에 쪽 인용이 남아 있다: {src[:60]!r}"
        if re.match(r"#{1,3} ", src.lstrip()):  # 새 절이 시작되면 앞 절의 강사용 메모를 먼저 내보낸다
            self.flush()
        self.cells.append(nbf.v4.new_markdown_cell(src.strip()))

    def code(self, src, visible=False, kind=None):
        cell = nbf.v4.new_code_cell(src.strip())
        if kind is not None:  # 실습 노트북의 셀 종류(예제·과제, 준비 코드는 "")
            cell.metadata["lab_kind"] = kind
        if not visible:
            cell.metadata["jupyter"] = {"source_hidden": True}
            cell.metadata["tags"] = ["교안도구"]
        self.cells.append(cell)

    def meta(self, src):
        if src:
            self.pending.append(src.strip())

    def h(self, level, title):
        self.md("#" * level + " " + title)
        self.cells[-1].metadata["heading"] = {"level": level, "title": title}

    def quiz_file(self, name, questions):
        for q in questions:  # 퀴즈 선택지는 항상 4개, 정답은 1개, 쪽 인용 없음
            assert len(q["answers"]) == 4, f"{name}: 선택지가 {len(q['answers'])}개"
            assert sum(a["correct"] for a in q["answers"]) == 1, f"{name}: 정답이 1개가 아님"
            assert "(p" not in json.dumps(q, ensure_ascii=False), f"{name}: 퀴즈에 쪽 인용이 남아 있다"
        self.quiz_dir.mkdir(parents=True, exist_ok=True)
        (self.quiz_dir / f"{name}.json").write_text(json.dumps(questions, ensure_ascii=False, indent=1), encoding="utf-8")
        self.code(f'show_quiz("{self.quiz_ref}/{name}.json")')

    def finish(self, out):
        """제목 옆 표시와 맨 위 목차를 채우고 파일로 쓴다."""
        self.flush()
        cells = self.cells
        for cell in cells:
            if cell.cell_type == "code":
                cell.source = quiet(fmt(cell.source))
        heads = [k for k, cell in enumerate(cells) if "heading" in cell.metadata]
        toc = []
        for n, k in enumerate(heads):
            level = cells[k].metadata["heading"]["level"]
            end = next((j for j in heads[n + 1:] if cells[j].metadata["heading"]["level"] <= level), len(cells))
            found = set().union(*(tags_of(cells[j]) for j in range(k + 1, end) if "강사용" not in cells[j].metadata.get("tags", [])))
            label = " ".join(f"({t})" for t in TAG_ORDER if t in found)
            title = cells[k].metadata["heading"]["title"]
            cells[k].source = "#" * level + " " + title + (f" <small>{label}</small>" if label else "")
            if level <= 3:
                toc.append("  " * (level - 2) + f"- {title}" + (f" {label}" if label else ""))
        cells.insert(1, nbf.v4.new_markdown_cell("**목차**\n\n" + "\n".join(toc)))
        out = Path(out)
        # 두 벌로 쓴다. 수강생본(course/…/notebooks/)은 강사용 메모를 빼고,
        # 강사본(dev/instructor/<챕터>/)은 메모를 두고 맨 위에서 수강생본 폴더로 옮겨 가 같은 경로로 실행한다.
        student = [c for c in cells if "강사용" not in c.metadata.get("tags", [])]
        chapter = out.parent.parent.name  # course/Chapter01/notebooks/x.ipynb → Chapter01
        root = out.parents[3]
        teacher_out = root / "dev" / "instructor" / chapter / out.name
        cd = nbf.v4.new_code_cell(f"%cd ../../../course/{chapter}/notebooks")
        cd.metadata["jupyter"] = {"source_hidden": True}
        cd.metadata["tags"] = ["교안도구", "강사본"]
        for path, body in ((out, student), (teacher_out, [cells[0], cd, *cells[1:]])):
            nb = nbf.v4.new_notebook(cells=body)
            nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
            path.parent.mkdir(parents=True, exist_ok=True)
            nbf.write(nb, path)
        print(f"✔ {out} ({len(student)}셀) + 강사본 {teacher_out.relative_to(root)} ({len(cells) + 1}셀)")
