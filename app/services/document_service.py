'''
Contains the functions for the first API task: 
receiving a file, extracting text, implementing the two chunking strategies, 
calling the embedding model, and saving the document metadata via db.py.'''

import io
import os
from typing import Literal, List
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.api.models import ChunkingStrategy, DocumentMetadata
from sqlalchemy.orm import Session
from datetime import datetime


def save_document_metadata(
    db: Session,
    document_id: str,
    filename: str,
    chunking_strategy: ChunkingStrategy,
    num_chunks: int,
    file_size: int
) -> DocumentMetadata:
    """
    Saves the document metadata to the Neon PostgreSQL database.

    Args:
        db: The SQLAlchemy database session.
        document_id: The unique ID of the document.
        filename: The name of the uploaded file.
        chunking_strategy: The strategy used for chunking.
        num_chunks: The total number of chunks generated.
        file_size: The size of the file in bytes.

    Returns:
        The created DocumentMetadata instance.
    """
    new_doc = DocumentMetadata(
        document_id=document_id,
        filename=filename,
        chunking_strategy=chunking_strategy,
        num_chunks=num_chunks,
        file_size=file_size,
        upload_timestamp=datetime.utcnow()
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


def chunk_text(text: str, strategy: ChunkingStrategy) -> List[str]:
    """
    Splits the input text into chunks based on the selected strategy.

    Args:
        text: The full text content to be chunked.
        strategy: The chunking strategy (FIXED or SEMANTIC).

    Returns:
        A list of text chunks.
    """
    if not text:
        return []

    if strategy == ChunkingStrategy.FIXED:
        # Fixed-size chunking: Simple, consistent size
        # We use a larger chunk size with some overlap to maintain context across boundaries
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""] # Standard separators
        )
        return splitter.split_text(text)

    elif strategy == ChunkingStrategy.SEMANTIC:
        # Semantic/Recursive chunking: Tries to keep related text together
        # We use a smaller chunk size but prioritize splitting on paragraph/sentence boundaries
        # This is better for retrieval as it preserves the "meaning" of a section
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""] # Prioritize sentence endings
        )
        return splitter.split_text(text)
    
    else:
        # Fallback (should not happen if Enum is used correctly)
        return [text]


def extract_text_from_file_bytes(
    file_bytes: bytes, 
    file_extension: Literal['.pdf', '.txt']
) -> str:
    """
    Extracts text content from file bytes based on the file extension.

    Args:
        file_bytes: The raw bytes of the uploaded file (from await UploadFile.read()).
        file_extension: The validated extension ('.pdf' or '.txt').

    Returns:
        The extracted text content as a single string.
    
    Raises:
        ValueError: If the file is a PDF but text extraction fails.
    """
    
    if file_extension == '.txt':
        # For text files, simply decode the bytes
        try:
            # We try UTF-8 first, then fall back to a common encoding if it fails
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            print("Warning: UTF-8 decoding failed, attempting ISO-8859-1 (Latin-1) fallback.")
            return file_bytes.decode('iso-8859-1', errors='ignore')

    elif file_extension == '.pdf':
        try:
            # Wrap the bytes in an in-memory stream object
            pdf_stream = io.BytesIO(file_bytes)
            
            # Create a PdfReader instance
            reader = PdfReader(pdf_stream)
            
            extracted_text = []
            
            # Iterate through all pages and extract text
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
            
            # Join all extracted text into one large string
            return "\n\n".join(extracted_text)
        
        except Exception as e:
            # Catch any exception during PDF parsing (e.g., corrupted file)
            raise ValueError(f"Failed to extract text from PDF: {e}")

    else:
        # This case should ideally not be reached due to prior validation in endpoints.py
        raise ValueError(f"Unsupported file extension for extraction: {file_extension}")
    

