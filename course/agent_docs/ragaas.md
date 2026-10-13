# 사내 RAGaaS 쓰는 법

사내 RAGaaS(RAG as a Service)로 문서를 올리고 검색하는 코드를 만들 때 이 문서를 따른다. 1-4 RAG 실습과 4-3 캡스톤이 쓴다. 사내 RAGaaS는 사내망에서만 동작한다.

## 1. 한 줄 요약

- RAGaaS는 **청킹·임베딩·벡터 저장소를 서버가 대신 해 주는 REST API**다. 문서 올리기 한 번, 검색 한 번이면 된다. 임베딩 클래스(`get_embeddings()`)나 Chroma가 필요 없다.
- 이 저장소에서는 **`config.ragaas.post_ragaas(엔드포인트, payload)`로만 부른다.** 주소와 인증 헤더는 그 안에서 채운다.
- `.env`의 `COURSE_ENV=out`(사외)이면 네트워크 없이 같은 모양의 **모의 응답(mock)** 이 온다. 내용은 `[MOCK RAGaaS] …`로 시작하는 연습용 문장이다.

```python
import os
from config.ragaas import post_ragaas

payload = {
    "index_name": os.getenv("index_name"),
    "permission_groups": ["rag-public"],
    "query_text": "펫보험 보장 내용이 뭐야?",
    "num_result_doc": 3,
    "fields_exclude": ["v_merge_title_content"],
}
hits = post_ragaas("retrieve-rrf", payload).json()["hits"]["hits"]
context = "\n\n".join(hit["_source"]["merge_title_content"] for hit in hits)
```

## 2. 참조할 코드

| 알고 싶은 것 | 볼 파일 |
|---|---|
| 주소·인증 헤더 만들기 | `course/config/samsung.py` (`ragaas_config`) |
| 요청 보내기와 모의 응답 | `course/config/ragaas.py` (`post_ragaas`, `MockResponse`) |
| 올리기 → 검색 → LLM 답변 → 삭제 전체 흐름 | `course/Chapter01/code/solution/03-rag/05_ragaas.py` |
| Agent 도구로 감싸기(`@tool rag_search`) | `course/Chapter02/code/solution/06-capstone/solution.py` |
| 캡스톤에서 수강생이 채울 자리 | `course/Chapter02/capstone/starter.py` (`rag_search`) |
| 필요한 `.env` 이름과 뜻 | 저장소 맨 위 `.env.sample` (2) RAGaaS 칸 |

## 3. 연결 규칙

- 주소: `<search_url>/dsllmrag/elastic/v2/<엔드포인트>`, 모두 `POST`(JSON 본문). `search_url`에는 앞부분만 적는다.
- 헤더: `Content-Type: application/json`, `x-dep-ticket: <rag_credential_key>`, `api-key: <rag_api_key>`.
  - **두 값이 모두 있어야 한다.** 하나라도 빠지면 인증에 실패한다.
- 인덱스: `.env`의 `index_name`. 수업용 인덱스는 펫보험 약관(`.env.sample`의 견본 값)이다. 강사가 따로 말하지 않으면 바꾸지 않는다.
- 시간 제한: 문서 올리기 300초, 그 밖 30초(`post_ragaas`가 정한다).
- 실패하면 `post_ragaas`가 `raise_for_status()`로 HTTP 오류를 낸다. 응답을 조용히 넘기지 않는다.

## 4. 엔드포인트 세 가지

`post_ragaas`는 아래 세 이름만 받는다. 다른 이름을 넣으면 `ValueError: 지원하지 않는 RAGaaS 엔드포인트`가 난다.

### 문서 올리기 `insert-doc`

```python
payload = {
    "index_name": INDEX_NAME,
    "data": {
        "doc_id": "meritz_pet_insurance",   # 나중에 지울 때 쓰는 ID
        "title": "메리츠 펫보험 약관",
        "content": raw_text,               # PDF 등에서 뽑은 글자(문자열)
    },
    "chunk_factor": {                      # 청킹은 서버가 한다. 방식과 크기만 정한다
        "logic": "fixed_size",
        "chunk_size": 500,
        "chunk_overlap": 75,
        "separator": " ",
    },
}
post_ragaas("insert-doc", payload, api_key=RAG_API_KEY)
```

