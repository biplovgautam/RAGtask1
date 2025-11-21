# app/services/llm_service.py

'''
RAG & Chat Orchestration	
Contains the complex logic for the second API task: 
it initializes and runs the Custom RAG Chain, integrates Redis for chat memory, 
binds the Interview Booking Tool (Function Calling) to the LLM, 
and handles the multi-turn conversational flow.'''


from .llm_wrapper import GroqLLM