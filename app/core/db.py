'''
Sets up the SQLAlchemy engine for Neon PostgreSQL database. 
Most importantly, it defines the get_db function, which FastAPI 
uses as a Dependency to provide a fresh, managed database connection for every request.
'''

import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables
load_dotenv()

# --- 1. Pinecone Setup ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "ragtask1" # The specific index we want to use

# 'pinecone_index' is the ONLY public interface for Pinecone operations
pinecone_index = None

if PINECONE_API_KEY:
    try:
        # Initialize Pinecone client internally (prefixed with _)
        _pc = Pinecone(api_key=PINECONE_API_KEY)
        # Connect to the specific index
        pinecone_index = _pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        print(f"Error initializing Pinecone: {e}")
else:
    print("Warning: PINECONE_API_KEY not found in environment variables.")


# --- 2. Neon PostgreSQL Setup ---
# We expect the connection string to be in DATABASE_URL or NEON_DB_URL
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("NEON_DB_URL")

# 'ndb' object interface for neon postgres (SQLAlchemy Engine)
ndb = None
SessionLocal = None
Base = declarative_base()

if DATABASE_URL:
    try:
        # Create SQLAlchemy engine
        # ndb represents the connection pool/engine
        ndb = create_engine(DATABASE_URL)
        
        # Create SessionLocal class for creating sessions
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ndb)
    except Exception as e:
        print(f"Error connecting to Neon DB: {e}")
else:
    print("Warning: DATABASE_URL or NEON_DB_URL not found in environment variables.")


def get_db():
    """
    Dependency to get a DB session.
    Yields a SQLAlchemy Session object.
    """
    if SessionLocal is None:
        # If DB is not configured, we can't yield a session.
        # In a real app, you might want to raise an error or handle this gracefully.
        raise RuntimeError("Database connection (ndb) is not initialized.")
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
