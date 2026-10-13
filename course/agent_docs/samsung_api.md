# 사내(삼성) LLM·임베딩을 LangChain에서 쓰는 법

사내 모델로 새 코드(노트북 셀, 캡스톤, 새 Agent)를 만들 때 이 문서를 따른다. 사내 API는 사내망에서만 동작한다.

## 1. 한 줄 요약

- **LLM**: 사내 게이트웨이는 OpenAI 호환 API다. LangChain의 `ChatOpenAI`에 사내 주소(`base_url`)와 인증 헤더(`default_headers`)를 넣어 쓴다. 이미 `config.llm.get_llm()`이 그렇게 만들어 준다.
- **임베딩**: 사내 임베딩은 REST API(`POST …/v1/embeddings`)다. LangChain 모듈이 따로 없으므로 `langchain_core.embeddings.Embeddings`를 상속한 작은 클래스로 감싼다. 이미 `config.embeddings.get_embeddings()`가 그렇게 만들어 준다.
- 그래서 이 저장소 안에서는 **직접 만들지 말고 아래 두 줄을 쓴다.** `.env`의 `COURSE_ENV`만 바꾸면 사내(`samsung`)·사외(`out`, OpenAI)가 저절로 바뀐다.

```python
from config.llm import get_llm
from config.embeddings import get_embeddings

llm = get_llm()                  # LangChain ChatModel (ChatOpenAI)
embeddings = get_embeddings()    # LangChain Embeddings
```

## 2. 참조할 코드

| 알고 싶은 것 | 볼 파일 |
|---|---|
| 사내 주소·인증 헤더를 만드는 곳(LLM·임베딩·RAGaaS 공통) | `course/config/samsung.py` (`llm_config`, `embedding_config`, `ragaas_config`) |
| `get_llm()`: 사내/사외 LLM 고르기 | `course/config/llm.py` |
| `get_embeddings()`: 사내 임베딩 LangChain 클래스 | `course/config/embeddings.py` (`_SamsungEmbeddings`) |
| `.env`를 읽고 `COURSE_ENV`로 연결 방식 정하기 | `course/config/__init__.py` |
| 사내 LLM을 HTTP로 직접 부르기(requests) | `course/Chapter01/code/solution/01-llm-api/01_requests.py` |
| 사내 LLM을 OpenAI SDK로 부르기 | `course/Chapter01/code/solution/01-llm-api/02_openai.py` |
| `get_llm()`으로 invoke·stream | `course/Chapter01/code/solution/01-llm-api/03_langchain.py` |
| 사내 임베딩 클래스를 직접 만드는 수업 코드 | `course/Chapter01/code/solution/03-rag/02_embeddings.py` (`SamsungEmbeddings`) |
| 임베딩 → Chroma 벡터 저장소 | `course/Chapter01/code/solution/03-rag/03_vector_store.py` |
| 임베딩 → retriever → RAG 체인(LCEL) | `course/Chapter01/code/solution/03-rag/04_langchain_rag.py` |
| 사내 RAGaaS 검색 | `course/config/ragaas.py` (`post_ragaas`), `course/Chapter01/code/solution/03-rag/05_ragaas.py` |
| Agent에서 `get_llm()` 쓰기(구조화 출력 포함) | `course/Chapter02/capstone/starter.py` |

## 3. LLM을 "삼성풍"으로 쓰는 법

`get_llm()`이 사내 설정일 때 만드는 것은 아래와 같다(`course/config/llm.py`).

```python
from langchain_openai import ChatOpenAI
from config.samsung import llm_config

samsung = llm_config()           # .env의 api_base_url, model, credential_key, send_system_name, user_id
llm = ChatOpenAI(
    api_key="samsung-gateway",   # SDK 필수값만 채운다. 실제 인증은 x-dep-ticket 헤더
    base_url=samsung["base_url"],
    model=samsung["model"],
    default_headers=samsung["headers"],
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)
```

- **인증은 헤더로 한다.** `x-dep-ticket`(= `credential_key`), `Send-System-Name`, `User-Id`, `User-Type: AD_ID`, `Prompt-Msg-Id`·`Completion-Msg-Id`(새 UUID). `llm_config()`가 모두 만든다. 메시지 ID는 `llm_config()`를 부를 때(= `get_llm()`을 부를 때) 한 번 정해진다.
- **`api_key`는 아무 글자나 넣는다.** OpenAI SDK가 빈 값을 받지 않아서 채울 뿐이다. 진짜 키를 넣지 않는다.
- **주소에 `/chat/completions`를 붙이지 않는다.** `api_base_url`은 앞부분만 적고, SDK가 뒤를 붙인다. requests로 직접 부를 때만 코드에서 붙인다(`01_requests.py`).
- **생각 모드는 끈다.** LangChain에서는 `extra_body={"chat_template_kwargs": {"enable_thinking": False}}`, requests로 부를 때는 본문에 `"include_reasoning": False`를 넣는다(원본 수업 코드 그대로).
- **옵션은 `get_llm()`에 넘긴다.** 예: `get_llm(temperature=0)`. 넘긴 값은 `ChatOpenAI`로 그대로 간다. `model`을 넘기면 `.env`의 모델 대신 그 모델을 쓴다.
- **LangChain 기능은 그대로 쓴다.** `invoke`, `stream`, `|`(LCEL), LangGraph 노드, `create_agent`, deepagents 모두 `llm` 하나를 넘기면 된다.
- **확인되지 않은 것:** 사내 게이트웨이에서 도구 호출(`bind_tools`)과 구조화 출력(`with_structured_output`), OpenAI SDK의 `client.responses…`가 되는지는 아직 확인되지 않았다. 안 되면 [troubleshooting.md](troubleshooting.md)의 해당 줄 순서대로 진단한다. 코드를 바꿔 우회하지 않는다.

