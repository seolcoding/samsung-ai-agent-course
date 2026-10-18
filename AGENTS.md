# AGENTS.md — 삼성전자 DS AI Agent 개발 프로젝트 교육 (v3.0, 2026-10-19)

강의용 실습 코드와 교안이다. 제품 코드가 아니다. 모든 변경은 "수강생 앞에서 어떻게 보이나"로 판단한다.

## 1. 과정

- 고객사 삼성전자 DS부문 AX·PI센터(담당 이산하 프로), 중개 워카(박혜진 프로 `hyejin@woka.kr`).
- M1 = `Chapter01`(1·2일차), M2 = `Chapter02`(3·4일차). 14차수 2026-10-19~22, 동탄DS큐브 23F OA강의장.
- 정본: 모듈·시간은 `dev/materials/2026-09-03_커리큘럼_제안서.pptx`, 강의·실습 내용은 받은 `course/ChapterNN/code/raw/`와 `slides/` PDF.

## 2. 방향 (2026-09-17 고객사 확정)

- 받은 강의·실습 내용은 그대로 두고 방식만 바꾼다: 주피터 노트북 + 사내 Coding AI와 페어 프로그래밍.
- 교육 목표: 1) Agent 개념·이론 2) Coding AI로 Agent 개발 3) 하네스·루프 엔지니어링 4) AI 산출물 검토·재지시.
- 수강생은 코드를 타이핑하지 않고 AI에게 시킨 뒤 결과를 리뷰한다. 실습은 이 전제로 설계한다.

## 3. 환경

- `uv` + `pyproject.toml`, VS Code, Coding AI는 사내 CodeMate(Roo Code 계열로 추정, 실제 UI는 강의장에서 확인).
- `.env`의 `COURSE_ENV=samsung`(사내 게이트웨이, 사내망 전용) 또는 `out`(사외: OpenAI, RAGaaS는 모의 응답).
- 수강생 PC는 미리 셋팅할 수 없다. 1일차 현장에서 다 같이 설치한다.

## 4. 수강생

- 코딩·AI가 낯선 수강생이 다수다. 모든 난이도는 이 기준선으로 정한다.
- 구조·리뷰 중심 설명을 좋아하고, 실습과 LLM과 직접 부딪히는 방식을 더 원한다(`dev/docs/2026_11차수_수강생피드백.md`).

## 5. 폴더와 브랜치

- `course/` 수강생 전달본(`dev/`를 참조하지 않는다): `ChapterNN/notebooks`·`tasks`·`code`·`slides`·`assets`, `config/`, `agent_docs/`, `Chapter02/capstone/`.
- `dev/` 강사용(전달 안 함): `builders`(노트북 빌더·spec), `qc`, `instructor`(강사본), `solutions/tasks`(과제 정답), `docs`, `materials`, `tests`.
- `.agents/skills/` 프로젝트 스킬(study에도 들어간다). 메일·첨부·받은 ZIP은 저장소 밖 `~/800_Archives/830_Courses/samsung_ds_ai_developer/`.
- `dev`에서 고치고 검사 → `main`(완성본)에 합침 → `dev/release.sh`가 수강생용 `study`를 만든다. `study`는 직접 고치지 않는다.
- 원격(origin, public): `dev`←로컬 `dev`, `study`←로컬 `study`(기본 브랜치). **로컬 `main`은 원격 main에 push하지 않는다.**

## 6. 반드시 지킬 것

1. 노트북은 직접 고치지 않는다. `dev/builders/`의 글·spec을 고쳐 다시 빌드한다(제작 규칙은 `dev/AGENTS.md`).
2. 받은 원본(`code/raw`·`solution`)은 그대로 두고 노트북에서만 바꿀 것은 spec `patch`로 한다. 원본을 고치면 raw·solution을 함께.
3. 코드를 바꾸면 슬라이드·교안 노트북과 어긋나지 않는지 함께 본다.
4. 키는 저장소에 쓰지 않는다(`.env`는 git 제외). 교육 계정이 든 `dev/materials/` 인수인계 자료만 사용자 허락으로 커밋했다.
5. 조용히 틀리는 데모가 최악이다(오류가 낫다). 고쳤으면 실제로 실행해 본다.
6. 시킨 것만 만든다. 근거 없는 내용(수업 진행, 수강생 반응, 사내 환경)을 지어내지 않는다.
7. `.env*` 주석은 ASCII, 파일 입출력은 `encoding="utf-8"`(윈도우 cp949 대비, `dev/tests/test_encoding.py`가 검사).
8. 명령과 링크는 프로젝트 루트 기준이고, 실행은 `uv run --env-file .env …`처럼 환경 파일을 적는다.

## 7. 알려진 결함과 미확인

- 사내 게이트웨이의 도구 호출(`bind_tools`)·구조화 출력이 확인되지 않았다. M2는 거의 전부 도구 호출이라 사전 점검 1순위다.
- 사내 Responses API(1-2·1-3), 사내 임베딩(다국어), RAGaaS, 사내 Langfuse도 미확인이다.
- RAGaaS는 `RAG_API_KEY` 전역변수와 요청 헤더 `'api-key'`가 둘 다 있어야 인증된다.
- 받은 원본 코드의 결함(HITL 거부 때 메일 전송, MCP SSE/stdio 어긋남, 3-4 `compile()` 누락 등)은 노트북에서 patch로 고쳤다.
- 받은 원본 A2A 코드는 현재 SDK 1.x와 API가 다르다. 캡스톤은 받은 `06-capstone/` 대신 `course/Chapter02/capstone/`을 쓴다.

## 8. 검증

- `uv sync --extra notebooks` 후 `uv run --extra notebooks python -m unittest discover -s dev/tests -p 'test_*.py'`(외부 API 없음).
- 노트북은 `dev/qc/notebook_qc.py`로 검사한다. 실제 모델·Langfuse·CodeMate 확인은 따로 기록한다.
- 노트북 출력과 키는 커밋하지 않는다.

## 9. 되돌리기와 기록

- 로컬 `main`의 최초 커밋 `c54a1ce`가 받은 zip 그대로다. 원본 zip은 아카이브의 `source_archives/`에 있다.
- 대량 이동·삭제와 게시 기록은 `~/_MANIFESTS/samsung_ds_*`에 있다.
