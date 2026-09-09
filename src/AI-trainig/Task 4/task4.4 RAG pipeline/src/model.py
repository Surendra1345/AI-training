from sqlalchemy import Integer,String,Text,Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class Chunk(Base):
    __tablename__="ragchunks"

    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    content:Mapped[str]=mapped_column(Text,nullable=False)
    embedding:Mapped[Vector]=mapped_column(Vector(384),nullable=False)

    source: Mapped[str | None] = mapped_column(Text)
    page: Mapped[int | None] = mapped_column(Integer)
    section: Mapped[str | None] = mapped_column(Text)
    date: Mapped[date | None] = mapped_column(Date)

