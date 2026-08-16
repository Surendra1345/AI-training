import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()  # reads .env and loads it into os.environ

API_KEY = os.environ["Api-Key"]

# response = httpx.post(
#     "https://openrouter.ai/api/v1/chat/completions",
#     headers={"Authorization": f"Bearer {API_KEY}"},
#     json={
#         "model": "openai/gpt-4o-mini",
#         "messages": [{"role": "user", "content": "What is the capital of France?"}],
#     },
# )

request_body = {
    "model": "openai/gpt-4o-mini",
    "messages": [{"role": "user", 
                "content": "who is the current president of America?"}],
}


response = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json=request_body,
)

data = response.json()  # this is the RESPONSE

print("REQUEST SENT:")
print(json.dumps(request_body, indent=2))

print("\nRESPONSE RECEIVED:")
print(json.dumps(data, indent=2))

print("\nANSWER:")
print(data["choices"][0]["message"]["content"])

# print(response.status_code)
# print(response.json())