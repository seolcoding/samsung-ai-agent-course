# AGENTS.md — 수업용 교안 노트북 (lessons/, v1.0, 2026-09-26)

이 폴더는 수업에서 여는 교안 노트북을 둔다. 루트 `AGENTS.md`의 규칙을 그대로 따르고, 이 문서는 노트북 제작 방식만 정한다.
작동하는 예시는 `html_embed_demo.ipynb`다. 새 방식을 쓰기 전에 이 예시로 먼저 확인한다.

## 1. 교안은 노트북으로 만든다

- 수업 교안은 이 폴더 아래 챕터 폴더(`Chapter01/`, `Chapter02/`)에 `.ipynb`로 만든다. 다른 위치에 교안 노트북을 만들지 않는다.
- 한 권은 강의 노트북 `<번호>_<이름>_LEC.ipynb`(슬라이드·설명·퀴즈, 실습 코드 없음)와 실습 노트북 `<번호>_<이름>_LAB.ipynb`(`lessons/drafts/build_lab.py`가 `lessons/drafts/labs/<폴더>.json`과 원본 코드로 조립. 원본 코드를 셀로 넣는다: 첫 구획은 접힌 준비 셀, 나머지는 보이는 코드 셀. 수강생은 노트북만 받으므로 `.py`·경로·다른 노트북을 언급하지 않는다)로 나눈다. 번호는 원본 PDF 번호를 따른다(예: `Chapter01/1-2_llm_api_LEC.ipynb`, `Chapter01/1-2_llm_api_LAB.ipynb`. 제목도 `# [LEC] …`, `# [LAB] …`으로 시작한다). 설명 수준은 C(슬라이드 요약 + 내용 있는 곳만 "왜 배우나")로 확정했다(2026-09-28). 강의 본문에 "실습 노트북에서 확인" 같은 안내를 되풀이하지 않는다.
- 실습 노트북의 구획은 두 종류다(2026-09-28 결정). 제목 옆에 `(예제)`·`(과제)`를 작게 표시하고(`(실습)` 표시는 쓰지 않는다), 코드 안에는 주석으로 표시한다. 원본 코드의 들여쓰기는 그대로 두고, 표시 주석은 해당 줄 바로 위에 같은 들여쓰기로 넣는다.
  - **예제**: 완성된 코드를 함께 실행한다. 바꿔 볼 값이 있는 줄 바로 위에 `# ✍️ CHANGE_HERE: …` 주석을 넣고, 바꿔 다시 실행한다.
  - **과제**: 원본의 TODO 주석을 `# ✍️ WRITE_HERE: …`로, 정답 줄을 `...  # ✍️ 여기를 채웁니다` 빈칸으로 바꾼다. 수강생이 CodeMate와 채운다.
  - 지시문 완성본은 주지 않는다. 과제마다 **프롬프트 힌트**(3문장 이내, 무엇을 어떻게 지시하면 되는지)와 **성공 기준**만 준다. 수강생이 지시를 직접 쓴다.
  - 수강생 글에서는 도구 이름(CodeMate)을 쓰지 않고 "AI"라고 한다. AI와 함께 작업하는 것은 당연한 전제라 길게 설명하지 않는다.
  - 성공 기준은 🟢(되어야 하는 것)와 ⛔(다시 해야 하는 신호)로 적는다. 자동 검사 셀은 두지 않는다. 수강생이 실행 결과를 보고 스스로 판단한 뒤 접힌 "정답 보기"와 비교한다.
- 노트북 안의 제목은 1부터 번호를 매긴다(`1.`, `1.1`, `1.1.1`). 챕터와 권은 폴더와 파일 이름으로 구분한다.
- 제목 바로 옆에 그 아래 내용의 종류를 `(슬라이드) (퀴즈) (코드) (예제) (과제)`처럼 작게 표시하고, 맨 위에 이 표시를 단 목차를 둔다. 빌더가 쓰는 `lessons/drafts/nbkit.py`가 셀 종류를 보고 자동으로 붙인다.
- 설명, 슬라이드, 그림, 실행 코드, 실습을 **노트북 한 권 안에 인라인**으로 넣는다. 수업 중 PDF 뷰어나 PPT로 화면을 바꾸지 않게 한다.
- 설명은 마크다운 셀에 쓴다. 슬라이드와 움직이는 그림은 코드 셀 출력으로 넣는다.

