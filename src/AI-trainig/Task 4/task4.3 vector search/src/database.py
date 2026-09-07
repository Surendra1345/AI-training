from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from model import Chunk

DATABASE_URL = "postgresql+psycopg://postgres:Surendra283@localhost:5432/Chunking"

engine = create_engine(DATABASE_URL)