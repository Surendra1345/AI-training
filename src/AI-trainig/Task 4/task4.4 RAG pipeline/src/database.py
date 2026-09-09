from sqlalchemy import create_engine


database_url="postgresql+psycopg2://postgres:Surendra283@localhost:5432/Chunking"

engine = create_engine(database_url, echo=True)
