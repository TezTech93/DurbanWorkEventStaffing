# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use Render's internal DATABASE_URL or fallback to local development URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

# For PostgreSQL, we need to set pool_size and other options
engine = create_engine(
    DATABASE_URL,
    pool_size=5,               # adjust as needed
    max_overflow=10,
    pool_pre_ping=True,        # ensures connections are alive
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()