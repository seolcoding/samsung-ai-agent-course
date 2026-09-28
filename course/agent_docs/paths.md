# 경로 규칙

노트북·코드가 파일을 못 찾을 때 이 규칙으로 확인한다. 경로를 고칠 때도 이 규칙을 지킨다.

## 폴더 구조

```
<저장소 맨 위>/                 pyproject.toml, uv.lock, .env(직접 만듦), .venv/(uv sync가 만듦)
  course/
    config/                    모델·임베딩·RAG 연결 설정 패키지(챕터 공통, import config.…)
    agent_docs/                이 문서들
    ChapterNN/
      notebooks/               수업 노트북 + data/(실습 자료)
      assets/                  이 챕터 노트북의 도구(widgets.py, 슬라이드 뷰어, 퀴즈 파일)
      slides/                  강의 슬라이드 PDF
      code/raw/, code/solution/  받은 원본 코드와 정답
```

## 노트북 안의 경로는 "노트북이 있는 폴더" 기준

VS Code는 노트북을 그 노트북이 있는 폴더(`course/ChapterNN/notebooks/`)에서 실행한다. 그래서:

| 쓰는 곳 | 코드 | 가리키는 곳 |
|---|---|---|
| 준비 셀 | `sys.path.insert(0, '..')` 후 `from assets.widgets import …` | `course/ChapterNN/assets/` |
| 퀴즈 | `show_quiz("../assets/quizzes/<권>/<문제>.json")` | `course/ChapterNN/assets/quizzes/` |
| 실습 자료 | `"data/meritz_pet_insurance.pdf"` | `course/ChapterNN/notebooks/data/` |
| 슬라이드 | `show_slides("1-2", [쪽])` | `course/ChapterNN/slides/` 아래 `1-2-*.pdf`를 자동으로 찾음 |
| 설정 | `import config.llm` | 설치된 패키지(`course/config/`). 경로와 상관없음 |
| `.env` | 자동(`find_dotenv`) | 노트북 폴더에서 위로 올라가며 처음 만나는 `.env` |
| 앱 파일(2-3) | `%%writefile app.py` | 노트북 폴더에 생긴다 |

- 지금 폴더 확인: 셀에서 `import os; print(os.getcwd())`. `…/course/ChapterNN/notebooks`가 나와야 한다.
- 다른 폴더가 나오면(VS Code 설정 `jupyter.notebookFileRoot`를 바꾼 경우 등) 노트북 맨 위에 `%cd <저장소>/course/ChapterNN/notebooks`를 한 번 실행하거나, 설정을 `${fileDirname}`(기본값)으로 되돌린다.
- 절대 경로(`C:\Users\…`, `/Users/…`)를 코드에 쓰지 않는다. 사람마다 달라서 다른 PC에서 깨진다.
- 경로에는 `Path("data") / "파일"`처럼 `pathlib`을 쓰면 윈도우·맥 모두 동작한다.

## 원본 코드(.py) 실행 위치

`code/raw/`, `code/solution/`의 파일은 **저장소 맨 위에서** 실행하는 것을 기준으로 작성되어 있다(예: MCP 클라이언트가 서버 파일을 `course/Chapter02/code/raw/…` 경로로 띄운다).

## 하지 말 것

- `course/ChapterNN/code/`, `assets/`, `config/`의 파일을 옮기거나 이름을 바꾸지 않는다. 노트북이 이 위치를 기준으로 만들어져 있다.
- 노트북을 다른 폴더로 복사해서 쓰지 않는다. 복사하면 `..`·`data/` 경로가 깨진다. 복사해야 하면 같은 `notebooks/` 폴더 안에 둔다.
