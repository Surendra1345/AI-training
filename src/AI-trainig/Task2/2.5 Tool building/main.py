import os
import json
import httpx
from dotenv import load_dotenv
from tools import TOOL_SCHEMAS
from tool_register import tool_registry

load_dotenv()

api_key = os.getenv("Api-Key")
prompt = input("Enter your prompt: ")
messages = [
    {
        "role": "user",
        "content": prompt
    }
]

request_body = {
    "model": "openai/gpt-4o-mini",
    "messages": messages,
    "tools": TOOL_SCHEMAS
}

response = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json=request_body
)

response.raise_for_status()

second_message = response.json()["choices"][0]["message"]

print("\nSecond model response:")
print(json.dumps(second_message, indent=2))
message = response.json()["choices"][0]["message"]

tool_calls = message.get("tool_calls")

if tool_calls:

    # Add the assistant's tool-call message to the conversation
    messages.append(message)

    for tool_call in tool_calls:

        tool_name = tool_call["function"]["name"]

        arguments = json.loads(
            tool_call["function"]["arguments"]
        )

        # Get the actual Python function
        function = tool_registry[tool_name]

        # Execute it
        result = function(**arguments)

        print("Tool result:", result)

        # Add the result back to the conversation
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(result)
            }
        )
else:
    print("\nFinal answer:")
    print(message.get("content"))