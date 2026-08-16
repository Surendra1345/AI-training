import os
import httpx
from dotenv import load_dotenv
import json


load_dotenv("../1.3 Tokens and cost reporting/.env")

api_key = os.environ["Api-Key"]

# question = input("Enter your question: ")

request_body = {
    "model": "gemini-3.5-flash-lite",
    "contents": [
        {
            "parts": [
                {
                    "text":"what is mean by fast api" *1000000
                }
            ]
        }
    ],
    "generationConfig": {
        "temperature":0,
        "maxOutputTokens": 20
    }
}


# for i in range(10):
response_body = httpx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        json=request_body,
    )

# answer = response_body.json()["candidates"][0]["content"]["parts"][0]["text"]

    # print(f"Run {i + 1}:")
# print("Status Code:", response_body.status_code )
# print(answer)

# input_tokens=request_body["contents"][0]["parts"][0]["text"].split()
# print("Input tokens:", len(input_tokens))

print("Status Code:", response_body.status_code)
print("Response:") 
print(json.dumps(response_body.json(), indent=2))

input_words = request_body["contents"][0]["parts"][0]["text"].split()
print("Input words:", len(input_words))