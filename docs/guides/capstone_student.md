# 캡스톤: 근거를 확인하는 보고서 Agent

수업은 [4일차 노트북의 4.3](../../lessons/day04.ipynb)에서 진행한다. 기존 과정의 Supervisor·MCP·승인·Streamlit·Skill 평가 요소를 유지하며, 이 통합본에서는 **근거 조사 후 작성 전 승인**으로 시점을 통일한다.

## 실행

```bash
uv sync --extra notebooks
uv run --extra notebooks streamlit run src/courseware/app.py
```

‘승인 후 보고서’를 선택하고 주제를 입력한다. ‘근거 조사’ 후 문서를 확인하고 ‘승인하고 작성’ 또는 ‘거절하고 중단’을 누른다. 기본은 교육용 모의 자료·원문 발췌이며 외부 API가 필요 없다.

## 구조

```text
src/courseware/
  capstone.py        Supervisor → Researcher → 승인 → Writer → 검사
  app.py             질문 UI와 보고서 승인 UI
  mcp_server.py      교육 문서 검색 Tool·Resource·Prompt
  knowledge.py       교육 자료 검색과 원문 발췌
  data/knowledge.json  실제 회사 자료가 아닌 교육용 데이터
  skills/report/SKILL.md  보고서 작업 규칙
```

각 Python 파일 옆의 `.ipynb`는 해당 구현을 읽고 작은 호출을 실행하는 동반 노트북이다. 4일차 노트북은 설명·그림·실습을 통합한다.

## CodeMate 작업 순서

1. 목표·입력·완료 기준을 적고 위 코드를 읽힌다.
2. 작은 변경 하나의 파일 범위와 검증 방법을 먼저 제안받는다.
3. 구현 후 정상·거절·근거 없음 경로를 실행한다.
4. 보고서 출처·내용·UI를 검토하고 다음 수정 지시를 내린다.
5. 실행 명령·실제 검증 결과·남은 제약을 정리하고 커밋한다.

새 요청에는 새 thread ID를 사용한다. 중단된 승인은 같은 thread에서 `Command(resume={"approved": True})` 또는 `False`로 재개한다. 노드를 재개하면 다시 시작될 수 있으므로 승인 앞에 외부 전송을 두지 않는다.

## 평가 기준

| 항목 | 배점 | 확인할 결과 |
| --- | ---: | --- |
| Supervisor 라우팅 | 30 | 조사·승인·작성·검사·종료가 상태에 따라 선택됨 |
| Human-in-the-Loop | 25 | 승인 대기, 승인 후 작성, 거절 후 Writer 미실행 |
| MCP 도구 연동 | 20 | 도구 발견과 실제 호출, 근거 목록 반환 |
| Streamlit UI | 15 | 근거 확인·승인/거절·보고서 표시 |
| Skill 규칙 반영 | 10 | 핵심 내용·근거·한계, 유효한 출처, 내용 검토 |

규칙 기반 Supervisor도 위 계약을 만족하면 기본 구현으로 인정한다. 모델 판단을 추가했다면 승인·종료 조건이 유지되는지 추가 검증한다. API 호출 여부만으로 가점을 정하지 않는다.

## 확장

- 실제 Writer: 노트북의 `RUN_LIVE=True`와 `get_llm()` 경로를 사용한다. 모델 응답의 충실성을 다시 검토한다.
- RAGaaS: 응답을 `id/title/text/source`로 변환하는 어댑터를 추가한다. `[MOCK RAGaaS]`는 실제 검색 결과로 표시하지 않는다.
- 웹 검색: 강의장 접근 정책과 도구 권한을 확인한 뒤 추가한다.
- 작성 후 승인: 초안 발행 승인이 필요하면 작성 전 승인과 별개 노드를 추가한다.
- DeepAgents: 4.1.4의 Skill·Backend 경계를 유지하며 필요한 작업에 적용한다.

기존 `src/raw/Chapter02/06-capstone`과 `src/solution/Chapter02/06-capstone`은 원본 비교 자료다. 이 통합본의 실행 명령은 `src/courseware`를 사용한다.
