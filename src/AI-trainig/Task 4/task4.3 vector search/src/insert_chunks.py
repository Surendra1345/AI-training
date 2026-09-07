from sqlalchemy.orm import Session

from database import engine
from model import Chunk
from chunking import all_chunks, embeddings


with Session(engine) as session:

    for chunk, embedding in zip(all_chunks, embeddings):

        db_chunk = Chunk(
            content=chunk.page_content,
            embedding=embedding.tolist(),
            source=chunk.metadata["source"],
            page=chunk.metadata["page"],
            section=chunk.metadata["section"],
            date=chunk.metadata["date"],
            chunking_method=chunk.metadata["chunking_method"],
        )

        session.add(db_chunk)

    session.commit()

print("All chunks inserted successfully.")