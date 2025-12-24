from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# путь к бд, sqlite лежит рядом с проектом
DATABASE_URL = "sqlite:///./history.db"

# check_same_thread=False нужен для sqlite чтобы работало с fastapi
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """генератор сессий для Depends"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
