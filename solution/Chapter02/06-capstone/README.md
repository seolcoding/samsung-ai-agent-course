# 캡스톤 프로젝트: 리서치 자동화 멀티 에이전트 시스템

## 시나리오

사용자가 주제를 입력하면 다음 흐름으로 자동 처리된다:

```
사용자 입력
    ↓
Supervisor (skills.md 기반)
    ├→ Researcher  (웹 검색 + RAG)
    ↓ (완료 보고)
    ├→ Writer      (초안 작성)
    ↓ (완료 보고)
    ├→ [Human Approval] ← 사용자가 초안 승인/수정 요청
    ↓ (승인)
    └→ 최종 결과 출력 (Streamlit UI)
```

## 구현 목표

1. **skills.md** — Supervisor와 각 Agent의 역할 및 행동 규칙 정의
2. **MCP 연동** — Researcher가 파일시스템 MCP로 로컬 문서도 검색
3. **Human-in-the-Loop** — Writer 초안 완료 후 사용자 승인 단계 포함
4. **Streamlit UI** — 전체 흐름을 웹 인터페이스로 확인

## 파일 구조

```
Chapter02/06-capstone/
  starter.py      ← 수강생 실습 시작점
solution/Chapter02/06-capstone/
  README.md       ← 이 파일
  solution.py     ← 정답 예시
  mcp_server.py   ← 정답 예시의 MCP 서버
  skills/         ← 정답 예시의 스킬
```

## 구현 체크리스트

- [ ] State 설계: `topic`, `research_result`, `draft`, `approved` 필드 포함
- [ ] Researcher 노드: `search_web` + MCP 파일시스템 도구 활용
- [ ] Writer 노드: 리서치 결과로 마크다운 포스트 작성
- [ ] Supervisor 노드: `RouteDecision` 스키마로 흐름 제어
- [ ] Human Approval: `interrupt_before=['writer']` 또는 별도 approval 노드
- [ ] MemorySaver 연결: 세션 유지
- [ ] Streamlit: 진행 상황 단계별 표시, 최종 결과 마크다운 렌더링

## 핵심 힌트

```python
# Supervisor 라우팅 스키마
class RouteDecision(BaseModel):
    next: Literal['researcher', 'writer', 'approval', 'FINISH']
    reason: str

# Human Approval 노드 패턴
app = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=['approval'],
)
# 1단계: researcher → writer 까지 실행 후 중단
# 2단계: 사용자 확인 후 app.invoke(None, config) 로 재개
```

## 평가 기준

| 항목 | 배점 |
|------|------|
| Supervisor 라우팅 정상 동작 | 30점 |
| Human-in-the-Loop 구현 | 25점 |
| MCP 도구 연동 | 20점 |
| Streamlit UI 구현 | 15점 |
| skills.md 규칙 반영 | 10점 |
