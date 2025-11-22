# Backend with two REST APIs using FastAPI :

1. Document Ingestion API
    - Upload .pdf or .txt files(done)
    - Extract text, apply two chunking strategies (selectable)(done)
    - Generate embeddings & store in Pinecone/Qdrant/Weaviate/Milvus (pc connectiondone, storing remaining)
    - Save metadata in SQL/NoSQL DB (db connection done storing the metadata remaining)
2. Conversational RAG API
    - Custom RAG (no RetrievalQAChain)
    - Use Redis for chat memory
    - Handle multi-turn queries
    - Support interview booking (name, email, date, time) using  LLM
    - Store booking info


### Constraints:
No FAISS/Chroma, no UI, no RetrievalQAChain clean modular code following industry standards for typing and annotations

## Status
- project initialization(done)
- uploading file(done)
- acceopting only the supported file type .pdf & .txt(done)
- text extraction using pypdf for .pdf and utf-8 decoding for .txt(done)
- selectable chunking(fixed, semantic) strategy(done)
- apply chunking strategy(done)


## project architecture
```
RAGtask1/
├── app/
│   ├── api/
│   │   ├── endpoints.py             # FastAPI router definitions
│   │   ├── models.py                # Pydantic models for API requests/responses
│   ├── core/
│   │   ├── db.py                    # Database connection setup (SQL/NoSQL)
│   ├── services/
|   |   ├── llm_wrapper.py                   # Your custom LLM wrapper (if needed)
│   │   ├── document_service.py      # Logic for text extraction, chunking, embedding
│   │   ├── vector_store_manager.py  # Pinecone/Qdrant connection and interaction
│   │   ├── llm_service.py           # Logic for RAG chain, memory, and function calling
├── .env.example
├── requirements.txt
├── main.py
```
