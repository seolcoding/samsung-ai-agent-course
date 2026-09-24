# 주피터 노트북 교안 안내

PDF 정본은 `docs/raw/`에 둔다. Python 실습과 정답의 `.ipynb`는 대응하는 `.py`와 같은 폴더에 둔다. 슬라이드 해설 노트북은 `docs/notebooks/`에 별도로 둔다.
슬라이드 화면·설명·실습을 한 권에 모은 최종 교안은 `lessons/`에 만든다. 이름과 작성 순서는 [통합 교안 작성 규칙](INTEGRATED_LESSONS.md)을 따른다. 지금 있는 [`lessons/_template.ipynb`](../lessons/_template.ipynb)는 복사해 쓰는 틀이며 수업용 완성본은 아니다.

## 시작하기

1. 프로젝트 루트에서 `uv sync`를 실행한다.
2. 노트북 커널이 없으면 `uv pip install ipykernel`을 실행한다.
3. VS Code에서 원하는 `.ipynb`를 열고 프로젝트의 `.venv` Python을 커널로 선택한다.
4. 먼저 설명과 실행 조건을 읽고 필요한 셀만 실행한다. API 호출, 서버 시작, 파일 쓰기 등은 해당 환경과 권한이 준비된 뒤 실행한다.

서버와 Streamlit 예제는 노트북에서 구조를 읽고 검토한 뒤, `src/raw/` 또는 `src/solution/`의 `.py`를 별도 터미널에서 실행한다. 슬라이드 노트북은 페이지별 개념을 설명하며, 도표의 세부 모습은 연결된 PDF에서 확인한다.

## 순서

| 일차 | 이론 교안 | 실습 노트북 |
| --- | --- | --- |
| 1일차 | [해설 노트북](notebooks/Chapter01/day01/) · [PDF](raw/Chapter01/day01/) | [LLM API](../src/raw/Chapter01/01-llm-api/) → [LangChain](../src/raw/Chapter01/02-langchain/) |
| 2일차 | [해설 노트북](notebooks/Chapter01/day02/) · [PDF](raw/Chapter01/day02/) | [RAG](../src/raw/Chapter01/03-rag/) → [LangGraph](../src/raw/Chapter01/04-langgraph/) → [Multi-Agent](../src/raw/Chapter01/05-multi-agent/) → [Streamlit RAG](../src/raw/Chapter01/06-rag-streamlit/) |
| 3일차 | [해설 노트북](notebooks/Chapter02/day01/) · [PDF](raw/Chapter02/day01/) | [복습](../src/raw/Chapter02/00-review/) → [MCP](../src/raw/Chapter02/01-mcp/) → [A2A](../src/raw/Chapter02/02-a2a/) → [LangGraph 심화](../src/raw/Chapter02/03-langgraph-advanced/) |
| 4일차 | [해설 노트북](notebooks/Chapter02/day02/) · [PDF](raw/Chapter02/day02/) | [하네스](../src/raw/Chapter02/04-harness/) → [관측·평가](../src/raw/Chapter02/05-observability/) → [캡스톤](../src/raw/Chapter02/06-capstone/) |

정답 노트북은 [`src/solution/`](../src/solution/)에 정답 `.py`와 함께 있다. 수강생용과 정답본의 코드가 다른 부분은 두 파일을 나란히 열어 비교한다. 노트북 코드는 해당 Python 예제를 옮긴 스냅샷이며, Python 파일의 후속 수정을 자동으로 따라가지 않는다. 수업 직전에는 컨플루언스의 최신 안내와 강의장 CodeMate 화면을 확인한다.
