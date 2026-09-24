import os
from collections import Counter
from pprint import pprint

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

import uuid

provider = os.getenv('LLM_PROVIDER', 'samsung').strip().lower()
if provider == 'openai':
    model = os.getenv('OPENAI_MODEL')
    api_key = os.getenv('OPENAI_API_KEY')
    if not model or not api_key:
        raise RuntimeError('OPENAI_MODEL과 OPENAI_API_KEY가 필요합니다.')
    client = OpenAI(api_key=api_key)
elif provider == 'samsung':
    model = os.getenv('model')
    required = ('api_base_url', 'credential_key', 'send_system_name', 'user_id')
    missing = [name for name in required if not os.getenv(name)]
    if not model or missing:
        raise RuntimeError(f'사내 LLM 설정이 부족합니다: {missing or ["model"]}')
    client = OpenAI(
        api_key='samsung-gateway',  # 실제 사내 인증은 x-dep-ticket 헤더에서 처리
        base_url=os.getenv('api_base_url'),
        default_headers={
            'x-dep-ticket': os.getenv('credential_key'),
            'Send-System-Name': os.getenv('send_system_name'),
            'User-Id': os.getenv('user_id'),
            'User-Type': 'AD_ID',
            'Prompt-Msg-Id': str(uuid.uuid4()),
            'Completion-Msg-Id': str(uuid.uuid4()),
        },
    )
else:
    raise ValueError(f'지원하지 않는 LLM_PROVIDER: {provider}')


# OpenAI SDK 예제는 사외에서는 공식 API, 사내에서는 호환 게이트웨이를 사용한다.


# ── Single Turn ───────────────────────────────────────────────────────────────
# input에 문자열을 직접 전달하면 사용자 메시지로 처리
response = client.responses.create(
    model=model,
    input='LLM이 무엇인지 3문장으로 설명해줘.',
)
print(response.output_text)
print()


# ── Multi Turn ────────────────────────────────────────────────────────────────
# input에 역할(role)이 있는 메시지 리스트를 전달하면 대화 맥락 유지
# developer: 시스템 지시 / user: 사용자 입력 / assistant: AI 응답
context = [
    {'role': 'developer', 'content': '너는 단답형 답변 챗봇이야. 경어체를 유지하면서, 가능하면 단답형으로 답변해줘.'},
    {'role': 'user', 'content': '대한민국의 수도는 어디지?'},
]
response_1 = client.responses.create(model=model, input=context)
print(response_1.output_text)

# 이전 응답(response_1.output)을 context에 추가해 대화를 이어감
context += response_1.output
context += [{'role': 'user', 'content': '그곳의 인구는 어느정도야?'}]
response_2 = client.responses.create(model=model, input=context)
print(response_2.output_text)


# ── Streaming ─────────────────────────────────────────────────────────────────
# stream()을 사용하면 LLM이 생성하는 토큰을 실시간으로 받을 수 있음
# output_text.delta 이벤트에 실제 텍스트 조각이 담겨 있음
with client.responses.stream(
    model=model,
    input='LLM이 무엇인지 3문장으로 설명해줘.',
) as stream:
    event_types = []
    for event in stream:
        event_types.append(event.type)
        if 'output_text.delta' in event.type:
            print(event.delta, end='')
    print()
    pprint(Counter(event_types))


# ── Temperature & Top P (참고용) ──────────────────────────────────────────────
# temperature: 0에 가까울수록 일관된 답변, 높을수록 창의적(최대 2.0)
# top_p: 확률 상위 p% 토큰만 사용. temperature와 동시 조정은 권장하지 않음
# 주의: gpt-5 계열은 temperature 미지원
"""
response = client.responses.create(
    model=model,
    input='LLM이 무엇인지 3문장으로 설명해줘.',
    temperature=0.2,
    top_p=0.1,
)
print(response.output_text)
"""
