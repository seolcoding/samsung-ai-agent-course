# AGENTS.md — 삼성전자 DS AI Agent 개발 프로젝트 교육 (2026-AI-PD)

이 리포지토리는 **강의용 실습 코드 + 교안**이다. 제품 코드가 아니다.
모든 변경은 "수강생 앞에서 이게 어떻게 보이는가"를 기준으로 판단한다.

## 1. 실행 환경

- **패키지**: `uv` + `pyproject.toml` (강의장 PC 기준 통일 설치, 셋팅에 1.5~2시간 소요)
- **에디터**: VS Code
- **Coding AI**: **CodeMate** — 삼성 사내 전용 LLM assistant, VS Code 확장으로 설치
- **수강생 PC 사전 셋팅 불가** (계정별 로컬 PC 초기화 정책). 셋팅은 1일차 현장에서 다 같이 한다.
- **LLM**: 기본 경로는 사내 게이트웨이(`LLM_PROVIDER=samsung`). 사내망에서만 동작한다.
  사외 준비 시에는 `LLM_PROVIDER=openai` / `EMBED_PROVIDER=openai`로 바꿔서 작업한다.

## 2. 리포지토리 구조

```
course/                    ← 수강생 전달본. 수강생에게 필요한 것만 둔다(dev/를 참조하지 않는다)
  README.md, AGENTS.md     수강생용 설치·실행 안내, 수강생 쪽 AI 코딩 도우미용 맥락
  agent_docs/              설치·경로·오류 해결 문서(setup.md, paths.md, troubleshooting.md). 환경 문제는 강사 PC에서도 이것부터 본다
  Chapter01/
    notebooks/             수업 노트북 13권(LEC/LAB, 강사용 메모 없는 수강생본) + data/
    code/raw/, code/solution/  받은 원본 실습 코드와 정답(.py와 코드가 읽는 data·md)
    slides/                교안 PDF 정본(day01/, day02/)과 커리큘럼 제안서 PDF
    assets/                이 챕터 노트북의 도구(widgets.py, PDF.js, 퀴즈 파일). 챕터마다 따로 둔다
  Chapter02/
    notebooks/             M2 노트북 14권(3-1~4-3 LEC/LAB) + data/. MCP·A2A 서버는 LAB 셀이 %%writefile로 이 폴더에 쓰고 터미널에서 띄운다(쓴 .py는 git 제외)
    capstone/              4-3 캡스톤 프로젝트 폴더(수강생이 AI와 함께 고침). starter.py, mcp_server.py, skills/, data/, README.md
    code/raw/, code/solution/, slides/, assets/   Chapter01과 같은 역할
  config/                  환경에 따른 LLM·임베딩·RAGaaS 공통 코드(패키지 `config`, 챕터 공통)
dev/                       ← 강사·개발용. 전달하지 않는다
  AGENTS.md                노트북 제작 규칙
  builders/                노트북 빌더(build_lab.py, build_lecture_*.py, build_capstone_guide.py, nbkit.py)와 글·spec(labs/*.json, labs/Chapter02/*.json, *_cells*.json, *_outline.md)
  qc/                      노트북 QC 하네스
  instructor/ChapterNN/    강사본 노트북(강사용 메모 포함, 빌드 산출)
  demos/                   교수법 데모 노트북과 그 자산
  docs/                    CURRICULUM.md, 수강생 피드백 정리, VALIDATION, guides(받은 캡스톤 README), templates, PDF 해설 노트북(notebooks/)
  archive/                 원본 .py 옆에 있던 .ipynb 변환본, main.py, 폴더 개편 전 안내 문서(docs/)
  tests/                   환경 분기·실습 경로 검증
  release.sh               main에서 수강생용 브랜치 study와 전달 zip 만들기
  work/                    실습 작업 복사본(Git 제외, 필요할 때만 만든다)
.env.sample, pyproject.toml, uv.lock   설치 파일(study에도 들어간다)
README.md                  처음 받은 담당자용 안내
```

**중요**: 사내 GitHub 레포는 원래 *"TODO가 전부 정답으로 채워진 최종본"*이다.
`course/Chapter01/code/raw/`가 정답과 거의 같은 것은 사고가 아니라 **의도된 배포 상태**다.
차수별 브랜치(4종)는 이전 차수 강사가 임의 구성한 것이고 **강사별 재구성이 허용**된다.
브랜치는 셋이다. `dev`에서 고치고 검사한 뒤 `main`(완성본 전체)에 합친다. 수강생용 `study`는 `main`에서 `dev/release.sh`로 만든다(`course/`와 설치 파일만, 이력이 섞이지 않는 별도 브랜치). `study`에서 직접 고치지 않는다. `main`을 깎지 않는다.
`raw`는 원본 파일 형식인 `.py`와 PDF를 뜻한다. 변경 금지 아카이브라는 뜻은 아니다.
수업은 노트북으로 한다. 교안 노트북은 `dev/builders/`의 빌더로 만들고 `dev/AGENTS.md`를 따른다. 설명·슬라이드·실습을 노트북 안에 인라인으로 넣고, 외부 CDN을 쓰지 않는다. 노트북을 직접 고치지 말고 빌더의 글·spec을 고쳐 다시 빌드한다.
실행에 쓰는 `skills.md`, `SKILL.md`, `data/*.md`는 문서 형식이어도 코드가 읽으므로 `course/ChapterNN/code/`의 실습 폴더에 둔다. 그 밖의 안내 문서는 `dev/docs/`에 둔다.
명령과 링크는 프로젝트 루트를 기준으로 적는다. 실행할 때는 `uv run --env-file .env`처럼 환경 파일을 명시한다.
메일 원문, 첨부, 전달받은 ZIP, 지난 준비 기록은 저장소 밖의 강의 아카이브에 둔다. 정규 폴더에는 수업·강의 운영에 직접 필요한 자료만 둔다.

