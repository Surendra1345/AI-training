
import os
import httpx
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("Api-Key")
primary_model = {
    "name": "qwen/qwen3.6-35b-invalid",   # deliberately broken
    "input_price": 0.14,
    "output_price": 1.00
}

fallback_model = {
    "name": "openai/gpt-4o-mini",
    "input_price": 0.15,
    "output_price": 0.60
}

messages = []
conversation_total_cost = 0.0
while True:
    question = input("\nEnter your question: ")
    if question.lower() == "exit":
        print("Conversation ended.")
        break
    messages.append({
        "role": "user",
        "content": question
    })
    models = [
        primary_model,
        fallback_model
    ]
    answer = None
    for model in models:
        print(f"\nTrying model: {model['name']}")
        request_body = {
            "model": model["name"],
            "messages": messages,
            "stream_options": {
                "include_usage": True
            },
            "stream": True
        }
        answer_parts = []
        last_chunk = {}
        try:
            with httpx.stream(
                "POST",
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=request_body,
                timeout=120.0
            ) as response:
                print("Status Code:", response.status_code)
                if response.status_code != 200:
                    print("Model failed.")
                    print("Error:")
                    error_body = response.read().decode("utf-8")
                    print(error_body)
                    continue
                print("\nAssistant: ", end="", flush=True)
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    last_chunk = chunk
                    choices = chunk.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        print(
                            content,
                            end="",
                            flush=True
                        )
                        answer_parts.append(content)
                print()
                answer = "".join(answer_parts)

                if not answer.strip():
                    print("Model returned no answer.")
                    continue

                usage = last_chunk.get("usage", {})
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                input_cost = (input_tokens / 1_000_000) * model["input_price"]
                output_cost = (output_tokens / 1_000_000) * model["output_price"]
                total_cost = input_cost + output_cost
                print(f"Input Tokens: {input_tokens}")
                print(f"Output Tokens: {output_tokens}")
                print(f"Input Cost: ${input_cost:.6f}")
                print(f"Output Cost: ${output_cost:.6f}")
                print(f"Turn Cost: ${total_cost:.6f}")
                conversation_total_cost += total_cost
                print(f"Conversation Total Cost:{conversation_total_cost:.6f}")

                messages.append({
                    "role": "assistant",
                    "content": answer
                })
                print(f"\nSuccessful model: {model['name']}")
                # Stop trying models
                break
        except httpx.RequestError as error:
            print("Request error:", error)
            continue

    if answer is None:
        print("\nBoth models failed.")
        messages.pop()

