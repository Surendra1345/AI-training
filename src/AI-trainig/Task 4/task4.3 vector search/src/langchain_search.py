import asyncio

asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

from langchain_postgres import PGEngine, PGVectorStore
from langchain_core.embeddings import Embeddings
from fastembed import TextEmbedding


class FastEmbedModel(Embeddings):

    def __init__(self):
        self.model = TextEmbedding("BAAI/bge-small-en-v1.5")

    def embed_documents(self, texts):
        return [
            embedding.tolist()
            for embedding in self.model.embed(texts)
        ]

    def embed_query(self, text):
        return list(
            self.model.embed([text])
        )[0].tolist()


# Same PostgreSQL database
DATABASE_URL = (
    "postgresql+psycopg://postgres:Surendra283@localhost:5432/Chunking"
)

engine = PGEngine.from_connection_string(
    url=DATABASE_URL
)

embedding_model = FastEmbedModel()


store = PGVectorStore.create_sync(
    engine=engine,
    table_name="chunks",

    # Our existing columns
    id_column="id",
    content_column="content",
    embedding_column="embedding",

    # Our metadata columns
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

query = "How can a farmer recover an account?"

results = store.similarity_search(
    query,
    k=5
)

print("\nTop 5 similar chunks:")

for i, document in enumerate(results, start=1):
    print("\n--------------------")
    print("Rank:", i)
    print("Content:", document.page_content)
    print("Metadata:", document.metadata)

print("Connected to existing chunks table!")