# 1-4 교안 노트북 — 목차 (v1, 2026-09-28)

> 2026-10-18: 실습 노트북에서 "AI에게 물어보기" 절을 뺐다(`dev/AGENTS.md`). 아래의 물어보기 항목은 지난 설계 기록이고 빌드에 쓰이지 않는다.

- **권 제목**: RAG 이론 & 실습 (PDF 표지 "1-4 RAG 이론 & 실습")
- **원본 PDF**: `docs/raw/Chapter01/day01/1-4-rag-theory-and-core-modules.pdf` (19쪽)
- **원본 코드**: `src/raw/Chapter01/03-rag/` 5개 + 데이터 1개
  - `01_data_loading.py`, `02_embeddings.py`, `03_vector_store.py`, `04_langchain_rag.py`, `05_ragaas.py`
  - `data/meritz_pet_insurance.pdf` (28쪽 약관, raw·solution 동일 파일)
- **커리큘럼**: 2.1 RAG 이론과 핵심 모듈 실습, 2일차 3.0H. PDF는 `day01` 폴더에 있지만 커리큘럼상 2일차 첫 블록이다.
- **만들 파일**: `lessons/Chapter01/1-4_rag_LEC.ipynb`, `lessons/Chapter01/1-4_rag_LAB.ipynb` (LAB 원천은 `lessons/drafts/labs/03-rag.json`, 현재 뼈대 상태)
- **사외 준비 환경**: `LLM_PROVIDER=openai`, `EMBED_PROVIDER=openai`, `RAG_PROVIDER=mock`

## 1. LEC 목차 (코드 셀 없음, PDF 순서 그대로)

| # | 절 제목 (PDF 제목) | 슬라이드 쪽 | 핵심 메시지 (근거 쪽) | 퀴즈 (4지선다) |
|---|---|---|---|---|
| 1 | 도입 | 1–2 | 세 덩어리: RAG 개념 · 핵심 모듈 6단계 · 청킹과 임베딩 (p2) | — |
| 2 | Fine-Tuning과의 비교 | 3–5 | RAG는 모델이 모르는 외부 지식을 찾아 답변에 함께 넣는다. 다시 학습시키지 않고 지식을 바꿀 수 있다(p4). Fine-Tuning은 말투·형식, RAG는 최신 정보·사내 문서(p5). **왜 배우나**: LLM은 학습 이후 정보와 사내 문서를 모른다(p4) | 사내 제품 매뉴얼의 최신 내용을 답하게 하려면 무엇이 알맞은가? (정답: RAG) |
| 3 | Naive → Advanced → Modular RAG 발전 과정 | 6–8 | Naive는 불러오기→나누기→임베딩·저장→검색→생성 5단계(p6). Advanced는 Query Rewrite·Hybrid Search·Re-ranking·Self-check를 더한다(p7). Modular는 단계를 모듈처럼 조합한다(p8) | 검색 결과의 우선순위를 다시 계산하는 보완 단계는? (정답: Re-ranking) |
| 4 | Loading, Splitting, Embedding | 9–12 | Loading은 본문과 메타데이터(파일명·페이지·URL)를 함께 불러온다(p10). Splitting은 너무 크면 찾기 어렵고 너무 작으면 맥락이 끊긴다(p11). Embedding은 의미가 비슷하면 가까운 벡터가 된다(p12). **왜 배우나**: 메타데이터가 있어야 출처를 붙이고(p10), 검색 품질은 임베딩 품질에 크게 좌우된다(p12) | 답변에 출처를 붙이려면 Loading 단계에서 무엇을 함께 남겨야 하나? (정답: 메타데이터) |
| 5 | Storage, Retrieval, Generation | 13–15 | Storage는 벡터·원문·메타데이터를 저장하고 인덱스를 관리한다(p13). Retrieval은 질문을 임베딩해 가까운 청크를 찾는다(p14). Generation은 검색된 근거 안에서 답하게 지시한다(p15). **왜 배우나**: 검색이 틀리면 생성이 좋아도 답변이 흔들린다(p14) | 검색 결과가 질문과 무관할 때 가장 먼저 의심할 단계는? (정답: Retrieval) |
| 6 | Fixed-size, Recursive, Semantic Chunking | 16–18 | Fixed-size는 단순하지만 문장 중간에서 잘린다. Recursive는 문단→문장→구분자 순으로 경계를 찾아 기본 선택지로 많이 쓴다(p17). Semantic은 의미 변화 지점에서 나누며 계산 비용이 크다(p18) | 정책 문서처럼 의미 흐름이 중요한 자료에 알맞은 방식은? (정답: Semantic) |
| 7 | 임베딩 모델 선택 기준 | 19 | 한국어 의미 유사도, 도메인 용어, 차원 수·속도·비용을 본다. 벤치마크 점수만으로 끝나지 않고 실제 질문 샘플·정답 문서·청킹별 결과로 확인한다(p19). **왜 배우나**: 사내 문서는 도메인 용어가 많아 실제 데이터로 확인해야 한다(p19) | 벤치마크 점수 말고 꼭 확인할 것은? (정답: 실제 질문 샘플로 본 검색 결과) |
| 8 | 정리 퀴즈 | — | 세 덩어리의 핵심 | 4문항: ① RAG와 Fine-Tuning의 역할 ② Naive RAG 5단계 중 빠진 단계 고르기 ③ chunk 크기를 너무 작게 했을 때 생기는 일 ④ 질문도 벡터로 바꾸는 이유 |

