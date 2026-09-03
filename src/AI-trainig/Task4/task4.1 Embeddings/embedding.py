from fastembed import TextEmbedding
import numpy as np

with open("dataset.txt", "r", encoding="utf-8") as file:
    sentences = [line.strip() for line in file if line.strip()]

print("Number of sentences:", len(sentences))

model = TextEmbedding("BAAI/bge-small-en-v1.5")

print("Model loaded successfully")

embeddings = list(model.embed(sentences))

print("Number of embeddings:", len(embeddings))
print("Embedding dimension:", len(embeddings[0]))


# Queries
query1 = "How to reset my credentials?"
query2 = "What is the process to change my password?"
query3 = "How can I update my account information?"
query4 = "What steps should I follow to recover my account?"
query5 = "How do I retrieve my forgotten username?"


# Run each query
for query in [query1, query2, query3, query4, query5]:

    print(f"\nQuery: {query}")

    # Convert query into vector
    query_vector = list(model.embed([query]))[0]

    # Calculate similarity with all 200 sentences
    similarities = []

    for sentence_vector in embeddings:

        similarity = np.dot(query_vector, sentence_vector) / (
            np.linalg.norm(query_vector) * np.linalg.norm(sentence_vector)
        )

        similarities.append(similarity)

    # Get indices of top 5 highest similarity scores
    top_k = 5

    sorted_indices = np.argsort(similarities)[::-1][:top_k]

    # Print top 5
    print("Top 5 similar sentences:")

    for rank, idx in enumerate(sorted_indices, start=1):

        print(
            f"{rank}. {sentences[idx]}"
            f"\n   Similarity: {similarities[idx]:.4f}"
        )

# Keyword search

query = "how to create account?"

query_words = query.lower().split()
result = []

for sentence in sentences:

    sentence_words = sentence.lower().split()

    score = 0

    for word in query_words:

        if word in sentence_words:
            score += 1

    # Append only after checking ALL words
    result.append((score, sentence))


# Sort results by score in descending order
result.sort(reverse=True)

print("\nKeyword Search Results:")

for score, sentence in result[:5]:
    print(f"Score: {score}, Sentence: {sentence}")

