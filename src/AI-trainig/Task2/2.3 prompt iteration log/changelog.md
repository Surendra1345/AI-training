version 1:
prompt -> what is mean fastapi
Base line
expected: the simple defination
Actual : it give a detailed defination with one example

version2:
prompt ->explain fastapi to the beginner
changed ->added the "to the beginner"
expected:
A simpler explanation suitable for a beginner.
Actual:
The response became more detailed, including APIs, installation, endpoints, Uvicorn, Swagger/ReDoc, and multiple code examples.

version 3:
prompt->Explain what FastAPI is to a beginner in 50 words or less.
changed :
just explain in "50 words"
expected:
The answer should be beginner-friendly.
The answer should be short.
It should be 50 words or fewer.
Actual:
The answer became shorter and more concise.

version 4:
prompt->Explain what FastAPI is to a beginner in 50 words with an example.
changed:
just added the 50 words with "example"
expected:
Short explanation + one example.
Actual:
It gave a short explanation and a simple FastAPI code example.

version 5:
prompt->Explain what FastAPI is to a beginner in 50 words or less. Give one simple real-world use case.
changed:
simple rea-world use case
expected:
A short explanation plus one practical use case.
Actual:
It gave a short explanation and a to-do list API as a real-world use case.