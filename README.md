# Backend with two REST APIs using FastAPI :

1. Document Ingestion API(done ready to digest any .pdf or .txt file)
    - Upload .pdf or .txt files(done)
    - Extract text, apply two chunking strategies (selectable)(done)
    - Generate embeddings & store in Pinecone/Qdrant/Weaviate/Milvus (pc connectiondone, storing done)
    - Save metadata in SQL/NoSQL DB (db connection done, storing the metadata done)
2. Conversational RAG API
    - Custom RAG (no RetrievalQAChain)(done)
    - Use Redis for chat memory(done using redis cloud)
    - Handle multi-turn queries(done)
    - Support interview booking (name, email, date, time) using  LLM(done)
    - Store booking info(done)


### Constraints:
No FAISS/Chroma, no UI, no RetrievalQAChain clean modular code following industry standards for typing and annotations

## 🎯 API Overview

### 1. **Document Ingestion API**
- **Endpoint**: `POST /documents/upload/`
- **Purpose**: Upload and process documents (.pdf, .txt)
- **Features**:
  - File upload with validation
  - Text extraction
  - Chunking (Fixed/Semantic strategies)
  - Embedding generation & storage (Pinecone)
  - Metadata storage (Neon PostgreSQL)

### 2. **Conversational RAG API**
- **Endpoint**: `POST /RAG/chat`
- **Purpose**: Chat with AI using knowledge base and memory
- **Features**:
  - Multi-turn conversations (Redis memory)
  - Knowledge base retrieval (optional)
  - Interview booking detection & storage
  - Session management (continue/restart)



## 🔄 Workflow Diagrams

### Document Ingestion Flow:
```
Upload File (.pdf/.txt)
    ↓
Extract Text (PyPDF/UTF-8)
    ↓
Choose Chunking Strategy (Fixed/Semantic)
    ↓
Apply Chunking
    ↓
Generate Embeddings (Pinecone Inference API)
    ↓
Store Vectors (Pinecone - default namespace)
    ↓
Save Metadata (Neon PostgreSQL)
    ↓
Return Response
```

### Conversational RAG Flow:
```
User Query
    ↓
Load History (Redis Cloud)
    ↓
Detect Booking Intent? ──→ YES → Extract Info → Save to DB
    ↓ NO
Retrieve Context (Pinecone) if knowledge_base=yes
    ↓
Generate Response (Groq LLM)
    ↓
Save to History (Redis)
    ↓
Return Response
```



## Status
- project initialization(done)
- uploading file(done)
- acceopting only the supported file type .pdf & .txt(done)
- text extraction using pypdf for .pdf and utf-8 decoding for .txt(done)
- selectable chunking(fixed, semantic) strategy(done)
- apply chunking strategy(done)
- embedding and storing both pinecone directly provides integrated interface for embedding models so we don't need to do embedding by ourself (done)
- saving document metadata in neon postgress(done)


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
|   |   ├── llm_wrapper.py           # custom LLM wrapper (groq)
│   │   ├── document_service.py      # Logic for text extraction, chunking, embedding
│   │   ├── vector_store_manager.py  # Pinecone/Qdrant connection and interaction
│   │   ├── llm_service.py           # Logic for RAG chain, memory, and function calling
├── .env.example
├── requirements.txt
├── main.py
```
