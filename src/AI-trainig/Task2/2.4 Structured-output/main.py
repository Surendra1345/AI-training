import os
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import json
import re
 
load_dotenv()
api_key = os.getenv("Api-Key")
 
class ResponseModel(BaseModel):
    name: str
    age: int
    company: int
    role: str
 
def call_model(prompt):
    request_body = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
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
def clean_response(response_text):
    response_text = response_text.strip()
    # Remove Markdown fences
    response_text = re.sub(
        r"^```(?:json)?\s*",
        "",
        response_text
    )
    response_text = re.sub(
        r"\s*```$",
        "",
        response_text
    )
    # Find JSON object if model added prose before/after it
    start = response_text.find("{")
    end = response_text.rfind("}")
    if start != -1 and end != -1:
        response_text = response_text[start:end + 1]
    # Remove trailing commas
    response_text = re.sub(
        r",\s*([}\]])",
        r"\1",
        response_text
    )
    return response_text.strip()
def extract_data(text):
    prompt = f"""
Extract the following information from the text:
 
- name
- age
- company
- role
 
Return only a JSON object.
 
The JSON must contain:
"name": string
"age": integer
"company": string
"role": string
 
Text:
{text}
"""
    response_text = call_model(prompt)
    cleaned_response = clean_response(response_text)
    parsed_data = json.loads(cleaned_response)
    response_model = ResponseModel(**parsed_data)
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
        # ---------------- FIRST ATTEMPT ----------------
        try:
            response_model = extract_data(text)
            print("\nSuccess:")
            print(response_model.model_dump_json(indent=2))
            success_count += 1
 
        # ---------------- RETRY ----------------
 
        except (json.JSONDecodeError, ValidationError) as e:
            print("\nFirst attempt failed:")
            print(e)
            recovered = False
            for i in range(max_retries):
                retry_prompt = f"""
Your previous response failed.
Validation/parsing error:
{e}
Return the corrected JSON.
Required schema:
 
{ResponseModel.model_json_schema()}
Return ONLY the JSON object.
Original text:
{text}
"""
 
                try:
                    print(f"\nRetry attempt {i + 1}/{max_retries}:")
                    retry_response = call_model(retry_prompt)
                    print("\nRetry response:")
                    print(retry_response)
                    retry_response = clean_response(retry_response)
                    retry_data = json.loads(retry_response)
                    retry_model = ResponseModel(**retry_data)
                    print("\nRecovered successfully:")
                    print(retry_model.model_dump_json(indent=2))
                    recovered_count += 1
                    recovered = True
                    break
                except (json.JSONDecodeError, ValidationError) as retry_error:
                    print(f"\nRetry attempt {i + 1} failed:")
                    print(retry_error)
            if not recovered:
                print("\nFailed after retry limit.")
                failed_count += 1
    except Exception as e:
        print("\nUnexpected error:")
        print(e)
        failed_count += 1
 
print("FINAL RESULT")
print(f"Total runs:         {run}")
print(f"First-pass success: {success_count}")
print(f"Recovered:          {recovered_count}")
print(f"Failed cleanly:     {failed_count}")
 