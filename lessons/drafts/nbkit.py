"""강의·실습 노트북 빌더가 함께 쓰는 셀 조립 도구.

- 제목은 노트북 안에서 1부터 번호를 매긴다. 제목 옆에 (슬라이드) (퀴즈) (코드) (실습) 표시를 작게 붙이고,
  맨 위에 같은 표시를 단 목차를 만든다(finish에서 셀 종류를 보고 자동으로 계산).
- 교안 도구를 부르는 코드 셀은 입력 칸을 접는다(source_hidden). 수강생이 직접 쓰는 셀만 보인다.
- 강사용 메모는 절마다 한 상자로 모아 접어 둔다.
- 수강생 글에는 "(p6)" 같은 쪽 인용을 넣지 않는다. 퀴즈는 4지선다·정답 1개이고 문제는 파일로 둔다.
"""

import json
import re
from pathlib import Path

import nbformat as nbf

TAG_ORDER = ["슬라이드", "퀴즈", "코드", "실습"]


def tags_of(cell):
    """셀 하나가 어떤 종류인지 돌려준다(목차·제목 옆 표시용)."""
    src = cell.source
    if cell.cell_type == "code":
        if "show_slides(" in src:
            return {"슬라이드"}
        if "show_quiz(" in src or "show_order_quiz(" in src:
            return {"퀴즈"}
        if not cell.metadata.get("jupyter", {}).get("source_hidden"):  # 수강생에게 보이는 셀
            if "✍" in src:
                return {"실습"}  # 빈칸을 채우는 셀
            return {"퀴즈"} if "예측" in src else {"코드"}
        if any(k in src for k in ("show_checklist(", "show_criteria(", "slide_setup(", "make_blank(")):
            return set()
        return {"코드"}
    return {"실습"} if "**CodeMate에게 줄 힌트**" in src or "**성공 기준**" in src else set()


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

    def code(self, src, visible=False):
        cell = nbf.v4.new_code_cell(src.strip())
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
        nb = nbf.v4.new_notebook(cells=cells)
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        nbf.write(nb, out)
        print(f"✔ {out} ({len(cells)}셀)")
