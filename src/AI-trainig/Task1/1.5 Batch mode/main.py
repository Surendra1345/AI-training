import os
import httpx
from dotenv import load_dotenv
import json
from time import perf_counter
import asyncio

load_dotenv("../1.3 Tokens and cost reporting/.env")

api_key = os.environ["Api-Key"]

input_token_cost = 0.75
output_token_cost = 3.75

# Read prompts from file
with open("prompt.txt", "r") as questions:
    prompts = [line.strip() for line in questions if line.strip()]

print("Number of prompts:", len(prompts))


async def send_prompt(client, prompt):

    request_body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 20
        }
    }

    response_body = await client.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        json=request_body,
        timeout=60.0
    )

    if response_body.status_code == 200:

        data = response_body.json()

        answer = data["candidates"][0]["content"]["parts"][0]["text"]

        usage = data.get("usageMetadata", {})

        input_tokens = usage.get("promptTokenCount", 0)
        output_tokens = usage.get("candidatesTokenCount", 0)

        input_cost = (input_tokens / 1_000_000) * input_token_cost
        output_cost = (output_tokens / 1_000_000) * output_token_cost

        total_cost = input_cost + output_cost

        return {
            "answer": answer,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost
        }

    else:

        print("Error:", response_body.status_code)

        print(json.dumps(response_body.json(), indent=2))

        return {
            "answer": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0
        }


async def main():

    async with httpx.AsyncClient() as client:

        # --------------------------------
        # Sequential execution
        # --------------------------------

        print("\nRunning sequential execution...")

        start_time = perf_counter()

        sequential_answers = []

        for prompt in prompts:
            result = await send_prompt(client, prompt)
            sequential_answers.append(result)

        end_time = perf_counter()

        sequential_time = end_time - start_time


        # --------------------------------
        # Concurrent execution
        # --------------------------------

        print("\nRunning concurrent execution...")

        start_time = perf_counter()

        concurrent_answers = await asyncio.gather(
            *(send_prompt(client, prompt) for prompt in prompts)
        )

        end_time = perf_counter()

        concurrent_time = end_time - start_time


    # --------------------------------
    # Print results
    # --------------------------------

    print("\n==============================")
    print("SEQUENTIAL RESULTS")
    print("==============================")

    for i, result in enumerate(sequential_answers, start=1):

        print(f"\nPrompt {i}:")
        print(result["answer"])

        print(f"Input tokens: {result['input_tokens']}")
        print(f"Output tokens: {result['output_tokens']}")
        print(f"Cost: ${result['cost']:.8f}")


    print("\n==============================")
    print("CONCURRENT RESULTS")
    print("==============================")

    for i, result in enumerate(concurrent_answers, start=1):

        print(f"\nPrompt {i}:")
        print(result["answer"])

        print(f"Input tokens: {result['input_tokens']}")
        print(f"Output tokens: {result['output_tokens']}")
        print(f"Cost: ${result['cost']:.8f}")


    # --------------------------------
    # Cost calculation
    # --------------------------------

    total_cost = sum(
        result["cost"] for result in concurrent_answers
    )

    average_cost = total_cost / len(concurrent_answers)


    # --------------------------------
    # Batch summary
    # --------------------------------

    print("\n==============================")
    print("BATCH SUMMARY")
    print("==============================")

    print("Number of prompts:", len(prompts))

    print(f"Sequential time: {sequential_time:.2f} seconds")

    print(f"Concurrent time: {concurrent_time:.2f} seconds")

    print(f"Total cost: ${total_cost:.8f}")

    print(f"Average cost per prompt: ${average_cost:.8f}")


    # --------------------------------
    # Comparison
    # --------------------------------

    print("\n==============================")
    print("TIME COMPARISON")
    print("==============================")

    if concurrent_time < sequential_time:

        print("Concurrent execution was faster.")

        speedup = sequential_time / concurrent_time

        print(f"Speedup: {speedup:.2f}x")

    else:

        print("Sequential execution was faster.")


asyncio.run(main())