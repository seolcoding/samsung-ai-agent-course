import os
import json
import uuid
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

# Private 환경
api_base_url = f'{os.getenv("api_base_url")}/chat/completions' 

payload = json.dumps({
    "model":"private-model.1-260330",
    "messages": [
        { "role": "user","content": "LLM이 무엇인지 3문장으로 설명해줘." },
    ],
    "temperature": 0.5,
    "stream": False,
    "include_reasoning": False,
})

headers = {
    'x-dep-ticket': os.getenv('credential_key'),  # 발급받은 credential 정보
    'Send-System-Name': os.getenv('send_system_name'),  # 승인 받으신 결재문서에 기입하신 Send-System-Name
    'User-Id': os.getenv('user_id'), 
    'User-Type': 'AD_ID', # 유저 AD ID
    'Prompt-Msg-Id': str(uuid.uuid4()),
    'Completion-Msg-Id': str(uuid.uuid4()),
    'Accept': 'text/event-stream; charset=utf-8',
    'Content-Type': 'application/json'
}


try:
    new_response = requests.request(
        "POST", 
        url=api_base_url,
        headers=headers, 
        data=payload, 
        timeout=None
    )
except Exception as e:
  print(e)
recv_json = new_response.json()
  
print("### 응답 Json")
pprint(recv_json)
 
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