- 수강생 글에는 쪽 표시를 넣지 않는다. 위 (pN)은 목차 작성용 근거다.
- 슬라이드 속 코드(p10–14)는 슬라이드로만 보여 준다. LEC에는 코드 셀을 두지 않는다.

## 2. LAB 목차

공통: 첫 셀은 환경 확인(LLM에 더해 임베딩 설정 이름도 확인해야 함, 아래 5절). 각 장의 첫 구획(불러오기)은 접힌 준비 셀.

| 장 | 원본 파일 | 구분 | CHANGE_HERE 후보 / WRITE_HERE로 쓸 TODO (원본 줄) | 성공 기준 초안 | 실행 제약 |
|---|---|---|---|---|---|
| 2 | 01_data_loading | 과제 2 + 예제 | **WRITE_HERE ①** `# TODO: PDFMinerLoader로 PDF를 읽고 Document 목록을 생성해 주세요.` → 빈칸 `loader = PDFMinerLoader(...)`, `documents = loader.load()` (p10에서 배움) · **WRITE_HERE ②** `# TODO: Text Splitter를 사용해 Document 목록을 Chunk로 나누어 주세요.` → 빈칸 `chunks = text_splitter.split_documents(documents)` (p11) · **CHANGE_HERE** `chunk_size=500`, `chunk_overlap=75`, 결과 확인의 `chunks[:3]` | 🟢 오류 없이 청크 3개가 `0. len=…` 형태로 출력된다 · 🟢 chunk_size를 줄이면 len 값이 작아진다 · ⛔ `NameError`/`FileNotFoundError`가 난다 | API 호출 없음. `__file__` 경로 문제(5절). 약관 PDF는 Document 1개로 읽힌다(PDFMiner 기본값) |
| 3 | 02_embeddings | 예제 + AI에게 물어보기 | TODO 없음. **CHANGE_HERE** `sentences` 목록의 세 번째 문장, `embed_query('애완동물이 뛰노는 모습')`의 질문 · **AI에게 물어보기**: 사내 임베딩을 LangChain에 맞추는 `SamsungEmbeddings` 클래스가 두 메서드만으로 동작하는 이유를 설명받기 | 🟢 [강아지] vs [개] 유사도가 [강아지] vs [주식]보다 크다 · 🟢 질문을 바꾸면 "가장 유사한 문장"이 바뀔 수 있다 · ⛔ 벡터 차원이 0이거나 유사도가 `nan` | 임베딩 API 호출. 사외는 OpenAI 임베딩 분기, 사내는 `SamsungEmbeddings` 분기. 유사도 숫자는 모델마다 달라 정답으로 고정하지 않는다 |
| 4 | 03_vector_store | 과제 2 + 예제 | **WRITE_HERE ①** `# TODO: 임베딩 모델을 가져오고 Chroma 벡터스토어를 생성해 주세요.` → 빈칸 `embeddings = get_embeddings()` + `Chroma.from_documents(...)` (p12–13) · **WRITE_HERE ②** `# TODO: 벡터스토어를 retriever로 변환해 주세요.` → 빈칸 `retriever = vectorstore.as_retriever(search_kwargs={'k': 3})` (p14) · **CHANGE_HERE** 검색 질문(아래 input 처리에 따라 달라짐) | 🟢 `retriever ready` 뒤 질문마다 청크 3개가 나온다 · 🟢 보험 약관과 관련된 질문이면 약관 문장이 보인다 · ⛔ 결과가 3개가 아니거나 빈 목록 | 청크 50개 임베딩. **`while True` + `input()` 무한 루프**(5절) |
| 5 | 04_langchain_rag | 과제 4 + 예제 | **WRITE_HERE ①②** 03과 같은 두 TODO(반복 연습) · **WRITE_HERE ③** `# TODO: 검색된 Document 목록을 context 문자열로 합쳐 주세요.` → 빈칸 `return '\n\n'.join(doc.page_content for doc in docs)` (p15) · **WRITE_HERE ④** `# TODO: retriever, prompt, llm, output parser를 연결해 RAG 체인을 완성해 주세요.` → 빈칸 `rag_chain = (...)` (LCEL·RunnablePassthrough는 1-3에서 배움) · **CHANGE_HERE** system 프롬프트 문장(p4의 "맥락에 답이 없으면 …" 규칙을 더해 보기) | 🟢 `RAG ready` 뒤 답변이 글자 단위로 흘러나온다(스트리밍) · 🟢 약관에 없는 질문에는 모른다고 답한다(CHANGE_HERE 뒤) · ⛔ `TypeError`(체인 입력 형식) 또는 약관과 무관한 일반 답변 | 임베딩 + LLM 호출. `while True` + `input()` 무한 루프(5절) |
| 6 | 05_ragaas | 예제 (과제 없음) | RAGaaS는 1-4 PDF와 앞 권에 없으므로 예제로 바꾼다. TODO 3줄은 지운다. **CHANGE_HERE** `question = '펫보험 보장 내용이 뭐야?'`, `'num_result_doc': 3` · **AI에게 물어보기**: 직접 만든 RAG(2~5장)와 RAGaaS의 단계 비교 설명받기 | 🟢 `검색된 문서 수: N` 뒤 답변이 흘러나온다 · 🟢 (사외 mock) 답변 근거에 `[MOCK RAGaaS]` 문구가 보인다 · ⛔ `401`/`403` 또는 `RuntimeError: 사내 API 설정이 부족합니다` | **실제 RAGaaS는 사내 전용, 사외 실행 불가**. 사외는 `RAG_PROVIDER=mock`으로 요청·응답 흐름만 연습(mock은 항상 1건을 돌려줘 `num_result_doc` 변화가 안 보임). insert/delete는 공유 인덱스 문제(5절) |
| 7 | 정리 | — | — | — | — |

