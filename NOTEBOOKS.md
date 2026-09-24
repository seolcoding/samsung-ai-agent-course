# 주피터 노트북 교안 안내

원본 PDF와 Python 파일은 그대로 두고, 같은 폴더에 같은 이름의 `.ipynb` 파일을 두었다. PDF 노트북은 개념 설명과 실습 질문을 제공하고, Python 노트북은 원본 코드와 CodeMate 검토 과제를 함께 제공한다.

## 시작하기

1. 프로젝트 루트에서 `uv sync`를 실행한다.
2. 노트북 커널이 없으면 `uv pip install ipykernel`을 실행한다.
3. VS Code에서 원하는 `.ipynb`를 열고 프로젝트의 `.venv` Python을 커널로 선택한다.
4. 먼저 설명과 실행 조건을 읽고 필요한 셀만 실행한다. API 호출, 서버 시작, 파일 쓰기 등은 해당 환경과 권한이 준비된 뒤 실행한다.

서버와 Streamlit 예제는 노트북에서 구조를 읽고 검토한 뒤, 원본 `.py`를 별도 터미널에서 실행하는 흐름을 따른다. PDF 노트북은 페이지별 개념을 설명하며, 도표의 세부 모습은 연결된 원본 PDF에서 확인한다.

## 순서

| 일차 | 이론 교안 | 실습 노트북 |
| --- | --- | --- |
| 1일차 | [M1 day01](99_pdf/Chapter01/day01/) | [LLM API](Chapter01/01-llm-api/) → [LangChain](Chapter01/02-langchain/) |
| 2일차 | [M1 day02](99_pdf/Chapter01/day02/) | [RAG](Chapter01/03-rag/) → [LangGraph](Chapter01/04-langgraph/) → [Multi-Agent](Chapter01/05-multi-agent/) → [Streamlit RAG](Chapter01/06-rag-streamlit/) |
| 3일차 | [M2 day01](99_pdf/Chapter02/day01/) | [복습](Chapter02/00-review/) → [MCP](Chapter02/01-mcp/) → [A2A](Chapter02/02-a2a/) → [LangGraph 심화](Chapter02/03-langgraph-advanced/) |
| 4일차 | [M2 day02](99_pdf/Chapter02/day02/) | [하네스](Chapter02/04-harness/) → [관측·평가](Chapter02/05-observability/) → [캡스톤](Chapter02/06-capstone/) |

정답 노트북은 [`solution/`](solution/)에 있다. 수강생용과 정답본의 코드가 다른 부분은 두 파일을 나란히 열어 비교한다. 실습 노트북의 코드는 원본 예제를 보존한 것이며, 알려진 결함을 자동 수정한 버전은 아니다. 수업 직전에는 컨플루언스의 최신 안내와 강의장 CodeMate 화면을 확인한다.
