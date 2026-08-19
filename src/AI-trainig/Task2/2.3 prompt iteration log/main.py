import os
import httpx
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("Api-Key")

with open ("prompt.txt", "r") as file:
    prompt = file.read()

request_body={
    "model": "openai/gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "maxOutputTokens": 100,
}

response = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json=request_body
)

print("Status Code:", response.status_code)
answer = response.json()["choices"][0]["message"]["content"]
print("Answer:", answer)