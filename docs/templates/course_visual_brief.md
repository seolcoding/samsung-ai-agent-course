# 통합 교안 그림 제작 템플릿

이 과정의 새 개념 그림은 [OpenAI GPT Image 2.5 프롬프팅 가이드](https://developers.openai.com/api/docs/guides/image-prompting)의 교육용 시각자료 작성 방식을 참고한다. 대상·학습 목표·필수 요소·관계를 먼저 정하고, 구도와 표현 제약을 고정한 뒤 결과를 검토한다. 수정할 때는 바꿀 요소 하나와 유지할 요소를 명시한다. 확인일: 2026-09-24.

실제 제작 도구는 내장 `image_gen`이다. 도구에서 내부 모델 식별자를 제공하지 않으므로 특정 API 모델로 생성했다고 표기하지 않는다. 아래는 이 강의에 맞춰 작성한 제작 규격이다.

## 공통 시각 규격

- 가로 16:9, 밝은 아이보리 배경, 큰 여백, 선명한 평면 일러스트.
- 모델·판단은 파랑, 자료·관찰은 청록, 실행·제어는 주황으로 표현한다.
- 패널은 최대 3개, 한 그림은 한 가지 질문에 답한다.
- 그림 안에는 짧은 영문 명사만 쓴다. 자세한 한국어 설명은 바로 아래 Markdown에 둔다.
- 시간·시각·강의 분량·장식용 숫자를 그림에 넣지 않는다.
- 실제 화면·사내 시스템·고객사 운영 데이터를 닮은 가짜 화면을 만들지 않는다.
- 연결 순서가 학습 목표인 도식은 `.dot` 원본도 제공한다.

## 생성 요청 틀

```text
Use case: scientific-educational
Audience: Korean adult beginners learning AI Agent development
Lesson objective: [그림으로 이해할 단 하나의 관계]
Asset type: wide concept plate embedded in an executable Jupyter lesson
Required components: [반드시 들어갈 대상]
Required relationships: [방향, 경계, 포함, 비교 관계]
Composition: [패널 수와 배치], landscape 16:9, generous whitespace
Style: crisp flat editorial illustration, consistent icon proportions, no photorealism
Palette: off-white background; cobalt for model/reasoning, teal for evidence, warm orange for execution/control
Text verbatim: [짧은 영문 라벨의 정확한 목록]
Constraints: [틀리면 안 되는 관계]; no extra text, logos, watermark, timestamps, metrics, fake UI
```

## 삽입 규칙

그림은 노트북에 attachment로 포함한다. 이미지 바로 아래에는 다음 설명을 쓴다.

```text
그림 [주제 번호].1 — [한 문장으로 표현한 핵심]
[위치·색·대상이 무엇을 뜻하는지 설명]
보면서 확인: [그림에서 찾아볼 관계]
표현 범위: [비유 또는 생략한 단계가 있으면 짧게 설명]
```

최종 이미지와 생성 프롬프트는 각각 `lessons/assets/suite/`, `docs/templates/course_visual_prompts.json`에 보관한다. 원본 경로와 사용 위치는 `docs/LESSON_SOURCES.md`에 기록한다.
