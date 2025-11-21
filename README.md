# FastAPI app with 2 end points :
1. Document ingestion API:
    - accepts(pdf,txt) files, extract text, chunks using selectable stratigies, embed chunks, store embeddings in vectordb and metadata in an RDB/noSQL Db.
2. Conversation RAG API:
    - support multi-turn conversational retrieval-augmented generation (RAG) with Redis for session memory, a custom retrieval + LLM composition (no RetrievalQAChain), and an LLM-driven interview booking flow that saves bookings.



- project initialization (done)
- both api endpoints  are yet to be implemented.


## project architecture
```
RAGtask1/
├── app/
│   ├── api/
│   │   ├── endpoints.py             # FastAPI router definitions
│   │   ├── models.py                # Pydantic models for API requests/responses
│   ├── core/
│   │   ├── config.py                # Environment variables and settings
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
