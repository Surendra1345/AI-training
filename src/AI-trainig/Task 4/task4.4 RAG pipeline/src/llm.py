import os
from random import choices
import httpx
from dotenv import load_dotenv
from search import semantic_search

load_dotenv()
api_key = os.getenv("Api-Key")

def generate_answer(query: str, top_k: int = 5,coversation=None):
    if conversation is None:
        conversation = []

    conversation = chat_conversation(conversation),

    conversation_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in conversation
    )
    # 1. Retrieve relevant chunks using semantic search
    results = semantic_search(query, top_k)
    # 2. Combine retrieved chunks into context

    thresold=0.60
    if results[0]["similarity"]<thresold:
        return {
            "answer": "I don't know based on the provided documents.",
            # "results": []
        }
    context = "\n\n".join(
        result["content"]
        for result in results
    )
    # 3. Create RAG prompt
    prompt =f"""
Answer the user's question using only the information
provided in the context.

Previous conversation:
{conversation_text}

Context:
{context}

Question:
{query}

If the answer is not present in the context, say:
"I don't know based on the provided documents."
"""
    # 4. Create LLM request
    request_body = {
        "model": "google/gemma-4-26b-a4b-it:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    # 5. Call OpenRouter
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=request_body,
        timeout=120
    )

    response.raise_for_status()

    # 6. Extract LLM answer
    data = response.json()
    print("OpenRouter response:")
    print(data)
    answer = data["choices"][0]["message"]["content"]

    citations = []

    for result in results:
      citations.append({
        "document": "RAG.pdf",
        "page": result["page"],
        "url": f"http://127.0.0.1:8000/src/RAG.pdf#page={result['page']}"
    })

    return {
    "answer": answer,
    "citations": citations
}

def chat_conversation(conversation,max_count=10):
   return conversation[-max_count:]

