from embed_model import model
from embed import embeddings, docs
import numpy as np


def semantic_search(query: str, top_k: int):
    query_embedding = list(model.embed([query]))[0]

    document_embeddings = np.array(embeddings)

    similarity = np.dot(
        query_embedding,
        document_embeddings.T
    ) / (
        np.linalg.norm(query_embedding)
        * np.linalg.norm(document_embeddings, axis=1)
    )

    top_k_indices = np.argsort(similarity)[-top_k:][::-1]

    results = []

    for index in top_k_indices:
        results.append({
            "content": docs[index].page_content,
            "similarity": float(similarity[index]),
            "source": docs[index].metadata.get("source"),
            "page": docs[index].metadata.get("page", 0) + 1
        })

    return results