집계: **5장**(원본 파일 1개당 1장), **과제 8개**(01: 2, 03: 2, 04: 4), **예제 5곳**(01 결과 확인, 02, 03 검색, 04 프롬프트, 05), **AI에게 물어보기 2곳**(02, 05).

## 3. 원본·솔루션 차이와 고른 쪽

| 파일 | 차이 | 고른 쪽 | 이유 |
|---|---|---|---|
| 01 | 결과 출력: raw는 청크 전문 출력 + "`[:120]` 지우기" 주석(코드에 `[:120]`이 없어 주석과 코드가 어긋남), solution은 `text[:120]` | **solution** | 화면이 짧고 주석·코드가 맞는다 |
| 02 | 벡터 출력: raw `v[:5]`(앞 5개), solution 벡터 전체(수천 개 숫자) | **raw** | 화면이 넘치지 않는다. 주석 "앞 5개 값"과도 맞는다 |
| 03 | raw는 Chroma·retriever 인자 사이에 설명 주석이 끼어 있고 retriever가 여러 줄, solution은 한 줄 + 끝 쉼표 + "ChromaDB를 저장하고 싶을 때" 주석 | **solution** | 정답 보기가 짧고 슬라이드 p14 모양과 같다 |
| 04 | 들여쓰기·공백만 다름 | **solution** (빌드 때 ruff 정리로 사실상 같음) | 체인 줄이 가지런하다 |
| 05 | INDEX_NAME: raw 고정값 `'rp-aicoa-meritz-pet'`(원본 addae97과 같음), solution은 `index_name` 환경변수 + 없으면 오류 | **raw** | 짧고, 사내 기준(원본 addae97)과 같다. mock은 인덱스 이름을 보지 않는다 |
| 05 | insert-doc·delete-doc: raw는 주석 처리(TODO), solution은 실행 | **raw(주석 유지)**, 4절 질문 2에 따라 바꿈 | 공유 인덱스를 수강생 20명이 동시에 올리고 지우는 것을 막는다 |
| 05 | `fields_exclude`: raw 주석, solution 실행 | **solution** | 응답에서 큰 벡터 필드를 빼서 응답이 가볍다. 출력 화면에는 차이 없음 |
| 05 | raw에만 있는 설명 주석(INDEX 여러 문서 등록, `# print(result)`, `# ai -> ...`) | **raw** | 설명 주석은 수강생에게 도움이 된다. 들여쓰기만 맞춘다 |

## 4. 실행 제약·위험과 처리 제안

