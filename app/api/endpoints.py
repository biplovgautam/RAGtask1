from fastapi import APIRouter, File, UploadFile
from app.services.llm_wrapper import GroqLLM
from typing import Annotated

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


@document_router.post('/uplaod/')
async def upload_document_file(
    # Use UploadFile to handle the file contents and metadata
    # Annotated[UploadFile, File(...)] ensures the parameter is correctly identified as an uploaded file
    file: Annotated[UploadFile, File()]
):
    """
    Handles a file upload request.
    
    For the RAG task, this is where you would call document_service.ingest_document(file).
    """
    
    # 1. Access the file's metadata
    # The 'file' object is an UploadFile instance.
    file_name = file.filename

    # 2. (Optional but recommended): Close the file stream.
    # We are not reading or saving the contents, but it's good practice.
    await file.close()

    # 3. Return the file name as requested
    return {"message": "File received successfully", "filename": file_name}
