import os
import uuid
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

provider = os.getenv('LLM_PROVIDER', 'samsung').strip().lower()
if provider == 'openai':
    api_base_url = 'https://api.openai.com/v1/chat/completions'
    model = os.getenv('OPENAI_MODEL')
    api_key = os.getenv('OPENAI_API_KEY')
    if not model or not api_key:
        raise RuntimeError('OPENAI_MODEL과 OPENAI_API_KEY가 필요합니다.')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
elif provider == 'samsung':
    required = ('api_base_url', 'model', 'credential_key', 'send_system_name', 'user_id')
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f'사내 LLM 설정이 부족합니다: {missing}')
    api_base_url = f'{os.getenv("api_base_url").rstrip("/")}/chat/completions'
    model = os.getenv('model')
    headers = {
        'x-dep-ticket': os.getenv('credential_key'),
        'Send-System-Name': os.getenv('send_system_name'),
        'User-Id': os.getenv('user_id'),
        'User-Type': 'AD_ID',
        'Prompt-Msg-Id': str(uuid.uuid4()),
        'Completion-Msg-Id': str(uuid.uuid4()),
        'Content-Type': 'application/json',
    }
else:
    raise ValueError(f'지원하지 않는 LLM_PROVIDER: {provider}')

payload = {
    "model": model,
    "messages": [
        { "role": "user","content": "LLM이 무엇인지 3문장으로 설명해줘." },
    ],
    "temperature": 0.5,
    "stream": False,
}
if provider == 'samsung':
    payload['include_reasoning'] = False

new_response = requests.post(
    api_base_url, headers=headers, json=payload, timeout=30
)
new_response.raise_for_status()
recv_json = new_response.json()
  
print("### 응답 Json")
pprint(recv_json)
print("### 결과 메시지")
print(recv_json["choices"][0]["message"]["content"])


"""
api_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

if not api_key:
    raise RuntimeError('OPENAI_API_KEY 환경변수를 설정해주세요.')

# OpenAI Responses API 엔드포인트
# - 기존 Chat Completions(/v1/chat/completions)의 후속 API
# - input 필드 하나로 단순 문자열과 대화 내역 모두 처리 가능
url = 'https://api.openai.com/v1/responses'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

payload = {
    'model': model,
    'input': 'LLM이 무엇인지 3문장으로 설명해줘.',
}

response = requests.post(url, headers=headers, json=payload, timeout=30)
response.raise_for_status()

data = response.json()
pprint(data)
"""
