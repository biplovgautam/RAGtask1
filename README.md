# FastAPI app with 2 end points :
1. Document ingestion API:
    - accepts(pdf,txt) files, extract text, chunks using selectable stratigies, embed chunks, store embeddings in vectordb and metadata in an RDB/noSQL Db.
2. Conversation RAG API:
    - support multi-turn conversational retrieval-augmented generation (RAG) with Redis for session memory, a custom retrieval + LLM composition (no RetrievalQAChain), and an LLM-driven interview booking flow that saves bookings.



- project initialization (done)
- both api endpoints  are yet to be implemented.