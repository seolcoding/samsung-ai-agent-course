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

1. 저장소 맨 위의 `.env.sample`을 같은 자리에 **`.env`** 라는 이름으로 복사한다. 노트북은 이 이름만 읽는다(노트북 폴더에서 위로 올라가며 `.env`를 찾는다).
2. `.env`의 **① 실행 환경**에서 하나만 남긴다.
   - 강의장(삼성 인트라넷) PC: `[사내]` 세 줄 — `LLM_PROVIDER=samsung`, `EMBED_PROVIDER=samsung`, `RAG_PROVIDER=samsung`. 견본의 기본값이다.
   - 사내망 밖: `[사외]` 세 줄 — `openai`, `openai`, `mock`. 사내 세 줄 앞에는 `#`을 붙인다.
3. 고른 환경의 칸만 채운다. **② 사내 값**은 사내 교육 페이지의 환경·API 키 안내에 있고, **③ 사외 값**은 강사가 알려 준다.
4. 노트북 맨 위 "환경 점검" 셀을 실행한다. "준비 완료"가 나오면 끝이다. 빠진 이름이 나오면 그 이름을 채우고 다시 실행한다.

- 값 뒤에 `# 설명`을 붙이지 않는다. 빈 값 뒤의 주석은 값으로 읽힌다. 설명은 윗줄에 쓴다.
- 키·토큰 값은 화면에 출력하거나 다른 파일·채팅에 붙여 넣지 않는다. 있는지만 확인한다.
- 환경별로 있어야 하는 이름:

| 설정 | 값 | 함께 있어야 하는 이름 |
|---|---|---|
| `LLM_PROVIDER` | `samsung`(사내, 비워 두어도 이 값) | `api_base_url`, `model`, `credential_key`, `send_system_name`, `user_id` |
| | `openai`(사외) | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| `EMBED_PROVIDER` | `samsung` | `embedding_api_url`, `embedding_x_dep_ticket` |
| | `openai` | `OPENAI_API_KEY`, `OPENAI_EMBEDDING_MODEL` |
| `RAG_PROVIDER` | `samsung` | `search_url`, `rag_credential_key`, `rag_api_key` (`index_name`은 견본 값 그대로) |
| | `mock`(연습용, 네트워크 없음) | 없음 |

- 사내 주소는 끝부분을 붙이지 않고 적는다. 코드가 `api_base_url` 뒤에 `/chat/completions`, `embedding_api_url` 뒤에 `/v1/embeddings`를 붙인다.

## 4. 모델·임베딩 부르는 법

- 모델: `from config.llm import get_llm` → `llm = get_llm()`
- 임베딩: `from config.embeddings import get_embeddings` → `get_embeddings()`
- 주소·모델 이름·키를 코드에 직접 쓰지 않는다. 환경을 바꿀 때는 `.env`만 바꾼다.

## 5. 원본 코드(.py)를 직접 실행할 때

노트북이 아니라 `code/raw/…`의 파일을 실행해야 하면 저장소 맨 위에서 실행한다.

```
uv run python course/Chapter01/code/raw/01-llm-api/01_requests.py
```
