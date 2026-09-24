# 주피터 노트북 교안 안내

PDF 정본은 `docs/raw/`에 둔다. Python 실습과 정답의 `.ipynb`는 대응하는 `.py`와 같은 폴더에 둔다. 슬라이드 해설 노트북은 `docs/notebooks/`에 별도로 둔다.
설명·그림·코드 실행·CodeMate 실습을 의미 번호 순서로 엮은 최종 교안은 `lessons/day01.ipynb`~`day04.ipynb`다. [통합 교안 조립 지도](INTEGRATED_LESSONS.md)의 `1.1`, `1.1.1` 번호를 따른다. 시간은 [강사용 배분표](INSTRUCTOR_TIMING.md)에만 둔다. [`lessons/_prototype_agent_loop.ipynb`](../lessons/_prototype_agent_loop.ipynb)는 `1.1.2`·`1.1.3`의 완성 모습 시범본, [`lessons/_template.ipynb`](../lessons/_template.ipynb)는 작성 틀이다. 수업에서는 완성된 `day01.ipynb`~`day04.ipynb`를 연다.

## 시작하기

1. 프로젝트 루트에서 `uv sync --extra notebooks`를 실행한다.
2. `lessons/day01.ipynb`부터 해당 일차의 노트북을 연다.
3. VS Code에서 원하는 `.ipynb`를 열고 프로젝트의 `.venv` Python을 커널로 선택한다.
4. 기본 `RUN_LIVE=False`, `ENABLE_LANGFUSE=False`에서 설명을 읽고 위에서부터 실행한다. API 호출, 서버 시작, 파일 쓰기 등은 해당 환경과 권한이 준비된 뒤 실행한다.

통합본의 서버·Streamlit 구현은 `src/courseware/`에 있다. MCP·A2A는 실제 프로토콜 호출, Streamlit은 AppTest를 노트북에서 실행한다. 브라우저 화면은 `uv run --extra notebooks streamlit run src/courseware/app.py`로 연다. Python 옆 동반 노트북은 구현을 import해 작은 호출을 실행한다. 슬라이드 노트북은 페이지별 개념을 설명하며, 도표의 세부 모습은 연결된 PDF에서 확인한다.

## 통합 노트북을 발표하며 실행하기

VS Code의 **Jupyter Slide Show** 확장(`ms-toolsai.vscode-jupyter-slideshow`)은 셀에 발표용 유형을 붙인다. 노트북을 연 뒤 명령 팔레트(맥 `Cmd+Shift+P`, 윈도우 `Ctrl+Shift+P`)에서 `Switch Slide Type`을 선택해 현재 셀의 유형을 바꿀 수 있다. 제목·핵심 그림은 `Slide`, 이어지는 설명·코드는 `Sub-Slide`, 강사용 출처·메모는 `Notes`로 표시한다. [작성 틀](../lessons/_template.ipynb)에 이 메타데이터의 예가 있다.

**수업 중 코드 실행과 CodeMate 실습은 VS Code의 `.ipynb` 화면에서 진행한다.** 확장은 셀 유형을 지정하는 기능이며 실행 가능한 발표 화면을 별도로 제공하지 않는다. `jupyter nbconvert lessons/day01.ipynb --to slides --post serve`로 변환한 HTML은 발표용 정적 화면이다. 그 화면에서 Python 셀을 실시간 실행할 수는 없다. `nbconvert`가 설치돼 있어야 하고, 기본 HTML은 Reveal.js를 외부 CDN에서 읽으므로 사내망에서 발표 자료로 쓸 때는 별도로 접속을 확인해야 한다. [Microsoft 확장 안내](https://github.com/microsoft/vscode-jupyter-slideshow), [Jupyter nbconvert 안내](https://nbconvert.readthedocs.io/en/latest/usage.html#reveal-js-html-slideshow).

## 원본 자료 순서

| 일차 | 이론 교안 | 실습 노트북 |
| --- | --- | --- |
| 1일차 | [해설 노트북](notebooks/Chapter01/day01/) · [PDF](raw/Chapter01/day01/) | [LLM API](../src/raw/Chapter01/01-llm-api/) → [LangChain](../src/raw/Chapter01/02-langchain/) |
| 2일차 | [해설 노트북](notebooks/Chapter01/day02/) · [PDF](raw/Chapter01/day02/) | [RAG](../src/raw/Chapter01/03-rag/) → [LangGraph](../src/raw/Chapter01/04-langgraph/) → [Multi-Agent](../src/raw/Chapter01/05-multi-agent/) → [Streamlit RAG](../src/raw/Chapter01/06-rag-streamlit/) |
| 3일차 | [해설 노트북](notebooks/Chapter02/day01/) · [PDF](raw/Chapter02/day01/) | [복습](../src/raw/Chapter02/00-review/) → [MCP](../src/raw/Chapter02/01-mcp/) → [A2A](../src/raw/Chapter02/02-a2a/) → [LangGraph 심화](../src/raw/Chapter02/03-langgraph-advanced/) |
| 4일차 | [해설 노트북](notebooks/Chapter02/day02/) · [PDF](raw/Chapter02/day02/) | [하네스](../src/raw/Chapter02/04-harness/) → [관측·평가](../src/raw/Chapter02/05-observability/) → [캡스톤](../src/raw/Chapter02/06-capstone/) |

정답 노트북은 [`src/solution/`](../src/solution/)에 정답 `.py`와 함께 있다. 수강생용과 정답본의 코드가 다른 부분은 두 파일을 나란히 열어 비교한다. 노트북 코드는 해당 Python 예제를 옮긴 스냅샷이며, Python 파일의 후속 수정을 자동으로 따라가지 않는다. 수업 직전에는 컨플루언스의 최신 안내와 강의장 CodeMate 화면을 확인한다.

## 실행 결과와 그림

학생 배포 노트북은 출력·실행 횟수를 비워 둔다. 그림은 attachment로 포함되어 단독 파일에서도 보이지만 코드 실행에는 프로젝트와 패키지가 필요하다. `tests/validate_lessons.py --execute --companions`는 새 커널로 실행해 검증하고 결과 노트북·HTML을 Git 제외 폴더 `docs/_build/`에 만든다. HTML은 읽기용이며 실행 화면은 원본 노트북이다.
