# 통합 교안 검증 기록

검증일: 2026-09-24. 환경: macOS, 프로젝트 `.venv`, Python 3.12.7. 브랜치: `feat/integrated-course-suite`.

## 검증 결과

| 대상 | 실행과 확인 | 결과 |
| --- | --- | --- |
| 통합 교안 | day01~day04, 새 커널에서 위에서 아래로 실행 | 4권·67개 코드 셀 통과 |
| 코드 옆 동반 노트북 | courseware의 6권, 각각 새 커널 실행 | 18개 코드 셀 통과 |
| 의미 번호 | 4권의 제목·metadata·강사용 배분표 대조 | 13개 블록·63개 주제 일치 |
| 시간 배분 | 의미 번호별 배정 합계 | 매일 480분, 전체 1,920분 |
| 그림 | attachment 존재·원본 경로·그림 설명·범위 설명 검사 | 생성 이미지 8개 + 도식 16개 포함 |
| 자동 테스트 | 기존 환경/경로 테스트 + 새 캡스톤/화면 테스트 | 19개 통과 |
| 기본 캡스톤 | 승인·거절·근거 없음·잘못된 승인값·새 thread | 기대 경로 통과 |
| MCP | FastMCP in-memory 및 별도 Python 프로세스 stdio | 도구 발견·정상 호출·입력 오류 확인 |
| A2A | SDK 1.x Agent Card·JSON-RPC·Message, HTTPX ASGI | 출처 포함 응답 확인 |
| Streamlit | AppTest 질문/승인/거절 + Aside 실제 브라우저 | 조사→근거 확인→승인→보고서·검사 결과 표시 |
| 시각 검토 | HTML의 개념 그림·한국어 캡션, 캡스톤 도식·화면 | 문자·연결·설명 읽기 확인 |
| 파일 상태 | 출력 비움·로컬 링크·git diff --check | 확인 완료 |

1일차의 토큰 선택 예제는 낮은 확률 후보도 보이도록 난수 시드를 조정한 뒤 해당 노트북을 다시 실행했다. 경고 안내 문구도 보완했다. 학생용 파일에는 실행 결과를 저장하지 않았다.

## 재현 명령

프로젝트 루트에서 실행한다.

```bash
uv sync --extra notebooks
uv run --extra notebooks python tests/validate_lessons.py --execute --companions
uv run --extra notebooks python -m unittest discover -s tests -p 'test_*.py'
uv run --extra notebooks streamlit run src/courseware/app.py
```

검증 실행본·읽기용 HTML은 `docs/_build/lessons/`와 `docs/_build/courseware/`에 생성한다. 이 폴더는 Git 제외 대상이다. 원본 노트북과 생성 이미지는 저장소에 포함한다. HTML은 읽기용이며 실행은 VS Code의 `.ipynb`에서 한다.

## 버전과 관찰된 경고

`uv.lock`으로 설치 버전을 고정했다. 기존 패키지 버전의 변경은 없으며 노트북 extra에 필요한 패키지가 추가됐다.

- LangChain 1.4.2, LangGraph 1.2.12, FastMCP 3.4.7, A2A SDK 1.1.5.
- DeepAgents 0.7.18, Langfuse 4.15.4, Streamlit 1.64.0.
- nbclient 0.11.0, nbformat 5.11.1, ipykernel 7.3.0.
- 1.3.4는 원본의 RunnableWithMessageHistory와 InMemoryChatMessageHistory를 비교 학습하며 deprecation 경고가 발생한다. 새 구현은 2.2.4·3.4.2의 Checkpointer를 따른다. 경고의 의미를 본문에 표시했다.
- AppTest는 브라우저 서버 밖에서 실행되어 ScriptRunContext 경고를 출력할 수 있다. 실제 위젯 동작과 결과를 assertion으로 확인했다.
- A2A 1.1.5의 즉시 응답 정리 중 Dispatcher 경고가 별도 호출에서 관찰됐다. Card·Message의 결과 검사는 통과했다. 장기 Task·취소는 검증 범위에 포함하지 않는다.
- 커널 시작 시 로컬 TCP 연결에 대한 IPKernel 경고가 출력된다. 이는 셀 실패를 뜻하지 않으며 검증은 로컬 커널에서 수행했다.

## 실제 연결로 확인할 범위

기본 모드는 외부 API를 호출하지 않는다. 자료·모델 대역은 교육용이라고 표시한다. LangChain·LangGraph·MCP·A2A·Chroma·DeepAgents·Streamlit 자체는 실제 라이브러리를 실행했다.

### 사외 실제 연결 (2026-09-26)

`.env`(`LLM_PROVIDER=openai`, `EMBED_PROVIDER=openai`, `RAG_PROVIDER=mock`, `gpt-6-luna`, `text-embedding-3-small`)로 day01~day04를 `RUN_LIVE=True`, `ENABLE_LANGFUSE=True`로 바꾼 임시 사본에서 새 커널로 실행했다. 저장소의 노트북은 바꾸지 않았다.

| 대상 | 결과 |
| --- | --- |
| 텍스트 응답·LCEL 체인 (1.2, 1.3) | 한국어 응답 확인 |
| 도구 호출 Agent (create_agent, LangGraph ToolNode) | `multiply` 호출 → 42, 72 결과로 최종 답변 |
| 임베딩 (2.1) | 7개 청크, 1536차원 |
| DeepAgents Skill 읽기 | 보고서 Skill 규칙을 요약 |
| 구조화 출력 Judge | `JudgeResult` 반환. 근거에 없는 "교육 자료입니다."를 지적 |
| 캡스톤 승인·거절·근거 없음 | 실제 모델 Writer가 출처 ID를 붙여 작성. 거절·근거 없음 경로에서 Writer 미실행 |
| Langfuse | `auth_check` 통과, Trace 생성과 observation 5개 저장을 API로 조회 |

- `gpt-6` 계열은 langchain-openai 1.6.6에서 도구가 있으면 Responses API로 자동 전환된다. 이때 `content`가 dict 목록으로 출력되어 사내 경로(Chat Completions, 문자열)와 화면이 달랐다. `src/config/llm.py`에서 `use_responses_api=False`로 고정해 두 경로의 출력 형식을 맞췄다.
- Langfuse 실습 셀은 모의 모델을 기록하므로 "LLM model을 해석하지 못했다"는 경고가 출력된다. 기록 자체는 저장된다.

아래는 아직 실행하지 않았다.

- 삼성 사내 LLM·임베딩의 실제 응답과 도구 호출.
- 사내 RAGaaS의 인증·응답·자료 접근 정책.
- 강의장 Windows PC의 설치, CodeMate UI, 사내 프록시·방화벽·컨플루언스 최신 과제.
- 기존 `src/raw/`·`src/solution/` 전체의 최신 SDK 이관.

실제 연결을 선택한 경우 오류를 자동으로 mock으로 바꾸지 않는다. 실행 조건은 [강사용 안내](INSTRUCTOR_GUIDE.md), 연결 구성은 [환경 설정](../src/config/)을 따른다.
