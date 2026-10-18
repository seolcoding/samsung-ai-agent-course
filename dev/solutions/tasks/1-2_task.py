"""1-2 과제(강사용 정답): 같은 질문을 requests와 SDK로 보내 답 꺼내기

실행(저장소 맨 위에서): uv run --env-file .env python course/Chapter01/tasks/1-2/1-2_task.py
"""
import requests
from openai import OpenAI

import config  # noqa: F401  .env를 읽는다
from config.samsung import llm_config

# ── 설정(그대로 둡니다): 사내 게이트웨이의 주소·모델·인증 헤더와 client를 준비합니다 ──
samsung = llm_config()
api_base_url = samsung["base_url"].rstrip("/")
model = samsung["model"]
headers = {**samsung["headers"], "Content-Type": "application/json"}
client = OpenAI(api_key="samsung-gateway", base_url=samsung["base_url"], default_headers=samsung["headers"])

# requests로 보낼 JSON(payload)에 함께 넣을 값입니다(사내 모델이 생각 과정을 답에 섞지 않게 합니다).
# payload에 **PAYLOAD_EXTRA로 풀어 넣습니다.
PAYLOAD_EXTRA = {"include_reasoning": False}

QUESTION = "노트북이 갑자기 느려졌어요. 먼저 확인할 것 하나만 알려 주세요."
print("질문:", QUESTION)


print("\n=== 1. requests로 직접 보내기 ===")
# ✍️ 목표 1: requests.post로 f"{api_base_url}/chat/completions"에 headers와 JSON(model, messages)을 보내고,
#            응답 JSON의 choices[0].message.content를 꺼내 출력합니다.
payload = {
    "model": model,
    "messages": [{"role": "user", "content": QUESTION}],
    **PAYLOAD_EXTRA,
}
http_response = requests.post(f"{api_base_url}/chat/completions", headers=headers, json=payload, timeout=60)
http_response.raise_for_status()
recv_json = http_response.json()
print(recv_json["choices"][0]["message"]["content"])


print("\n=== 2. SDK로 보내기 ===")
# ✍️ 목표 2: client.responses.create로 developer 메시지(상담원 역할·두 문장 이내)와 user 메시지(QUESTION)를 보내고,
#            output_text를 출력합니다.
context = [
    {"role": "developer", "content": "너는 친절한 IT 헬프데스크 상담원이야. 두 문장 이내로 답해 줘."},
    {"role": "user", "content": QUESTION},
]
sdk_response = client.responses.create(model=model, input=context)
print(sdk_response.output_text)
