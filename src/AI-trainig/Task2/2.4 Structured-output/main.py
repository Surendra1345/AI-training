import os
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

api_key = os.getenv("Api-Key")


class ResponseModel(BaseModel):
    name: str
    age: int
    company: int
    role: str

def call_model(prompt, use_schema=False):
    request_body = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    # Use schema only when requested
    if use_schema:
        request_body["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "response_model",
                "strict": True,
                "schema": ResponseModel.model_json_schema()
            }
        }
    response_body = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=request_body,
        timeout=120.0
    )
    if response_body.status_code != 200:
        raise Exception(
            f"API Error {response_body.status_code}: {response_body.text}"
        )
    data = response_body.json()
    return data["choices"][0]["message"]["content"]
def extract_data(text):
    prompt = f"""
Extract the following information from the text:
- name
- age
- company
- role
Return only a JSON object.
Text:
{text}
"""
    # First call without the schema
    response_text = call_model(prompt)
    print("\nFirst response:")
    print(response_text)
    # Validate the actual response
    response_model = ResponseModel.model_validate_json(response_text)
    return response_model
text = """
My name is Surendra and I am 22 years old.
I am working at Genworx.ai as a Fullstack Trainee.
"""
success_count = 0
recovered_count = 0
failed_count = 0
max_retries = 1
for run in range(1, 11):
    print(f"RUN {run}")
    try:
        # ---------- FIRST ATTEMPT ----------
        try:
            response_model = extract_data(text)
            print("\nSuccess:")
            print(response_model.model_dump_json(indent=2))
            success_count += 1
        # ---------- FIRST RETRY PROMPT ----------
        except ValidationError as e:
            print("\nFirst attempt failed:")
            print(e)
            recovered = False
            for i in range(max_retries):
                retry_prompt = f"""
Your previous response failed Pydantic validation.
Validation error:
{e}
Extract the information again.
Original text:
{text}
Return only valid JSON.
"""
                try:
                    print(
                        f"\nRetry attempt {i + 1}/{max_retries}"
                    )
                    retry_response = call_model(
                        retry_prompt,
                        use_schema=False
                    )
                    print("\nRetry response:")
                    print(retry_response)
                    retry_model = ResponseModel.model_validate_json(
                        retry_response
                    )
                    print("\nRecovered successfully:")
                    print(
                        retry_model.model_dump_json(indent=2)
                    )
                    recovered_count += 1
                    recovered = True
                    break
                except ValidationError as retry_error:
                    print(
                        f"\nRetry attempt {i + 1} failed:"
                    )
                    print(retry_error)
            # ---------- SECOND / FINAL RETRY PROMPT ----------

            if not recovered:
                final_retry_prompt = f"""
This is the final correction attempt.

Previous attempts failed validation.

The required data types are:

- name: string
- age: integer
- company: String
- role: string

Return ONLY a valid JSON object.

Original text:
{text}
"""
                try:
                    print("\nSwitching to final retry prompt...")
                    final_response = call_model(
                        final_retry_prompt,
                        use_schema=True
                    )
                    print("\nFinal retry response:")
                    print(final_response)
                    final_model = ResponseModel.model_validate_json(
                        final_response
                    )
                    print("\nRecovered by final retry:")
                    print(
                        final_model.model_dump_json(indent=2)
                    )
                    recovered_count += 1
                    recovered = True
                except ValidationError as final_error:
                    print("\nFinal retry failed:")
                    print(final_error)
            # ---------- ALL ATTEMPTS FAILED ----------
            if not recovered:
                print("\nFailed after all retry attempts.")
                failed_count += 1
    except Exception as e:
        print("\nUnexpected error:")
        print(e)
        failed_count += 1

print("FINAL RESULT")
print("Total runs:         10")
print(f"First-pass success: {success_count}")
print(f"Recovered:          {recovered_count}")
print(f"Failed cleanly:     {failed_count}")