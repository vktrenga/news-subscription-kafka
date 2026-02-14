from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/eventdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