1. **`__file__`가 노트북에 없음 (01·03·04·05)**: `PDF_PATH = Path(__file__).parent / 'data' / ...`가 `NameError`가 난다. 접힌 준비 셀에서 PDF 경로를 정해 주는 방식이 필요하다(`src/raw/…/*.ipynb`는 `__file__`을 준비 셀에서 지정하는 선례가 있다). 수강생은 노트북만 받으므로 약관 PDF도 함께 배포해야 한다(질문 3).
2. **`while True` + `input()` 무한 루프 (03·04)**: 셀이 끝나지 않고, `nbconvert --execute` QC는 `input()`에서 실패한다. 제안: 루프는 그대로 두고 "빈 줄이 아니라 셀 중지(■)로 끝낸다"를 안내하거나, 빌드 때 루프 한 줄만 `question = '...'` 한 번 실행으로 바꾼다(질문 1).
3. **05 RAGaaS는 사내 전용**: `RAG_API_KEY` 전역변수(`rag_api_key`)와 `api-key` 요청 헤더(`config.samsung.ragaas_config`)가 둘 다 있어야 인증된다. 사외는 실행 불가 → `RAG_PROVIDER=mock`으로 흐름만 연습하고, 장 첫머리에 "사외에서는 모의 응답"이라고 표시한다. 사내 실제 동작은 강의장 사전 확인 목록에 올린다.
4. **05 insert-doc·delete-doc**: 모두 같은 `INDEX_NAME`·`doc_id`를 쓴다. 한 명이 delete를 실행하면 다른 수강생 검색이 비고, 동시에 insert하면 중복 청크가 쌓일 수 있다. insert-doc는 서버 청킹·임베딩이라 최대 300초 걸린다. 제안: 두 줄은 주석으로 두고 "강사가 수업 전에 한 번 업로드" 방식(질문 2).
5. **임베딩 설정 확인**: LAB 첫 환경 확인 셀은 LLM 이름만 본다. 1-4는 `EMBED_PROVIDER`(사외 `OPENAI_EMBEDDING_MODEL`, 사내 `embedding_api_url`·`embedding_x_dep_ticket`)와 05의 `RAG_PROVIDER`·`rag_api_key`·`rag_credential_key`·`search_url`도 확인해야 한다.
6. **경고 출력**: `langchain_community` 불러올 때 `DeprecationWarning`(sunset 안내)이 뜬다. QC 기준이 "오류·경고 없이"이므로 준비 셀에서 이 경고만 숨길지 정해야 한다.
7. **Loading 메타데이터와 슬라이드의 차이**: PDFMinerLoader 기본값은 28쪽 약관을 Document 1개(약 2만 자)로 읽어 페이지 번호가 없다. p10의 "페이지 번호 메타데이터"와 다르므로 강사용 메모에 적는다(코드는 바꾸지 않음).
8. **02의 빈 "실습: SamsungEmbeddings 구현" 구획**: 주석만 있고("아래 주석을 해제하고…") 아래에 코드가 없다. 클래스는 파일 윗부분(접히는 준비 구획)에 이미 완성돼 있다. 제안: 이 주석 구획은 셀로 만들지 않고, 클래스가 있는 구획을 보이는 예제 셀로 나눈다(`split` 지정).
9. **실행 시간·비용**: 03·04·05가 각각 PDF를 다시 읽고 청크 50개를 다시 임베딩한다(사내는 10개씩 5회). 03·04는 인메모리 Chroma라 파일 쓰기는 없다(`persist_directory`는 주석).

## 5. 커리큘럼 항목 대조 (`docs/CURRICULUM.md` 2.1)

| 커리큘럼 항목 | 위치 |
|---|---|
| RAG vs Fine-tuning 역할 분리 | LEC 2 |
| Naive → Advanced → Modular RAG 발전 흐름 | LEC 3 |
| 핵심 모듈 Loading / Splitting / Embedding / Storage / Retrieval / Generation | LEC 4–5 |
| 청킹 전략(Fixed/Recursive/Semantic)과 임베딩 모델 선택 관점 | LEC 6–7 |
| [실습] PDF 로딩/청킹/벡터스토어(Chroma) 구축 | LAB 2–4 |
| [실습] LangChain RAG 체인 구성 및 스트리밍 응답 구현 | LAB 5 |
| [실습] RAGaaS API 기반 사내형 RAG 구현 패턴 이해 | LAB 6 (사외는 mock) |

## 6. 사용자에게 물어볼 것

1. **03·04의 `input()` 무한 루프**: 루프를 그대로 두고 셀 중지로 끝내게 할까요, 아니면 빌드 때 질문 한 개를 변수로 넣어 한 번만 실행하도록 바꿀까요? (뒤쪽이면 CHANGE_HERE로 질문을 바꾸게 할 수 있고, QC 자동 실행도 통과합니다.)
2. **05 insert-doc·delete-doc**: 공유 인덱스를 지키기 위해 수강생 노트북에서는 주석으로 두고 강사가 미리 업로드하는 방식으로 할까요?
3. **약관 PDF 배포**: 수강생은 노트북만 받으므로 `meritz_pet_insurance.pdf`를 노트북 옆(예: `lessons/Chapter01/data/`)에 함께 둘까요, 다른 배포 방식이 있나요?
