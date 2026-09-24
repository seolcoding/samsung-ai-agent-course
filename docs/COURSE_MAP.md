# 강의 자료 지도

M1은 `Chapter01`(1·2일차), M2는 `Chapter02`(3·4일차)다. 아래 경로는 프로젝트 루트 기준이다. 강의 직전의 세부 순서와 과제는 컨플루언스 최신 안내를 확인한다.
슬라이드·설명·코드를 합친 수업용 노트북은 [`lessons/`](../lessons/)에 만든다. [조립 지도](INTEGRATED_LESSONS.md)의 4일·13개 시간 블록을 따라 원본의 순서를 다시 짠다. 아래의 기존 노트북은 통합본을 만드는 재료다.

| 일차 | PDF 정본 | Python 실습 | 학습 노트북 |
| --- | --- | --- | --- |
| 1일차 | [Chapter01/day01](raw/Chapter01/day01/) | [LLM API·LangChain](../src/raw/Chapter01/) | 실습 코드 옆 `.ipynb` · [슬라이드 해설](notebooks/Chapter01/day01/) |
| 2일차 | [Chapter01/day02](raw/Chapter01/day02/) | [RAG·LangGraph·Multi-Agent·Streamlit](../src/raw/Chapter01/) | 실습 코드 옆 `.ipynb` · [슬라이드 해설](notebooks/Chapter01/day02/) |
| 3일차 | [Chapter02/day01](raw/Chapter02/day01/) | [복습·MCP·A2A·LangGraph 심화](../src/raw/Chapter02/) | 실습 코드 옆 `.ipynb` · [슬라이드 해설](notebooks/Chapter02/day01/) |
| 4일차 | [Chapter02/day02](raw/Chapter02/day02/) | [하네스·관측·캡스톤](../src/raw/Chapter02/) | 실습 코드 옆 `.ipynb` · [슬라이드 해설](notebooks/Chapter02/day02/) |

정답 Python 파일과 노트북은 [`src/solution/`](../src/solution/)에 같은 장·주제 순서로 둔다. 실행에 필요한 PDF·텍스트 데이터는 해당 실습의 `data/` 폴더에 둔다. 외부 API 연결은 [`src/config/`](../src/config/)에서 환경변수에 따라 선택한다.
