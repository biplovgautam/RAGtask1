from fastapi import FastAPI
from llmwrapper import GroqLLM


app = FastAPI()

# --- 1. INITIALIZE THE LLM INSTANCE ---
# Create the LLM instance globally so it is only initialized once
# when the application starts, not on every request.
try:
    llm = GroqLLM()
except ValueError as e:
    # Handle the case where the API key is missing before the app starts
    print(f"Error initializing GroqLLM: {e}")
    llm = None # Set to None or handle as a critical startup failure

@app.get('/')
async def hello_world():
    return ("hello world")




@app.get('/llmtest/{string}')
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