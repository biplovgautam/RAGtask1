'''
Defines Pydantic models used for data validation. 
This ensures that request data (like a chat message) and response data 
(like the LLM's answer) strictly conform to a defined JSON structure.'''

from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from app.core.db import Base

class ChunkingStrategy(str, Enum):
    """
    Defines the two selectable chunking strategies for document ingestion.
    """
    FIXED = "fixed"         # Simple, reliable, consistent chunk size
    SEMANTIC = "semantic"   # Context-preserving, better quality for RAG

class IngestionResponse(BaseModel):
    """
    Response model for the document ingestion endpoint.
    """
    message: str
    filename: str
    document_id: str
    chunking_strategy: ChunkingStrategy
    extracted_text_length: int
    num_chunks: int

# --- Document Metadata Model for DB Storage (SQLAlchemy) ---

class DocumentMetadata(Base):
    """
    SQLAlchemy model for the 'documents' table in Neon PostgreSQL.
    """
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    chunking_strategy = Column(SQLEnum(ChunkingStrategy), nullable=False)
    num_chunks = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)