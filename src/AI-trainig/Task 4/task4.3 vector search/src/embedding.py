from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-en-v1.5")

text = "A farmer creates an account by entering basic profile information."

embedding = list(model.embed([text]))[0]

print("Embedding dimension:", len(embedding))
print("First 5 values:", embedding[:5])