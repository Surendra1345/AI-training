import os
import httpx
from dotenv import load_dotenv
import json
from time import perf_counter
import logging

load_dotenv()

API_KEY = os.environ["Api-Key"]
question=input("Enter your question: ")

request_body = {
    "contents": [
        {
            "parts": [
                {
                    "text": question
                }
            ]
        }
    ]
}

count_response = httpx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:countTokens",
    headers={
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json",
    },
    json=request_body,
)

input_tokens = count_response.json()["totalTokens"]

print(f"Input tokens: {input_tokens}")

start_time = perf_counter()

response = httpx.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
    headers={
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json",
    },
    json=request_body,
)

logging.basicConfig(level=logging.INFO)

print("STATUS CODE:", response.status_code)

logging.info("REQUEST SENT:")
print(json.dumps(request_body, indent=2))


logging.info("RESPONSE RECEIVED:")
print(json.dumps(response.json(), indent=2))

logging.info("ANSWER:")
print(response.json()["candidates"][0]["content"]["parts"][0]["text"])

# print(response.status_code)
# print(response.json())

usage = response.json()["usageMetadata"]

output_tokens = usage["candidatesTokenCount"]
total_tokens = usage["totalTokenCount"]

print(f"Input tokens: {input_tokens}")
print(f"Output tokens: {output_tokens}")
print(f"Total tokens: {total_tokens}")

logging.info("Cost calculation:")
input_cost=(input_tokens/1000000)*0.75
output_cost=(output_tokens/1000000)*3.75

print(f"Output cost: ${output_cost:.6f}")
print(f"Input cost: ${input_cost:.6f}")

total_cost = input_cost + output_cost
INR=total_cost*95.3


end_time=perf_counter()
latency_ms = (end_time - start_time) * 1000


logging.info(
    f"input_tokens={input_tokens} "
    f"output_tokens={output_tokens} "
    f"total_tokens={total_tokens}  "
    f"latency_ms={latency_ms:.2f} "
    f"cost_usd={total_cost:.6f} "
    f"cost_inr={INR:.6f}"
)