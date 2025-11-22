from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from app.services.llm_wrapper import GroqLLM
from app.services.document_service import extract_text_from_file_bytes, chunk_text
from app.api.models import IngestionResponse, ChunkingStrategy
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

@document_router.post('/upload/', response_model=IngestionResponse)
async def upload_document_file(
    file: Annotated[UploadFile, File(...)],
    chunking_strategy: Annotated[ChunkingStrategy, Form()] = ChunkingStrategy.FIXED
):
    """
    Handles a file upload request, restricted to .pdf and .txt files.
    Extracts text and prepares for chunking based on the selected strategy.
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
        
        # 6. Extract text from the file
        # We cast file_extension to the Literal type expected by the function
        text_content = extract_text_from_file_bytes(file_bytes, file_extension) # type: ignore
        
        # 7. Chunk the text based on the selected strategy
        chunks = chunk_text(text_content, chunking_strategy)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await file.close()

    # 8. Generate a unique document ID
    doc_id = str(uuid.uuid4())

    # 9. Return the result using the Pydantic model
    return IngestionResponse(
        message="File processed and chunked successfully",
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