## 3. 반드시 지킬 것

1. **실습본(`code/raw/`)과 정답본(`code/solution/`)을 함께 고친다.** 한쪽만 고치면 정답지와 화면이 어긋난다.
2. **슬라이드(`course/ChapterNN/slides/`)·교안 노트북(빌더 글·spec)을 함께 확인한다.** 코드만 고치면 강사가 슬라이드를 가리키며 다른 화면을 보게 된다.
3. **데모가 조용히 틀리는 것을 최악으로 친다.** 에러가 나는 편이 낫다. 실습 코드를 고쳤으면 실제로 실행해 본다.
4. **외부 API 키는 리포지토리에 쓰지 않는다.** `.env`는 `.gitignore` 대상이다.
5. **RAGaaS 실습**은 `RAG_API_KEY` 전역변수와 `'api-key'` 요청 헤더 2가지가 없으면 인증 실패한다.
6. **정본은 두 가지다.** 모듈·시간은 커리큘럼 제안서(2026-09-03판), 강의·실습 내용은 받은 컨플루언스 자료(`course/ChapterNN/code/raw/` Python, `course/ChapterNN/slides/` PDF)다.
7. **YAGNI — 시킨 것만 만든다.** 요청하지 않은 기능·파일·설명·안내를 덧붙이지 않는다.
   근거 없는 내용(수업 진행, 수강생 반응, 사내 환경 등)을 상상해서 쓰지 않는다. 필요해 보이면 먼저 묻는다.
8. **`.env*` 파일의 주석은 영어(ASCII)로 쓴다.** 한글 주석이 있으면 강의장 윈도우 PC에서 옛 메모장 등이 cp949로 저장할 때 `import config`가 깨진다. ASCII만 담으면 어떤 방식으로 저장해도 바이트가 같다. 텍스트 파일을 읽고 쓰는 코드도 늘 `encoding="utf-8"`을 넣는다(윈도우 기본은 cp949). 둘 다 `dev/tests/test_encoding.py`가 검사한다.

## 4. 알려진 결함

2026-09-21 전수 감사 결과. 우선순위 높은 것만:

- `course/Chapter01/code/raw/04-langgraph/04_human_in_the_loop.py` — "거부" 시나리오가 메일을 **실제로 전송**한다. `update_state` 누락.
- `course/Chapter02/code/raw/01-mcp/` — 서버는 SSE, 클라이언트는 stdio. 슬라이드의 SSE 설정이 한 번도 실행되지 않는다.
- `course/Chapter02/code/raw/03-langgraph-advanced/03_memory_store.py` — `compile()`에 checkpointer·store 누락. 슬라이드 3-4 p7과 화면이 다르다.
- `course/Chapter02/code/raw/06-capstone/` — `mcp_server.py`와 `skills/`가 정답본에만 있다. 배점 20점이 배포본에서 불가능하다.
- 기존 `course/Chapter02/code/solution/06-capstone/`에는 배점 대상인 Streamlit UI가 없다.
- 원본 A2A 코드와 현재 SDK 1.x의 API가 다르다. 기존 raw/solution은 별도 이관 대상이다.
- `course/Chapter02/code/solution/06-capstone/solution.py` — `skills=['skills/researcher/']`가 SKILL.md가 든 폴더를 가리켜 deepagents 0.7.18이 skill을 0개 찾는다. 오류 없이 돌지만 skill 양식을 따르지 않는다. 수강생용 `course/Chapter02/capstone/`에서는 skill 폴더를 한 단계 더 넣어 고쳤다(2026-09-28).
- 사내 게이트웨이의 도구 호출(`bind_tools`)·구조화 출력이 확인되지 않았다. M2의 MCP·A2A·Harness(deepagents)·캡스톤은 모든 단계가 도구 호출이라 강의장 사전 점검 1순위다.

## 5. 검증

`uv sync --extra notebooks` 후 `uv run --extra notebooks python -m unittest discover -s dev/tests -p 'test_*.py'`로 환경 분기·실습 경로를 검사한다. 기본은 외부 API 없는 모드이며 실제 모델·Langfuse·사내 CodeMate 확인은 분리해 기록한다. 노트북의 키·출력은 커밋하지 않는다.
