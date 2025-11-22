# app/services/llm_service.py

'''
RAG & Chat Orchestration	
Contains the complex logic for the second API task: 
it initializes and runs the Custom RAG Chain, integrates Redis for chat memory, 
binds the Interview Booking Tool (Function Calling) to the LLM, 
and handles the multi-turn conversational flow.'''

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from .llm_wrapper import create_groq_llm
from .vector_store_manager import search_similar_chunks
from app.core.db import redis_client
from app.api.models import InterviewBooking, ConversationMode


class ConversationalRAGService:
    """
    Handles conversational RAG with Redis memory and interview booking detection.
    This is a completely separate service from document ingestion.
    """
    
    def __init__(self):
        """Initialize the LLM and set up system prompts."""
        self.llm = create_groq_llm(temperature=0.7, max_tokens=1024)
        self.max_history = 10  # Keep last 10 messages in memory
        
    def _get_redis_key(self, session_id: str) -> str:
        """Generate Redis key for a session."""
        return f"chat_history:{session_id}"
    
    def _get_chat_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieve chat history from Redis."""
        if not redis_client:
            return []
        
        try:
            key = self._get_redis_key(session_id)
            history_json = redis_client.get(key)
            
            if history_json:
                return json.loads(history_json)
            return []
        except Exception as e:
            print(f"Error retrieving chat history: {e}")
            return []
    
    def _save_chat_history(self, session_id: str, history: List[Dict[str, str]]) -> None:
        """Save chat history to Redis with expiration."""
        if not redis_client:
            return
        
        try:
            key = self._get_redis_key(session_id)
            # Keep only last N messages to avoid memory bloat
            trimmed_history = history[-self.max_history:]
            redis_client.setex(
                key,
                3600 * 24,  # Expire after 24 hours
                json.dumps(trimmed_history)
            )
        except Exception as e:
            print(f"Error saving chat history: {e}")
    
    def _clear_chat_history(self, session_id: str) -> None:
        """Clear chat history from Redis."""
        if not redis_client:
            return
        
        try:
            key = self._get_redis_key(session_id)
            redis_client.delete(key)
        except Exception as e:
            print(f"Error clearing chat history: {e}")
    
    def _format_chat_history(self, history: List[Dict[str, str]]) -> str:
        """Format chat history for LLM context."""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for msg in history[-6:]:  # Last 6 messages (3 turns)
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role.upper()}: {content}")
        
        return "\n".join(formatted)
    
    def _detect_booking_intent(self, query: str, history: List[Dict[str, str]] = None) -> bool:
        """
        Detect if user wants to book an interview.
        Checks both current query and recent conversation history.
        """
        booking_keywords = [
            "book", "schedule", "appointment", "interview",
            "meeting", "reserve", "set up", "arrange"
        ]
        
        # Check current query
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in booking_keywords):
            return True
        
        # Check if recent conversation history mentions booking
        if history:
            # Check last 4 messages for booking context
            recent_messages = history[-4:] if len(history) > 4 else history
            for msg in recent_messages:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in booking_keywords):
                    return True
        
        return False

    def _extract_booking_info(self, conversation: str) -> Optional[Dict[str, str]]:
        """
        Use LLM to extract booking information from conversation.
        Returns dict with name, email, date, time or None.
        """
        extraction_prompt = f"""
You are a helpful assistant that extracts interview booking information from conversations.

