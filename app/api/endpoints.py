'''
API Routers	Defines the actual @app.post() and @app.get() decorators 
(using FastAPI's APIRouter). It handles input from the client 
(e.g., query string, uploaded file), calls the necessary functions in the 
services layer, and structures the final HTTP response.'''