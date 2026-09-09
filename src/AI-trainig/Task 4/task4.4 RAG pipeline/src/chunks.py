from datetime import date
from sqlalchemy.orm import Session
from database import engine
from model import Chunk
from embed import docs, embeddings

with Session(engine) as session:

    for doc, embedding in zip(docs, embeddings):

        chunk = Chunk(
            content=doc.page_content,
            embedding=embedding.tolist(),
            source=doc.metadata.get("source"),
            page=doc.metadata.get("page"),
            section=doc.metadata.get("section"),
            date=date.today(),
        )

        session.add(chunk)
    session.commit()
print("All chunks inserted successfully.")