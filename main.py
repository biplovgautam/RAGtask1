'''
This is the root of the entire FastAPI application. 
It creates the main FastAPI() instance and includes/registers 
all the routers defined in app/api/endpoints.py.'''

from fastapi import FastAPI
from app.api import endpoints
from app.core.db import Base, ndb

app = FastAPI(
    title="RAGTask Backend API",
    description="Two REST APIs: 1) Document Ingestion API, 2) Conversational RAG API with Redis memory and interview booking.",
    version="1.0.0"
) 

# Create database tables
# Import models to register them with Base
from app.api.models import DocumentMetadata, InterviewBooking
if ndb is not None:
    Base.metadata.create_all(bind=ndb)

# ============================================
# Register the two main API routers
# ============================================

# API 1: Document Ingestion (POST /documents/upload/)
app.include_router(endpoints.document_router)

# API 2: Conversational RAG (POST /RAG/chat)
app.include_router(endpoints.rag_router)