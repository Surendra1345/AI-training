import asyncio
import os

# Windows event loop required by psycopg async connections
asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)
from sqlalchemy import create_engine, text
from langchain_postgres import PGEngine, PGVectorStore
from langchain_core.embeddings import Embeddings
from fastembed import TextEmbedding


# --------------------------------------------------
# 1. FastEmbed adapter for LangChain
# --------------------------------------------------

class FastEmbedModel(Embeddings):

    def __init__(self):
        self.model = TextEmbedding(
            "BAAI/bge-small-en-v1.5"
        )

    def embed_documents(self, texts):
        return [
            embedding.tolist()
            for embedding in self.model.embed(texts)
        ]

    def embed_query(self, text):
        return list(
            self.model.embed([text])
        )[0].tolist()


# --------------------------------------------------
# 2. PostgreSQL connection
# --------------------------------------------------

DATABASE_URL = "postgresql+psycopg://postgres:Surendra283@localhost:5432/Chunking"

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set in the .env file"
    )

# SQLAlchemy engine for raw SQL
sql_engine = create_engine(DATABASE_URL)

# LangChain PostgreSQL engine
engine = PGEngine.from_connection_string(
    url=DATABASE_URL
)

# --------------------------------------------------
# 3. Create embedding model
# --------------------------------------------------

embedding_model = FastEmbedModel()

# --------------------------------------------------
# 4. Connect LangChain to existing chunks table
# --------------------------------------------------

store = PGVectorStore.create_sync(
    engine=engine,
    table_name="chunks",

    # Existing columns
    id_column="id",
    content_column="content",
    embedding_column="embedding",

    # Existing metadata columns
    metadata_columns=[
        "source",
        "page",
        "section",
        "date",
        "chunking_method",
    ],

    # We don't have a JSON metadata column
    metadata_json_column=None,

    embedding_service=embedding_model,
)

print("Connected to existing chunks table!")


# --------------------------------------------------
# 5. Query
# --------------------------------------------------

query = "How can a farmer recover an account?"


# ==================================================
# 6. RAW SQL VECTOR SEARCH
# ==================================================

query_embedding = embedding_model.embed_query(query)

raw_sql = text("""
    SELECT
        id,
        content,
        source,
        page,
        section,
        chunking_method,
        embedding <=> CAST(:query_embedding AS vector) AS distance
    FROM chunks
    ORDER BY embedding <=> CAST(:query_embedding AS vector)
    LIMIT 5;
""")


with sql_engine.connect() as connection:

    raw_results = connection.execute(
        raw_sql,
        {
            "query_embedding": str(query_embedding)
        }
    ).fetchall()


print("RAW SQL RESULTS")



for i, row in enumerate(raw_results, start=1):

    print("\n--------------------")
    print("Rank:", i)
    print("ID:", row.id)
    print("Content:", row.content)
    print("Source:", row.source)
    print("Page:", row.page)
    print("Section:", row.section)
    print("Chunking method:", row.chunking_method)
    print("Distance:", row.distance)


# ==================================================
# 7. LANGCHAIN VECTOR SEARCH
# ==================================================

langchain_results = store.similarity_search(
    query,
    k=5
)

print("LANGCHAIN RESULTS")

for i, document in enumerate(
    langchain_results,
    start=1
):

    print("\n--------------------")
    print("Rank:", i)
    print("Content:", document.page_content)
    print("Metadata:", document.metadata)


# ==================================================
# 8. COMPARE RESULTS
# ==================================================

print("COMPARISON")

raw_contents = [
    row.content
    for row in raw_results
]

langchain_contents = [
    document.page_content
    for document in langchain_results
]


print(
    "Raw SQL returned:",
    len(raw_results),
    "chunks"
)

print(
    "LangChain returned:",
    len(langchain_results),
    "chunks"
)


if raw_contents == langchain_contents:

    print("Same results and same order: YES")

else:

    print("Same results and same order: NO")


# Compare the actual chunks regardless of order

if set(raw_contents) == set(langchain_contents):

    print("Same chunks returned: YES")

else:

    print("Same chunks returned: NO")