## 4. 사내 임베딩을 LangChain과 맞추는 법

LangChain의 벡터 저장소(Chroma 등)·retriever는 `Embeddings` 인터페이스만 본다. 메서드 두 개만 있으면 된다.

| 메서드 | 받는 것 | 돌려주는 것 |
|---|---|---|
| `embed_documents(texts)` | 문장 목록 `list[str]` | 벡터 목록 `list[list[float]]` (같은 순서) |
| `embed_query(text)` | 문장 하나 `str` | 벡터 하나 `list[float]` |

사내 임베딩 API 규칙(`config.samsung.embedding_config()`, 원본 `02_embeddings.py` 기준):

- 주소: `<embedding_api_url>/v1/embeddings`, `POST`
- 헤더: `Content-Type: application/json`, `x-dep-ticket: <embedding_x_dep_ticket>`
- 본문: `{"input": ["문장1", "문장2", ...]}` — **한 번에 10개까지** 보낸다. 더 많으면 10개씩 나눠 보낸다.
- 응답: `{"data": [{"embedding": [...]}, ...]}` — 보낸 순서대로 `data[i]["embedding"]`을 모은다.

`course/config/embeddings.py`의 `_SamsungEmbeddings`가 이 규칙대로 만든 클래스다. 쓰는 쪽에서는 사내·사외 구분 없이 같다.

```python
from langchain_chroma import Chroma
from config.embeddings import get_embeddings

embeddings = get_embeddings()
vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
```

- 같은 벡터 저장소에는 **같은 임베딩으로 만든 벡터만** 넣는다. 사외(OpenAI)로 만든 Chroma 폴더를 사내 임베딩으로 검색하면 차원이 달라 오류가 나거나 엉뚱한 결과가 나온다. `COURSE_ENV`를 바꿨으면 저장소를 다시 만든다.
- 사내 RAGaaS는 서버가 임베딩까지 해 주므로 이 클래스가 필요 없다. `config.ragaas.post_ragaas()`를 쓴다(자세한 것은 [ragaas.md](ragaas.md)).

## 5. 이 저장소 밖(새 프로젝트)에서 쓸 때

`config` 패키지가 없는 새 프로젝트에서는 아래를 그대로 옮겨 쓴다. 값은 이 저장소 `.env`와 같은 이름으로 그 프로젝트의 `.env`에 둔다. 주소·키를 코드에 적지 않는다.

```python
import os
import uuid

import requests
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI

load_dotenv(encoding="utf-8")


def samsung_llm(**kwargs) -> ChatOpenAI:
    """사내 LLM 게이트웨이를 LangChain ChatModel로 만든다."""
    kwargs.setdefault("model", os.environ["model"])
    return ChatOpenAI(
        api_key="samsung-gateway",
        base_url=os.environ["api_base_url"],
        default_headers={
            "x-dep-ticket": os.environ["credential_key"],
            "Send-System-Name": os.environ["send_system_name"],
            "User-Id": os.environ["user_id"],
            "User-Type": "AD_ID",
            "Prompt-Msg-Id": str(uuid.uuid4()),
            "Completion-Msg-Id": str(uuid.uuid4()),
        },
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        **kwargs,
    )


class SamsungEmbeddings(Embeddings):
    """사내 임베딩 REST API를 LangChain Embeddings로 감싼다. 한 번에 10개씩 보낸다."""

    def __init__(self, batch: int = 10):
        self.url = os.environ["embedding_api_url"].rstrip("/") + "/v1/embeddings"
        self.headers = {"Content-Type": "application/json", "x-dep-ticket": os.environ["embedding_x_dep_ticket"]}
        self.batch = batch

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = []
        for i in range(0, len(texts), self.batch):
            resp = requests.post(self.url, json={"input": texts[i:i + self.batch]}, headers=self.headers, timeout=120)
            resp.raise_for_status()
            result.extend(item["embedding"] for item in resp.json()["data"])
        return result

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
```

- 필요한 패키지: `langchain-openai`, `langchain-core`, `requests`, `python-dotenv`.
- 값이 없으면 `KeyError: '<이름>'`이 난다. 그 이름을 `.env`에 채우게 안내한다. 값을 대신 지어내지 않는다.

## 6. 하지 말 것

- 주소·모델 이름·키·티켓을 코드에 직접 쓰지 않는다. 늘 `.env`에서 읽는다.
- 키·티켓 값을 출력하거나 로그·채팅·파일에 남기지 않는다. 확인은 `uv run python -m config.check --json`(이름만 나옴)으로 한다.
- 이 저장소 안에서는 `course/config/`를 고치지 않는다. 사내 연결이 안 되면 [setup.md](setup.md)의 설정 점검과 [troubleshooting.md](troubleshooting.md)부터 본다.