## 2. HTML·JavaScript 넣는 법

- 마크다운 셀에서는 `<script>`가 실행되지 않는다. 동작이 필요한 HTML은 **코드 셀**에서 `display(HTML(...))`로 출력한다.
- 짧은 것은 셀 안에 문자열로 직접 쓴다(인라인). 길거나 여러 번 쓰는 것은 `assets/`에 HTML 파일로 두고 `HTML(filename="assets/...")`으로 읽는다. 파일을 고치면 그 셀만 다시 실행한다.
- 여러 노트북에서 쓰는 위젯(슬라이드, 메시지 흐름, 그래프 실행, 코드 지도, 체크리스트, 점수표)은 `assets/widgets.py`에 있다. `from assets.widgets import ...`로 쓴다. 새 위젯도 이 규칙을 지켜 여기에 더한다.
- Python 값은 `json.dumps(..., ensure_ascii=False)`로 HTML 문자열 안에 끼워 JavaScript로 넘긴다.
- VS Code는 한 노트북의 출력을 같은 화면에 그린다. 그래서 요소 `id`가 겹치면 서로 간섭한다.
  - 앱마다 고유한 바깥 `id`를 하나 두고, 안쪽 요소는 그 안에서 `querySelector`로 찾는다.
  - 스크립트는 `(() => { ... })();`로 감싸 변수가 새지 않게 한다.
  - 같은 앱을 여러 번 띄울 때는 `iframe srcdoc`으로 격리한다. `<iframe>`을 `<div>`로 감싸야 IPython 경고가 나오지 않는다.

## 3. 슬라이드 넣는 법

- 원본이 PDF인 교안은 **PDF.js로 PDF를 그대로 그린다(2026-09-28 확정).** 벡터라 선명하고, 글자를 선택·복사할 수 있다.
  - `show_slides("1-2", [9, 10])`: `docs/raw/` 아래에서 `1-2-*.pdf`를 찾아 필요한 쪽만 보여 준다.
  - PDF.js는 `assets/vendor/pdfjs-3.11.174/`(legacy 빌드, Apache-2.0)를 HTML 안에 넣어 쓴다. 외부 주소를 부르지 않는다.
  - 노트북 맨 위 준비 셀에서 `slide_setup()`을 부른다. 노트북을 다시 열어 슬라이드가 비어 보이면 이 셀을 다시 실행한다.
  - Jupyter 화면의 require.js(AMD)와 부딪히지 않도록, 불러오는 동안 `define`을 잠시 숨긴다(`widgets.py`).
- PDF가 없는 자료(예: 커리큘럼 PPTX)는 예전 방식대로 이미지 묶음을 쓴다. 쪽 이미지를 `assets/slides/<이름>.json`으로 만든다.

  ```
  uv run python lessons/assets/build_slide_deck.py <입력.pdf|입력.pptx> lessons/assets/slides/<이름>.json
  ```

  필요한 도구는 `pdftoppm`(poppler), PPTX라면 `soffice`(LibreOffice)다. 이 방식은 화질이 떨어지고 글자를 선택할 수 없다.
- PDF를 `iframe`에 바로 넣지 않는다. VS Code 출력 화면에는 PDF 뷰어가 없다.

## 4. 모든 것을 HTML 안에 넣는다

- VS Code 출력 화면은 상대 경로의 로컬 파일(`<img src="...">`, `<script src="...">`, `IFrame("x.html")`)을 불러오지 못하는 경우가 많다.
- 그래서 이미지는 base64 `data:` URI로, 스크립트는 `<script>` 본문으로 HTML 안에 넣는다.

## 5. 사내망: 외부 CDN을 쓰지 않는다

- 강의장은 사내망이다. HTML에 외부 주소(`https://`, `//`)를 넣지 않는다. 가능하면 기본 JavaScript·SVG로 만든다.
- 라이브러리가 꼭 필요하면 사외에서 `.js` 파일을 받아 `assets/vendor/`에 두고, 파일 이름에 버전을 적는다(예: `chart-4.4.1.min.js`). 생성 스크립트가 그 내용을 `<script>` 본문으로 넣는다.
- 새 HTML을 만든 뒤 외부 주소가 없는지 `src=`, `href=`, `http`, `<link`, `import(`로 검색해 확인한다.

