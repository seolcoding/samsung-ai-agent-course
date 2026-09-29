# 통합 교안 개념 그림 템플릿

`$imagegen`은 **개념의 차이·상황·비유**를 직관적으로 보여 줄 때 쓴다. 도구 연결, 데이터 흐름, 상태 변경처럼 위치와 순서가 정확해야 하는 그림은 [`flow_diagram.dot`](flow_diagram.dot)을 복사해 그린다. 노트북에서는 두 방식 모두 그림 바로 아래에 설명을 붙인다.

## 생성 지시 틀

아래 대괄호만 주제에 맞게 바꾸고 나머지 스타일은 유지한다. 그림 안에 글자를 넣지 않고 번호·뜻은 노트북 본문에 적는다.

```text
Use case: scientific-educational
Asset type: wide concept illustration for section [의미 번호와 주제] in a beginner Korean AI Agent Jupyter lesson
Primary request: [수강생이 구별해야 할 한 가지 개념 차이 또는 상황을 구체적으로 묘사]
Style/medium: clean editorial illustration with crisp shapes, friendly but professional, suitable for a corporate training room
Composition/framing: wide 16:9, balanced, generous margins, readable when projected; use two panels only when comparing two cases
Color palette: restrained cobalt blue, teal, warm orange accents on an off-white background
Text: none
Constraints: no logos, no brands, no readable words, no tiny UI text, no invented data or metrics, no watermarks
```

## 노트북의 그림 설명 틀

```text
![그림에 실제로 보이는 대상과 관계를 한 문장으로 설명](attachment:그림.png)

**그림 [의미 번호].1 — [그림의 주장].** [왼쪽·오른쪽 또는 색상·요소가 무엇을 뜻하는지 설명].
**보면서 확인:** [수강생이 그림에서 찾아야 할 것].
**표현의 한계:** [삽화가 실제 코드·데이터·순서를 보증하지 않는 부분].
```

그림이 없어도 이해되는 장식 이미지는 만들지 않는다. 한 그림에는 주장이 하나여야 한다. 생성 결과에 잘못된 글자·UI·연결이 있으면 수업에 넣지 않는다. 최종 PNG는 `course/ChapterNN/assets/`에 두고 노트북에는 Markdown attachment로 포함한다. 생성 원본과 노트북의 설명이 서로 같은 개념을 가리키는지 확인한다.