Analyze this conversation and extract the following information if provided:
- Name (person's full name)
- Email (valid email address)
- Date (in YYYY-MM-DD format)
- Time (in HH:MM format, 24-hour)

If any information is missing or unclear, return "MISSING" for that field.

Conversation:
{conversation}

Return ONLY a JSON object with this exact format (no other text):
{{"name": "...", "email": "...", "date": "...", "time": "..."}}
"""
        
        try:
            response = self.llm(extraction_prompt)
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                booking_data = json.loads(json_match.group())
                
                # Validate all fields are present and not "MISSING"
                required_fields = ["name", "email", "date", "time"]
                if all(
                    field in booking_data and 
                    booking_data[field] and 
                    booking_data[field].upper() != "MISSING"
                    for field in required_fields
                ):
                    return booking_data
        except Exception as e:
            print(f"Error extracting booking info: {e}")
        
        return None
    
    def _save_booking(self, booking_data: Dict[str, str], session_id: str, db: Session) -> bool:
        """Save booking information to database."""
        try:
            booking = InterviewBooking(
                name=booking_data["name"],
                email=booking_data["email"],
                date=booking_data["date"],
                time=booking_data["time"],
                session_id=session_id
            )
            db.add(booking)
            db.commit()
            return True
        except Exception as e:
            print(f"Error saving booking: {e}")
            db.rollback()
            return False
    
    def _retrieve_context(self, query: str, top_k: int = 3) -> Tuple[str, int]:
        """
        Retrieve relevant context from Pinecone vector store.
        Returns formatted context string and count of chunks.
        """
        try:
            matches = search_similar_chunks(query, top_k=top_k)
            
            if not matches:
                return "", 0
            
            # Format context from retrieved chunks
            context_parts = []
            for i, match in enumerate(matches, 1):
                text = match.get("metadata", {}).get("text", "")
                if text:
                    context_parts.append(f"[Context {i}]: {text}")
            
            return "\n\n".join(context_parts), len(matches)
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return "", 0
    
    def chat(
        self, 
        query: str, 
        session_id: str, 
        mode: ConversationMode,
        use_knowledge_base: bool,
        db: Session
    ) -> Dict:
        """
        Main conversational RAG logic.
        
        Args:
            query: User's question/message
            session_id: Unique session identifier
            mode: CONTINUE or RESTART
            use_knowledge_base: Whether to retrieve context from vector DB
            db: Database session for booking storage
            
        Returns:
            Dict with response, metadata, and booking status
        """
        # Handle restart mode
        if mode == ConversationMode.RESTART:
            self._clear_chat_history(session_id)
            history = []
        else:
            history = self._get_chat_history(session_id)
        
        # Detect booking intent (check query + history)
        is_booking_intent = self._detect_booking_intent(query, history)
        booking_created = False
        
        # If booking intent detected, check if we have enough info
        if is_booking_intent:
            # Add current query to temporary history for extraction
            temp_history = history + [{"role": "user", "content": query}]
            
            # Use FULL conversation history for booking extraction (not just last 6)
            full_conversation = []
            for msg in temp_history:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                full_conversation.append(f"{role.upper()}: {content}")
            
            conversation_text = "\n".join(full_conversation)
            
            booking_data = self._extract_booking_info(conversation_text)
            
            if booking_data:
                # We have complete booking info, save it
                booking_created = self._save_booking(booking_data, session_id, db)
                
                if booking_created:
                    response = f"Great! I've scheduled your interview for {booking_data['name']} on {booking_data['date']} at {booking_data['time']}. A confirmation will be sent to {booking_data['email']}."
                    
                    # Update history
                    history.append({"role": "user", "content": query})
                    history.append({"role": "assistant", "content": response})
                    self._save_chat_history(session_id, history)
                    
                    return {
                        "response": response,
                        "retrieved_chunks": 0,
                        "booking_created": True
                    }
        
        # Regular RAG flow: retrieve context based on knowledge_base setting
        if use_knowledge_base:
            context, num_chunks = self._retrieve_context(query)
        else:
            context = ""
            num_chunks = 0
        
        # Format history for LLM
        history_text = self._format_chat_history(history)
        
        # Build prompt
        if context:
            prompt = f"""You are a helpful AI assistant with access to a knowledge base. Use the provided context to answer questions accurately.

CONVERSATION HISTORY:
{history_text}

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUERY: {query}

Instructions:
- Answer based on the context and conversation history
- If user wants to book an interview, ONLY ask for these 4 details (don't ask about purpose, company, or topic):
  1. Full name
  2. Email address
  3. Date (YYYY-MM-DD format)
  4. Time (HH:MM format, 24-hour)
- Once you have all 4 details, confirm them back to the user
- Don't ask what the interview is for or who it's with
- Be conversational and helpful
- If context doesn't contain relevant information, say so politely

RESPONSE:"""
        else:
            prompt = f"""You are a helpful AI assistant.

CONVERSATION HISTORY:
{history_text}

USER QUERY: {query}

Instructions:
- Continue the conversation naturally
- If user wants to book an interview, ONLY collect these 4 details (nothing more):
  1. Full name
  2. Email address  
  3. Date (YYYY-MM-DD format)
  4. Time (HH:MM format, 24-hour)
- Don't ask what the interview is for, who it's with, or the topic
- Once you have all 4 details, confirm them
- Be friendly and professional

RESPONSE:"""
        
        # Get LLM response
        response = self.llm(prompt)
        
        # Update conversation history
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": response})
        self._save_chat_history(session_id, history)
        
        return {
            "response": response,
            "retrieved_chunks": num_chunks,
            "booking_created": booking_created
        }


# Singleton instance
_rag_service = None

def get_rag_service() -> ConversationalRAGService:
    """Get or create the RAG service singleton."""
    global _rag_service
    if _rag_service is None:
        _rag_service = ConversationalRAGService()
    return _rag_service