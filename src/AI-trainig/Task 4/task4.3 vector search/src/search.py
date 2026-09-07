from fastembed import TextEmbedding
from sqlalchemy import create_engine, text

# Embedding model
model = TextEmbedding("BAAI/bge-small-en-v1.5")

# User query
query = "How can a farmer recover an account?"

# Create query embedding
query_embedding = list(model.embed([query]))[0]

print("Query embedding dimension:", len(query_embedding))


# PostgreSQL connection
DATABASE_URL = "postgresql+psycopg://postgres:Surendra283@localhost:5432/Chunking"

engine = create_engine(DATABASE_URL)


# Vector search
sql = text("""
    SELECT
        id,
        content,
        source,
        page,
        section,
        chunking_method,
        embedding <=> CAST(:query_embedding AS vector) AS distance
    FROM chunks
    WHERE chunking_method = 'structure-aware'
    ORDER BY embedding <=> CAST(:query_embedding AS vector)
    LIMIT 5;
""")


with engine.connect() as connection:

    results = connection.execute(
        sql,
        {
            "query_embedding": str(query_embedding.tolist())
        }
    )

    for row in results:
        print("\n--------------------")
        print("ID:", row.id)
        print("Content:", row.content)
        print("Source:", row.source)
        print("Page:", row.page)
        print("Section:", row.section)
        print("Chunking method:", row.chunking_method)
        print("Distance:", row.distance)