import httpx
import os
from dotenv import load_dotenv
from time import perf_counter
import asyncio

load_dotenv()

api_key = os.getenv("Api-Key")


with open("prompt.txt", "r", encoding="utf-8") as questions:
    prompts = [line.strip() for line in questions if line.strip()]


models = {
    "google/gemini-3.5-flash": {
        "input_price": 1.50,
        "output_price": 9.00
    },

    "openai/gpt-4o-mini": {
        "input_price": 0.15,
        "output_price": 0.60
    },

    "deepseek/deepseek-v4-flash": {
        "input_price": 0.09,
        "output_price": 0.18
    },

    "qwen/qwen3.6-35b-a3b": {
        "input_price": 0.14,
        "output_price": 1.00
    }
}


results = []


async def send_request(client, model, pricing, prompt):

    request_body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "usage": {
            "include": True
        }
    }

    start_time = perf_counter()

    response = await client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=request_body,
        timeout=120.0
    )

    elapsed_time = perf_counter() - start_time

    if response.status_code == 200:

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        usage = data.get("usage", {})

        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        input_price = pricing["input_price"]
        output_price = pricing["output_price"]

        input_cost = (
            input_tokens / 1_000_000
        ) * input_price

        output_cost = (
            output_tokens / 1_000_000
        ) * output_price

        total_cost = input_cost + output_cost

        print(f"\nModel: {model}")
        print(f"Prompt: {prompt}")
        print("Status Code:", response.status_code)
        print(f"Latency: {elapsed_time:.2f} seconds")

        print("Answer:")
        print(answer)

        print(f"Input tokens: {input_tokens}")
        print(f"Output tokens: {output_tokens}")
        print(f"Input cost: ${input_cost:.8f}")
        print(f"Output cost: ${output_cost:.8f}")
        print(f"Total cost: ${total_cost:.8f}")

        return {
            "model": model,
            "prompt": prompt,
            "answer": answer,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "latency": elapsed_time,
            "usable": bool(answer)
        }

    else:

        print(f"\nModel: {model}")
        print(f"Prompt: {prompt}")
        print("Status Code:", response.status_code)
        print("Request failed:")
        print(response.text)

        return {
            "model": model,
            "prompt": prompt,
            "answer": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "input_cost": 0,
            "output_cost": 0,
            "total_cost": 0,
            "latency": elapsed_time,
            "usable": False
        }


async def main():

    async with httpx.AsyncClient() as client:

        for model, pricing in models.items():

            print("\n==============================")
            print(f"MODEL: {model}")
            print("==============================")

            model_results = await asyncio.gather(
                *(
                    send_request(
                        client,
                        model,
                        pricing,
                        prompt
                    )
                    for prompt in prompts
                )
            )

            results.extend(model_results)

    # --------------------------------
    # MODEL COMPARISON
    # --------------------------------

    print("\n==============================")
    print("MODEL COMPARISON")
    print("==============================")

    for model in models:

        model_results = [
            result
            for result in results
            if result["model"] == model
        ]

        if not model_results:
            print(f"\nModel: {model}")
            print("No results available")
            continue
        total_cost = sum(
            result["total_cost"]
            for result in model_results
        )
        average_cost = total_cost / len(model_results)
        total_latency = sum(
            result["latency"]
            for result in model_results
        )
        average_latency = total_latency / len(model_results)
        usable_count = sum(
            result["usable"] is True
            for result in model_results
        )
        print(f"\nModel: {model}")
        print(f"Average cost per call: ${average_cost:.8f}")
        print(f"Average latency: {average_latency:.2f} seconds")
        print(
            f"Usable: {usable_count}/{len(model_results)}"
        )
asyncio.run(main())