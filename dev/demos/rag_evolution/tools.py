"""실제 조회 도구. 실패도 구조화해 모델과 화면이 함께 확인한다."""

from decimal import Decimal, InvalidOperation
from html import unescape
import math
import re
from typing import Callable
from urllib.parse import quote, urlparse

import requests
from langchain_core.tools import tool

from documents import load_pdf_documents

REQUEST_TIMEOUT = 12
MAX_PAGE_READS = 4
USER_AGENT = "AnimalInsuranceLearningDemo/1.0 (educational local application)"


def _failure(status: str, message: str, **details) -> dict:
    return {"ok": False, "status": status, "message": message, "sources": [], **details}


def _api(host: str, params: dict) -> dict:
    # All hosts originate in this module; tool users cannot supply request URLs.
    response = requests.get(
        f"https://{host}/w/api.php",
        params={"format": "json", "formatversion": 2, **params},
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
        allow_redirects=False,
    )
    response.raise_for_status()
    if response.status_code != 200:
        raise ValueError("unexpected_http_status")
    data = response.json()
    if "error" in data:
        raise ValueError("api_error")
    return data


def _network_failure(error: Exception) -> dict:
    if isinstance(error, requests.Timeout):
        return _failure("timeout", "외부 조회 제한 시간을 초과했습니다. 다시 실행해 주세요.")
    if isinstance(error, requests.HTTPError):
        status = error.response.status_code if error.response is not None else None
        return _failure("http_error", "외부 조회 서버가 요청을 처리하지 못했습니다.", http_status=status)
    return _failure("external_error", "외부 조회에 실패했습니다. 네트워크 연결이나 응답 형식을 확인해 주세요.")


def _wiki_page(query: str) -> tuple[dict | None, str]:
    """제목이 정확히 맞는 문서를 먼저 찾고, 없으면 검색 1위 문서를 쓴다."""
    language = "ko" if re.search(r"[가-힣]", query) else "en"
    host = f"{language}.wikipedia.org"
    fields = {"action": "query", "prop": "extracts|pageimages", "explaintext": 1, "exintro": 1,
              "exchars": 1200, "exlimit": 1, "piprop": "name", "pilicense": "free"}
    data = _api(host, {**fields, "titles": query, "redirects": 1})
    pages = [page for page in data.get("query", {}).get("pages", []) if not page.get("missing")]
    if not pages:
        data = _api(host, {**fields, "generator": "search", "gsrsearch": query, "gsrnamespace": 0, "gsrlimit": 1})
        pages = data.get("query", {}).get("pages", [])
    return (pages[0] if pages else None), host


def _wiki_result(query: str) -> dict:
    if not query.strip():
        return _failure("invalid_input", "검색할 동물 이름이나 질문을 입력해 주세요.")
    try:
        page, host = _wiki_page(query.strip()[:300])
        if not page:
            return _failure("no_results", "위키피디아 검색 결과가 없습니다.")
        text = page.get("extract", "").strip()
        if not text:
            return _failure("empty_text", "검색된 위키피디아 문서에서 요약문을 읽지 못했습니다.")
        source = {"source": f"Wikipedia: {page['title']}",
                  "url": f"https://{host}/wiki/{quote(page['title'].replace(' ', '_'))}",
                  "text": text}
        return {"ok": True, "status": "ok", "query": query, "text": text, "sources": [source]}
    except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError) as error:
        return _network_failure(error)


