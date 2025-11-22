'''
Contains the functions for the first API task: 
receiving a file, extracting text, implementing the two chunking strategies, 
calling the embedding model, and saving the document metadata via db.py.'''

import io
import os
from typing import Literal
from pypdf import PdfReader


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