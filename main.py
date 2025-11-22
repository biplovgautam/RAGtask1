'''
This is the root of the entire FastAPI application. 
It creates the main FastAPI() instance and includes/registers 
all the routers defined in app/api/endpoints.py.'''

from fastapi import FastAPI
from app.api import endpoints
from app.core.db import Base, ndb

app = FastAPI(
    title="RAGtask API",
    description="This is a custom RAG developed for my AI/ML intern task at palm mind.",
    version="1.0.0") 

# Create database tables
# Import models to register them with Base
from app.api.models import DocumentMetadata
if ndb is not None:
    Base.metadata.create_all(bind=ndb)

# includes all endpoints in this actual app from the app/api/endpoints.py
app.include_router(endpoints.router) 

# include endpoint for the document ingestion
app.include_router(endpoints.document_router)


# include conversational RAG endpoints in main
app.include_router(endpoints.rag_router)