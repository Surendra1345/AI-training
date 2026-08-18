import httpx
from time import perf_counter


with open("prompt.txt", "r", encoding="utf-8") as questions:
    prompts = [line.strip() for line in questions if line.strip()]


model = "llama3.2"


for prompt in prompts:

    request_body = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    start_time = perf_counter()

    response = httpx.post(
        "http://localhost:11434/api/generate",
        json=request_body,
        timeout=120.0
    )

    elapsed_time = perf_counter() - start_time

    print(f"\nPrompt: {prompt}")
    print("Status Code:", response.status_code)
    print(f"Latency: {elapsed_time:.2f} seconds")

    if response.status_code == 200:

        data = response.json()

        answer = data["response"]

        print("Answer:")
        print(answer)

    else:

        print("Request failed:")
        print(response.text)