'''
Defines Pydantic models used for data validation. 
This ensures that request data (like a chat message) and response data 
(like the LLM's answer) strictly conform to a defined JSON structure.'''

from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from app.core.db import Base
from typing import Optional, List

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


# --- Conversational RAG Models ---

class ConversationMode(str, Enum):
    """
    Defines conversation modes for chat memory management.
    """
    CONTINUE = "continue"   # Continue conversation with history
    RESTART = "restart"     # Clear history and start fresh

class ChatRequest(BaseModel):
    """
    Request model for conversational RAG endpoint.
    """
    query: str
    mode: ConversationMode = ConversationMode.CONTINUE
    session_id: Optional[str] = "default"  # Optional session ID for multi-user support

class ChatResponse(BaseModel):
    """
    Response model for conversational RAG endpoint.
    """
    response: str
    session_id: str
    mode: ConversationMode
    retrieved_chunks: Optional[int] = 0
    booking_created: Optional[bool] = False

# --- Interview Booking Model for DB Storage (SQLAlchemy) ---

class InterviewBooking(Base):
    """
    SQLAlchemy model for the 'interview_bookings' table in Neon PostgreSQL.
    Stores interview booking information extracted by the LLM.
    """
    __tablename__ = "interview_bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    date = Column(String, nullable=False)  # Store as string (e.g., "2025-11-25")
    time = Column(String, nullable=False)  # Store as string (e.g., "14:00")
    created_at = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, nullable=True)  # Track which conversation created this booking