- RAGaaS는 글자만 받는다. PDF는 먼저 글자로 뽑는다(`05_ragaas.py`는 `PDFMinerLoader` 사용).
- 캡스톤은 문서를 올리지 않고 검색만 한다(`solution.py`).

### 검색 `retrieve-rrf`

```python
payload = {
    "index_name": INDEX_NAME,
    "permission_groups": ["rag-public"],
    "query_text": question,
    "num_result_doc": 3,                       # 받을 조각 수
    "fields_exclude": ["v_merge_title_content"],  # 벡터 값은 빼고 받는다
}
hits = post_ragaas("retrieve-rrf", payload, api_key=RAG_API_KEY).json()["hits"]["hits"]
texts = [hit["_source"]["merge_title_content"] for hit in hits]
```

- RRF는 키워드 검색(BM25)과 의미 검색(kNN) 결과를 합치는 하이브리드 검색이다.
- 결과는 `hits.hits` 목록이다. 조각 글은 각 항목의 `_source.merge_title_content`에 있다.
- 결과가 비면(`hits == []`) 빈 문자열을 넘기지 말고 "검색 결과 없음"처럼 알 수 있는 글을 돌려준다(캡스톤 정답 방식).
- 원본 코드 주석에는 BM25·kNN만 쓰는 검색도 있다고 적혀 있지만, 이 과정에서는 확인하지 않았고 `post_ragaas`도 받지 않는다. RRF만 쓴다.

### 문서 지우기 `delete-doc`

```python
payload = {"index_name": INDEX_NAME, "permission_groups": ["rag-public"], "doc_id": "meritz_pet_insurance"}
post_ragaas("delete-doc", payload, api_key=RAG_API_KEY)
```

- 내가 올린 `doc_id`만 지운다.

## 5. LLM·Agent와 잇는 법

- **RAG 체인:** 검색한 글을 합쳐 프롬프트의 `{context}`에 넣고 `get_llm()`으로 답하게 한다(`05_ragaas.py` 3부).
- **Agent 도구:** `@tool`로 감싸 Agent에게 준다. docstring이 도구 설명이 되므로 "사내 문서를 검색한다"처럼 언제 쓰는지 적는다(`solution.py`의 `rag_search`).
- `api_key`를 넘기지 않으면 `post_ragaas`가 `.env`의 `rag_api_key`를 쓴다.

## 6. 문제가 생기면

| 증상 | 원인 | 할 일 |
|---|---|---|
| `RuntimeError: 사내 API 설정이 부족합니다: [...]` | `search_url`·`rag_credential_key`·`rag_api_key` 중 빈 값 | 그 이름을 `.env`에 채운다. 사외 PC면 `COURSE_ENV=out` |
| `RuntimeError: 사내 RAGaaS에는 index_name 환경변수가 필요합니다.` | `index_name`이 비어 있음 | `.env.sample`의 견본 값을 그대로 쓴다 |
| 인증 실패(401 등) | 두 인증 값 중 하나가 틀리거나 빠짐 | 두 값을 다시 복사한다. 값을 출력해 확인하지 않는다 |
| 연결 오류, 시간 초과 | 사내망 밖 | 사외에서는 `COURSE_ENV=out`(모의 응답) |
| 답에 `[MOCK RAGaaS]`가 나온다 | 사외 설정이라 모의 응답을 받음 | 정상이다. 실제 약관 내용은 사내망에서만 나온다 |

점검: `uv run python -m config.check --json`(이름만 나옴). 그 밖의 오류는 [troubleshooting.md](troubleshooting.md)를 본다.

## 7. 하지 말 것

- 주소·인덱스 이름·키를 코드에 직접 쓰지 않는다. `.env`에서 읽는다.
- `rag_api_key`·`rag_credential_key` 값을 출력하거나 파일·채팅에 남기지 않는다.
- `requests.post`로 RAGaaS를 직접 부르지 않는다. 늘 `post_ragaas`를 쓴다(사외 모의 응답이 그래야 동작한다).
- 이 저장소 안에서는 `course/config/`를 고치지 않는다.
