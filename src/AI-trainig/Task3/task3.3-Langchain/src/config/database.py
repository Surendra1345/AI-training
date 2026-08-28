from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
DATABASE_URL="postgresql://postgres:Surendra283@localhost:5432/AI-training"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase): 
    pass

def get_db():   
    db=SessionLocal()  
    try:       
        yield db   
    finally:       
         db.close()