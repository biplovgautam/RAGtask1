'''
Defines Pydantic models used for data validation. 
This ensures that request data (like a chat message) and response data 
(like the LLM's answer) strictly conform to a defined JSON structure.'''

from enum import Enum
from pydantic import BaseModel

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

# --- Document Metadata Model for DB Storage ---

class DocumentMetadata(BaseModel):
    """
    Schema for storing document metadata in the SQL/NoSQL database.
    """
    document_id: str
    filename: str
    chunking_strategy: ChunkingStrategy
    num_chunks: int
    ingestion_timestamp: str