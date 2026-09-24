# 통합 교안 작성 규칙

최종 수업 교안은 `lessons/`의 주제별 주피터 노트북이다. 한 권에서 **슬라이드 화면 → 설명 → 실행 코드 → CodeMate 실습 → 결과 검토**가 이어지도록 만든다. 기존 PDF, 슬라이드 해설 노트북, Python 실습은 내용을 가져오는 원본으로 유지한다.

## 폴더와 이름

```text
lessons/
  _template.ipynb
  Chapter01/
    day01/
      1-1-ai-agent-design-thinking.ipynb
      1-2-development-environment-and-llm-api-mechanism.ipynb
      ...
    day02/
      2-1-langgraph-theory-and-advanced-features.ipynb
      ...
  Chapter02/
    day01/
      3-1-course-one-review-and-advanced-direction.ipynb
      ...
    day02/
      4-1-harness-engineering-core-principles.ipynb
      ...
```

PDF 한 개에 최종 노트북 한 개를 대응시킨다. 파일명은 `docs/raw/`의 PDF 이름에서 확장자만 `.ipynb`로 바꾼다. 각 노트북은 해당 PDF와 `docs/notebooks/`의 해설, 관련 `src/raw/` 실습을 참고한다. 현재 PDF는 14개이므로 완성 목표도 14권이다. 완성 전에는 빈 노트북을 수강생용 경로에 만들지 않는다.

## 한 권의 흐름

1. 제목, 오늘의 학습 목표, 실행 환경을 짧게 적는다.
2. 강의에 쓰는 슬라이드 **화면을 노트북 안에 첨부 이미지로 넣고** PDF 쪽수를 적는다. PDF 링크만 걸어 두면 통합본이 아니다. PDF의 강의 내용을 빠뜨리지 않도록 모든 강의용 쪽을 대응시키고, 반복·표지 등 생략한 쪽은 이유를 기록한다.
3. 슬라이드 바로 아래에 초심자용 설명과 코드가 연결되는 이유를 적는다.
4. 코드는 실행 가능한 셀로 옮기되, 셀을 위에서부터 실행할 수 있게 순서를 정한다. API 호출·서버 시작·파일 쓰기는 실행 조건과 예상 결과를 먼저 적는다. 실행 결과와 비밀값은 저장하지 않는다.
5. CodeMate에 줄 작업 지시와 생성 결과를 검토할 질문을 둔다. 수강생이 단순히 빈칸을 채우게 하지 않는다.
6. 끝에 요약, 확인 문제, 원본 PDF·해설·실습 파일 경로를 적는다.

슬라이드 이미지는 노트북의 Markdown 셀에 **attachment**로 넣는다. 그러면 노트북 파일 하나를 옮겨도 이미지가 따라간다. 슬라이드를 처음에 몰아넣지 않고 각 설명과 실습 옆에 배치한다. 슬라이드 한 장에 설명·실습이 여럿이면 틀의 1~4절을 반복한다. 별도 터미널이 필요한 MCP 서버나 Streamlit은 실행 코드를 억지로 셀에 넣지 않고 노트북에 명령·화면·검토 기준을 둔다.

## 작성 순서와 확인

`lessons/_template.ipynb`를 복사해 위 이름으로 저장한다. 먼저 한 주제를 완성해 수업 흐름을 확인한 뒤 같은 틀을 나머지에 적용한다. 각 권을 만들 때 원본 PDF 쪽수, 실습 경로, 코드 동작, 수강생용·정답본의 차이를 확인한다. 내용이 바뀌면 관련 `src/raw/`, `src/solution/`, `docs/notebooks/`, `lessons/`를 함께 살핀다.

`lessons/`는 수강생이 여는 완성 교안이다. 제작 중인 원고는 최종 경로에 두지 않고 현재 작업 브랜치에서 편집한다. 수업 직전에는 컨플루언스 최신 수정사항과 사내 CodeMate 실제 화면을 대조한다.
