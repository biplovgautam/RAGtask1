from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from app.services.llm_wrapper import GroqLLM
from app.services.document_service import extract_text_from_file_bytes, chunk_text, save_document_metadata
from app.services.vector_store_manager import embed_and_store_chunks, search_similar_chunks
from app.api.models import IngestionResponse, ChunkingStrategy, ChatRequest, ChatResponse, ConversationMode, KnowledgeBaseMode
from app.core.db import get_db
from sqlalchemy.orm import Session
from typing import Annotated
import os
import uuid

router = APIRouter()

# --- 1. INITIALIZE THE LLM INSTANCE ---
# Create the LLM instance globally so it is only initialized once
# when the application starts, not on every request.
try:
    llm = GroqLLM()
except ValueError as e:
    # Handle the case where the API key is missing before the app starts
    print(f"Error initializing GroqLLM: {e}")
    llm = None # Set to None or handle as a critical startup failure

@router.get('/')
async def hello_world():
    return ("hello world")




@router.get('/llmtest/{string}')
async def llmtest(string: str):
    """
    Takes the user's string query and passes it to the GroqLLM for an answer.
    """
    
    if not llm:
        return {"error": "LLM not initialized due to missing API key."}
        
    # The string path parameter holds the user's query.
    user_query = string
    
    # LangChain's LLM components are typically synchronous, so we run
    # the synchronous call within FastAPI's async environment.
    # The 'invoke' method executes the synchronous _call method you defined.
    # Note: For production use, you might use 'run_in_threadpool' or 
    # a dedicated background task, but a simple synchronous call is fine here 
    # as the requests library handles the waiting.
    
    # We call the LLM instance directly with the query string
    llm_response = llm(user_query) 
    
    # Return the LLM's answer as a JSON response
    return {
        "query": user_query,
        "answer": llm_response
    }






# endpoint for the docuemnt ingestion

document_router = APIRouter(
    prefix="/documents",
    tags=["Document Ingestion"]
)

# --- Defining allowed extensions ---
ALLOWED_EXTENSIONS = {'.pdf', '.txt'}

@document_router.get('/test-retrieval/{query}')
async def test_retrieval(query: str):
    """
    Test endpoint to check if vector retrieval works.
    Searches for chunks similar to the query string.
    """
    try:
        matches = search_similar_chunks(query)
        
        # Extract only JSON-serializable data from Pinecone matches
        serializable_results = []
        for match in matches:
            serializable_results.append({
                "id": match.get("id", ""),
                "score": match.get("score", 0.0),
                "metadata": match.get("metadata", {})
            })
        
        return {
            "query": query, 
            "num_results": len(serializable_results),
            "results": serializable_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@document_router.post('/upload/', response_model=IngestionResponse)
async def upload_document_file(
    file: Annotated[UploadFile, File(...)],
    chunking_strategy: Annotated[ChunkingStrategy, Form()] = ChunkingStrategy.FIXED,
    db: Session = Depends(get_db)
):
    """
    Handles a file upload request, restricted to .pdf and .txt files.
    Extracts text, chunks it, embeds/stores in Pinecone, and saves metadata to DB.
    """
    
    # 1. Access the file's metadata
    file_name = file.filename

    # 2. If file_name is None
    if not file_name:
        raise HTTPException(status_code=400, detail="File must have a name.")
    
    # 3. Get the file extension
    file_extension = os.path.splitext(file_name)[1].lower()

    # 4. Check if the extension is in our allowed set
    if file_extension not in ALLOWED_EXTENSIONS:
        await file.close() 
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Only .pdf and .txt files are allowed."
        )
    
    try:
        # 5. Read the file content
        file_bytes = await file.read()
        file_size = len(file_bytes)
        
        # 6. Extract text from the file
        # We cast file_extension to the Literal type expected by the function
        text_content = extract_text_from_file_bytes(file_bytes, file_extension) # type: ignore
        
        # 7. Chunk the text based on the selected strategy
        chunks = chunk_text(text_content, chunking_strategy)
        
        # 8. Generate a unique document ID
        doc_id = str(uuid.uuid4())
        
        # 9. Embed and Store in Pinecone (using integrated embeddings)
        # This will generate embeddings and upsert them to the 'ragtask1' index
        embed_and_store_chunks(chunks, doc_id)
        
        # 10. Save Metadata to Neon PostgreSQL
        save_document_metadata(
            db=db,
            document_id=doc_id,
            filename=file_name,
            chunking_strategy=chunking_strategy,
            num_chunks=len(chunks),
            file_size=file_size
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch other errors (like DB or Pinecone issues)
        print(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        await file.close()

    # 11. Return the result using the Pydantic model
    return IngestionResponse(
        message="File processed, embedded, and stored successfully",
        filename=file_name,
        document_id=doc_id,
        chunking_strategy=chunking_strategy,
        extracted_text_length=len(text_content),
        num_chunks=len(chunks)
    )





# endpoints for the conversational RAG

rag_router = APIRouter(
    prefix= "/RAG",
    tags=["Conversational RAG"]
)

@rag_router.get("/")
async def check():
    return ("this is jsut to chek the endpoint /RAG/")


@rag_router.post("/chat", response_model=ChatResponse)
async def conversational_rag(
    query: Annotated[str, Form(...)],
    mode: Annotated[ConversationMode, Form()] = ConversationMode.CONTINUE,
    knowledge_base: Annotated[KnowledgeBaseMode, Form()] = KnowledgeBaseMode.YES,
    session_id: Annotated[str, Form()] = "default",
    db: Session = Depends(get_db)
):
    """
    Conversational RAG endpoint with Redis memory management and Form-based parameters.
    
    This endpoint is completely separate from document ingestion.
    It provides:
    - Multi-turn conversations with memory (Redis)
    - Optional context retrieval from Pinecone vector store (based on knowledge_base)
    - Interview booking detection and storage
    - Session management (continue/restart)
    
    Args:
        query: User's message/question (Form field)
        mode: Conversation mode - CONTINUE or RESTART (Form dropdown)
        knowledge_base: Whether to use vector DB - YES or NO (Form dropdown)
        session_id: Session identifier (Form field, default: "default")
        db: Database session for booking storage
        
    Returns:
        ChatResponse with LLM answer, metadata, and booking status
    """
    from app.services.llm_service import get_rag_service
    
    try:
        # Get the RAG service
        rag_service = get_rag_service()
        
        # Convert knowledge_base enum to boolean
        use_knowledge_base = (knowledge_base == KnowledgeBaseMode.YES)
        
        # Process the chat request
        result = rag_service.chat(
            query=query,
            session_id=session_id,
            mode=mode,
            use_knowledge_base=use_knowledge_base,
            db=db
        )
        
        # Return response
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            mode=mode,
            knowledge_base_used=use_knowledge_base,
            retrieved_chunks=result.get("retrieved_chunks", 0),
            booking_created=result.get("booking_created", False)
        )
        
    except Exception as e:
        print(f"Error in conversational RAG: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )