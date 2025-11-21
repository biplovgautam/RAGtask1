'''
Sets up the SQLAlchemy engine for Neon PostgreSQL database. 
Most importantly, it defines the get_db function, which FastAPI 
uses as a Dependency to provide a fresh, managed database connection for every request.
'''