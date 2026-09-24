# 삼성전자 DS AI Agent 교육

업무 자료·실습 코드·교안을 모은 프로젝트다. 작업 위치는 `~/100_Dev/samsung_ds_ai_developer`이다.

## 자료 찾기

| 위치 | 내용 |
| --- | --- |
| [작업 지침](AGENTS.md) | 교육 개편 방향, 실행 환경, 작업 규칙, 기존에 발견한 결함 |
| [업무 맥락](context/PROJECT_CONTEXT.md) | 메일 기반 일정·관계자·환경 안내. 2026-09-06 시점 기록 |
| [커리큘럼](context/CURRICULUM.md) | 전달받은 커리큘럼 비교 |
| [자료 출처](context/SOURCES.md) | 메일과 첨부자료 출처 |
| [교안 PDF](99_pdf/) | 교안 정본 14개 |
| [M1 실습](Chapter01/) | 1·2일차 실습 |
| [M2 실습](Chapter02/) | 3·4일차 실습 (`00-review/` ~ `06-capstone/`) |
| [정답본](solution/) | 실습 정답 |
| [공통 설정](config/) · [패키지 목록](pyproject.toml) | LLM 연결 코드와 Python 의존성 |
| [메일·첨부 원본](private/) | 로컬 보관 자료. Git 제외 |
| [전달받은 ZIP](source_archives/) | 원본 ZIP 2개. Git 제외 |

## 자료 시점

`context/`는 9월 6일 수집 기록을 보존한다. 9월 17일 확정된 실습 개편 방향과 9월 21일 코드 점검 내용은 [AGENTS.md](AGENTS.md)에 있다. 폴더 통합 과정에서 교육 내용이나 실습 코드는 수정하지 않았다.

## Git과 테스트

통합 브랜치는 `organize/consolidate-20260924`다. 기존 코드 저장소와 업무 자료 저장소의 이력을 함께 보존했다. `main`은 통합 전 코드 상태를 유지한다.

격리 테스트 환경은 아직 만들지 않았다. 후속 테스트는 통합 브랜치를 기준으로 별도 작업 폴더와 실행 환경을 구성한다. `private/`와 `source_archives/`는 Git 복제나 worktree 생성 시 자동으로 복사되지 않는다.

## 통합 기록

2026-09-24 아래 자료를 이 위치로 모았다.

- `~/200_Vault/220_Projects/samsung_elec_agent`: 업무 문서와 원본 첨부.
- `~/200_Vault/220_Projects/samsung_ds_ai_developer`: 전달받은 교안 ZIP.
- 기존 `2026-AI-PD-main/`: Git 저장소, 실습 코드와 교안 PDF.

전체 백업·이동 목록·복구 절차는 `~/_MANIFESTS/samsung_ds_consolidation_20260924/`에 있다. 기존 폴더의 잔여 자료는 `~/000_Inbox/090_To_Delete/samsung_ds_consolidation_20260924/`에 보관했다.
