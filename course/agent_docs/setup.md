# 설치와 설정

수강생 PC에서 노트북을 처음 실행할 때, 또는 설치·설정이 꼬였을 때 이 순서대로 확인한다. 명령은 모두 **저장소 맨 위 폴더**(`pyproject.toml`이 있는 곳, `course/`의 위)에서 실행한다.

## 1. 파이썬 환경(uv)

1. `uv --version`이 나오는지 본다. 없으면 uv를 설치한다(사내 PC는 강사 안내 방법을 따른다).
2. 패키지를 설치한다.

   ```
   uv sync --extra notebooks
   ```

   - 저장소 맨 위에 `.venv/`가 생긴다. 파이썬 버전은 3.12 이상이다(`pyproject.toml`의 `requires-python`).
   - `config` 패키지(`course/config/`)도 이때 함께 설치된다. 그래서 노트북 어디서든 `import config.llm`이 된다.
   - 퀴즈(`jupyterquiz`), 커널(`ipykernel`)도 `notebooks` 묶음에 들어 있다.
3. 설치를 확인한다.

   ```
   uv run python -c "import config.llm, langchain_openai, jupyterquiz; print('ok')"
   ```

## 2. VS Code 커널

- 노트북 오른쪽 위 "커널 선택"에서 저장소의 `.venv`(Python 3.12)를 고른다.
- 다른 파이썬(시스템 파이썬, conda 등)을 고르면 `No module named 'config'` 같은 오류가 난다.
- 커널을 바꾼 뒤에는 맨 위 셀부터 다시 실행한다.

## 3. `.env` (연결 설정)

- `.env.sample`을 복사해 저장소 맨 위에 **`.env`** 라는 이름으로 만든다. 노트북은 이 이름만 읽는다.
  - 노트북 폴더에서 위쪽 폴더로 올라가며 `.env`를 찾는다(`find_dotenv`). 그래서 저장소 맨 위에 두면 된다.
- 값은 강사가 알려 준다. 키·토큰 값은 화면에 출력하거나 다른 파일·채팅에 붙여 넣지 않는다.
- 어떤 이름이 필요한지는 환경에 따라 다르다.

| 설정 | 값 | 함께 있어야 하는 이름 |
|---|---|---|
| `LLM_PROVIDER` | `openai`(사외) | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| | `samsung`(사내, 기본값) | `api_base_url`, `model`, `credential_key`, `send_system_name`, `user_id` |
| `EMBED_PROVIDER` | `openai` | `OPENAI_API_KEY`, `OPENAI_EMBEDDING_MODEL` |
| | `samsung` | `embedding_api_url`, `embedding_x_dep_ticket` |
| `RAG_PROVIDER` | `mock`(연습용, 네트워크 없음) | 없음 |
| | `samsung` | `search_url`, `rag_credential_key`, `rag_api_key` |

- `LLM_PROVIDER`를 비워 두면 `samsung`으로 동작한다. 사외 PC에서 사내 값을 쓰면 연결되지 않는다.
- 실습 노트북 맨 위 "환경 점검" 셀이 빠진 이름의 **개수와 이름**만 알려 준다(값은 보여 주지 않는다). 빠진 이름을 `.env`에 채운 뒤 그 셀을 다시 실행한다.

## 4. 모델·임베딩 부르는 법

- 모델: `from config.llm import get_llm` → `llm = get_llm()`
- 임베딩: `from config.embeddings import get_embeddings` → `get_embeddings()`
- 주소·모델 이름·키를 코드에 직접 쓰지 않는다. 환경을 바꿀 때는 `.env`만 바꾼다.

## 5. 원본 코드(.py)를 직접 실행할 때

노트북이 아니라 `code/raw/…`의 파일을 실행해야 하면 저장소 맨 위에서 실행한다.

```
uv run python course/Chapter01/code/raw/01-llm-api/01_requests.py
```
