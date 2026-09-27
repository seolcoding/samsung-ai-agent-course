"""PDF 또는 PPTX의 페이지를 이미지로 바꿔 슬라이드 묶음(JSON) 한 파일로 만든다.

노트북에서는 assets.widgets.show_slides(묶음 이름, pages=[...])로 필요한 쪽만 꺼내 보여 준다.

사용법 (프로젝트 루트에서):
    uv run python lessons/assets/build_slide_deck.py <입력.pdf|입력.pptx> lessons/assets/slides/<이름>.json

필요한 도구: pdftoppm (poppler), PPTX라면 soffice (LibreOffice)
"""

import base64
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def fail(what, why, fix):
    print(f"✖ {what} | {why} | {fix}")
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        fail("인자 오류", "입력과 출력 경로가 필요함", "사용법은 파일 맨 위 설명 참고")
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    if not src.exists():
        fail("입력 파일 없음", str(src), "경로 확인")
    if shutil.which("pdftoppm") is None:
        fail("pdftoppm 없음", "poppler 미설치", "brew install poppler")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pdf = src
        if src.suffix.lower() == ".pptx":
            if shutil.which("soffice") is None:
                fail("soffice 없음", "LibreOffice 미설치", "brew install --cask libreoffice")
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(src)],
                           check=True, capture_output=True)
            pdf = tmp / (src.stem + ".pdf")
        print(f"✔ [1/3] PDF 준비: {pdf.name}")

        subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=80", "-scale-to", "1280",
                        str(pdf), str(tmp / "page")], check=True)
        pages = sorted(tmp.glob("page-*.jpg"), key=lambda p: int(re.findall(r"\d+", p.stem)[-1]))
        images = ["data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode() for p in pages]
        print(f"✔ [2/3] 페이지 이미지 {len(images)}장 변환")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"source": src.name, "images": images}), encoding="utf-8")
    print(f"✔ [3/3] 저장: {out} ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