## 6. 경로·용량·커밋

- 코드 셀 안의 경로는 노트북이 있는 폴더(`lessons/Chapter01/` 등) 기준이다. 준비 셀에서 `sys.path.insert(0, '..')`로 `lessons/assets`를 불러온다. 마크다운에 적는 명령은 프로젝트 루트 기준이다.
- 실습에서 고칠 파일은 원본(`src/raw/`)을 직접 고치지 않고 `lessons/work/`에 복사해서 고친다. `work/`는 Git 제외 대상이다.
- 출력을 저장하면 슬라이드 이미지가 노트북 파일에 들어가 수 MB가 된다. 커밋 전에 출력을 지운다.
- 고객사 자료(커리큘럼 제안서 등)로 만든 뷰어는 내용이 이미지로 들어 있다. 커밋·공유 전에 확인한다.

## 7. 검증

- 기존 교수법 도구(Jupytext, nbstripout, ipytest, Graphviz, diagrams, archify, plotly, jupyterquiz)의 사용 예와 사내망 점검표는 `demo_d_tool_tryout.ipynb`에 있다. 필요한 패키지는 `uv sync --extra notebooks --extra teaching`으로 설치한다.
- 퀴즈 형식 11가지(jupyterquiz, jupytercards, 순서 맞추기·틀린 줄 찾기 위젯, 예측 후 실행, ipytest 빈칸, LLM 채점 서술형)는 `demo_e_quiz_types.ipynb`에 있다. 숫자형 문제의 정답은 코드로 계산해 넣어 교안이 바뀌어도 어긋나지 않게 한다.

- QC: `uv run python lessons/qc/notebook_qc.py <노트북>`(규칙 검사, `--execute`면 새 커널 실행까지)와 Claude Code 명령 `/notebook-qc`(판단 점검표)로 확인한다.
  - 종류는 파일 이름 끝(`_LEC`/`_LAB`)으로 정한다. 강의 노트북에 `run_step`·`show_code`·`show_code_map`·`make_blank`·`show_diff`가 있으면 FAIL, 실습 노트북에 `make_blank`·`run_step`·`show_diff`·`show_code_map`·`show_slides`가 있으면 FAIL이다.
  - 두 종류 모두 수강생 글(강사용 상자 밖 마크다운·퀴즈)에 `.py` 파일 이름·`src/`·`lessons/`·`.ipynb`가 있으면 FAIL, 다른 노트북 언급("강의 노트북", "실습 노트북", "강의에서 본", `_LEC`, `_LAB`)은 WARN이다.
  - 두 종류 모두 수강생 글에 `CodeMate`가 있으면 FAIL이다. 실습 노트북은 지시문 완성본이 있으면 FAIL, `✍️ CHANGE_HERE`·`WRITE_HERE`가 코드 줄 끝에 붙어 있으면 FAIL, 프롬프트 힌트가 3문장을 넘으면 FAIL, 보이는 코드에 `TODO`가 남았거나 `WRITE_HERE`·`CHANGE_HERE` 앞에 `# ✍️`가 없으면 FAIL, 자동 검사 셀(`show_criteria`)이 있으면 FAIL이다. 과제 빈칸 셀마다 빈칸 상태 문법, 앞쪽의 프롬프트 힌트·🟢 성공 기준, "정답 보기"를 끼웠을 때의 문법을 검사한다. 예제의 CHANGE_HERE는 같은 장에 🟢 성공 기준 글이 있어야 한다. `(작성 예정)`은 뼈대 상태라 WARN이다.
- 새 커널 실행: `uv run --extra notebooks jupyter nbconvert --to notebook --execute lessons/<이름>.ipynb --output-dir <임시 폴더>`. 모든 셀이 오류·경고 없이 출력을 내는지 본다.
- JavaScript 동작은 `--to html`로 내보낸 파일을 브라우저에서 눌러 보고, VS Code에서도 직접 눌러 본다. 내보낸 HTML은 require.js·MathJax를 CDN에서 부르지만 검증용일 뿐이며 수업 노트북과는 관계없다.