def _plain(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", value or "")).strip()


def _safe_wikimedia_url(value: str, hosts: set[str]) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname in hosts and not parsed.username


def make_tools(store_factory: Callable | None = None, top_k: int = 3) -> list:
    """위키피디아·사진·합계 도구에 보험 도구 하나를 더한다.

    검색 인덱스가 없으면(4·5단계) PDF 쪽 읽기, 있으면(8단계) 보험 벡터 검색.
    """

    @tool
    def wikipedia_search(query: str) -> dict:
        """동물에 관한 위키피디아 요약문을 찾는다. query에는 동물 이름만 넣는다(예: 고양이). 원문 URL과 실패 상태를 반환한다."""
        return _wiki_result(query)

    @tool
    def animal_photo(animal: str) -> dict:
        """동물의 위키피디아 대표 사진을 Wikimedia Commons에서 찾는다. 출처·저작자·라이선스가 모두 확인된 사진만 반환한다."""
        if not animal.strip():
            return _failure("invalid_input", "사진을 조회할 동물 이름을 입력해 주세요.")
        try:
            page, _ = _wiki_page(animal.strip()[:300])
            filename = page.get("pageimage") if page else None
            if not filename:
                return _failure("no_photo", "검색된 위키피디아 문서에 Commons 대표 사진이 없습니다.")
            data = _api("commons.wikimedia.org", {
                "action": "query", "titles": f"File:{filename}",
                "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": 800,
            })
            pages = data.get("query", {}).get("pages", [])
            infos = pages[0].get("imageinfo", []) if pages else []
            if not infos:
                return _failure("no_photo", "Commons에서 사진 정보를 찾지 못했습니다.")
            info = infos[0]
            metadata = info.get("extmetadata", {})
            author = _plain(metadata.get("Artist", {}).get("value", ""))
            license_name = _plain(metadata.get("LicenseShortName", {}).get("value", ""))
            license_url = unescape(metadata.get("LicenseUrl", {}).get("value", "")).strip()
            if license_url.startswith("//"):
                license_url = "https:" + license_url
            parsed_license = urlparse(license_url)
            image_url = info.get("thumburl") or info.get("url", "")
            source_url = info.get("descriptionurl", "")
            if not author or not license_name or parsed_license.scheme != "https" or not parsed_license.hostname:
                return _failure("missing_attribution", "사진의 저작자 또는 라이선스 정보를 확인할 수 없어 표시하지 않습니다.")
            if not _safe_wikimedia_url(image_url, {"upload.wikimedia.org", "thumb.wikimedia.org"}) or not _safe_wikimedia_url(source_url, {"commons.wikimedia.org"}):
                return _failure("invalid_photo_url", "사진 출처 주소를 확인할 수 없어 표시하지 않습니다.")
            if not info.get("mime", "").startswith("image/"):
                return _failure("no_photo", "검색 결과가 사진 파일이 아닙니다.")
            photo = {"image_url": image_url, "source_url": source_url,
                     "author": author, "license": license_name, "license_url": license_url}
            return {"ok": True, "status": "ok", "animal": animal, "photo": photo,
                    "sources": [{"source": f"Wikimedia Commons: {filename}", "url": source_url}]}
        except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError) as error:
            return _network_failure(error)

    @tool
    def cost_sum(amounts: list[float]) -> dict:
        """사용자가 제시한 원화 비용들을 합산한다. 보험료나 보험금 지급액을 추정하거나 보장 여부를 판단하지 않는다."""
        if not amounts or len(amounts) > 100 or any(not math.isfinite(x) or x < 0 for x in amounts):
            return _failure("invalid_amounts", "0 이상의 유한한 비용을 1~100개 입력해 주세요.")
        try:
            total = sum((Decimal(str(x)) for x in amounts), Decimal(0))
            if not math.isfinite(float(total)):
                return _failure("invalid_amounts", "합계가 너무 커서 표시할 수 없습니다.")
            return {"ok": True, "status": "ok", "amounts": amounts, "total": float(total),
                    "currency": "KRW", "sources": [],
                    "note": "입력 비용의 단순 합계입니다. 보험료나 지급 보험금 계산이 아닙니다."}
        except (InvalidOperation, OverflowError):
            return _failure("invalid_amounts", "입력 비용을 계산할 수 없습니다.")

    pages_read = []

    @tool
    def insurance_pdf_page(page: int) -> dict:
        """2024년 제공 동물보험 PDF의 지정한 쪽을 읽는다. page는 1~28 물리적 PDF 쪽번호다. 어느 쪽에 무엇이 있는지는 알려 주지 않는다. 질문 하나에 최대 4쪽까지 읽을 수 있다."""
        if len(pages_read) >= MAX_PAGE_READS:
            return _failure("read_limit", f"이번 질문에서 이미 {MAX_PAGE_READS}쪽({pages_read})을 읽었습니다. "
                            "더 읽지 말고 지금까지 읽은 내용으로 답하고, 찾지 못했으면 찾지 못했다고 답하세요.")
        pages_read.append(page)
        try:
            documents = load_pdf_documents()
            if page < 1 or page > len(documents):
                return _failure("out_of_range", f"물리적 PDF 쪽번호는 1~{len(documents)}입니다.")
            document = documents[page - 1]
            if not document.page_content:
                return _failure("empty_text", "이 PDF 쪽에서 텍스트를 추출하지 못했습니다.", page=page)
            return {"ok": True, "status": "ok", "page": page, "text": document.page_content,
                    "notice": "2024년 제공 문서 기준", "sources": [{**document.metadata, "text": document.page_content}]}
        except Exception:
            return _failure("document_error", "보험 PDF를 읽지 못했습니다. 앱 자료 파일을 확인해 주세요.")

    result = [wikipedia_search, animal_photo, cost_sum]
    if store_factory is None:
        return result + [insurance_pdf_page]

    @tool
    def insurance_search(query: str) -> dict:
        """2024년 제공 동물보험 PDF에서 질문과 비슷한 청크를 찾는다. 보험 질문에 쓴다. 근거 내용, 물리적 PDF 쪽번호, 청크 ID를 반환한다. 개인별 보험료는 문서에 없다."""
        if not query.strip():
            return _failure("invalid_input", "보험 문서에서 찾을 질문을 입력해 주세요.")
        try:
            matches = store_factory().similarity_search(query, k=top_k)
            sources = [{**document.metadata, "text": document.page_content} for document in matches if document.page_content.strip()]
            if not sources:
                return _failure("no_results", "보험 문서 검색 결과가 없습니다.")
            return {"ok": True, "status": "ok", "query": query,
                    "notice": "2024년 제공 문서 기준. 유사한 청크를 찾은 결과이며 답변 존재를 보증하지 않습니다.",
                    "sources": sources}
        except Exception:
            # Provider errors may embed authentication headers or URLs; do not expose them.
            return _failure("retrieval_error", "보험 문서 벡터 검색에 실패했습니다. 임베딩 연결과 인덱스를 확인해 주세요.")
    return result + [insurance_search]
