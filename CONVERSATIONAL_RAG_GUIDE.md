# Conversational RAG API - Implementation Guide

## ✅ Complete Implementation

The Conversational RAG API is now fully implemented as a **separate system** from document ingestion.

---

## 🏗️ Architecture

### Key Components:

1. **`app/api/models.py`**
   - `ConversationMode` enum: `CONTINUE` | `RESTART`
   - `ChatRequest`: Request model (query, mode, session_id)
   - `ChatResponse`: Response model (response, metadata, booking status)
   - `InterviewBooking`: SQLAlchemy model for storing bookings

2. **`app/services/llm_service.py`**
   - `ConversationalRAGService`: Main orchestration class
   - Redis memory management
   - Context retrieval from Pinecone
   - Interview booking detection & extraction
   - Multi-turn conversation handling

3. **`app/api/endpoints.py`**
   - `POST /RAG/chat`: Main conversational endpoint

4. **`app/core/db.py`**
   - Redis connection setup
   - Automatic connection with fallback

---

## 🚀 API Usage

### Endpoint: `POST /RAG/chat`

#### Request Body:
```json
{
  "query": "What is machine learning?",
  "mode": "continue",
  "session_id": "user123"
}
```

#### Parameters:
- **`query`** (required): User's message/question
- **`mode`** (optional): 
  - `"continue"` (default): Continue with chat history
  - `"restart"`: Clear history and start fresh
- **`session_id`** (optional): Session identifier (default: "default")

#### Response:
```json
{
  "response": "Machine learning is...",
  "session_id": "user123",
  "mode": "continue",
  "retrieved_chunks": 2,
  "booking_created": false
}
```

---

## 🔄 Features

### 1. **Multi-Turn Conversations**
- Redis stores last 10 messages per session
- 24-hour expiration on chat history
- Session-based isolation (multiple users supported)

### 2. **Context Retrieval (RAG)**
- Automatically searches Pinecone for relevant chunks
- Top 3 most similar documents used as context
- Seamless integration with document ingestion vectors

### 3. **Interview Booking**
- Detects booking intent via keywords
- Extracts: name, email, date (YYYY-MM-DD), time (HH:MM)
- Stores in `interview_bookings` table in Neon PostgreSQL
- Automatic confirmation response

### 4. **Memory Management**
- **CONTINUE mode**: Maintains conversation context
- **RESTART mode**: Clears Redis history
- Efficient trimming (keeps last 10 messages)

---

## 📊 Workflow

```
User Query → [Redis: Load History] → [Detect Booking Intent?]
                                           ↓
                                    [YES: Extract Info]
                                           ↓
                                    [Complete? → Save to DB]
                                           ↓
                                    [NO: Regular RAG Flow]
                                           ↓
                          [Pinecone: Retrieve Context] → [LLM: Generate Response]
                                           ↓
                               [Redis: Save History] → Return Response
```

---

## 🧪 Testing Examples

### Example 1: Simple Question
```bash
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "mode": "continue",
    "session_id": "test1"
  }'
```

### Example 2: Multi-Turn Conversation
```bash
# First message
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Python", "session_id": "test2"}'

# Follow-up (will have context)
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are its main features?", "session_id": "test2"}'
```

### Example 3: Interview Booking
```bash
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want to book an interview for John Doe, email john@example.com, on 2025-11-25 at 14:00",
    "session_id": "booking1"
  }'
```

### Example 4: Restart Conversation
```bash
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Start fresh conversation",
    "mode": "restart",
    "session_id": "test2"
  }'
```

---

## 🔧 Environment Setup

### Required Environment Variables:

Add to your `.env` file:
```env
# Existing variables
PINECONE_API_KEY=your_pinecone_key
DATABASE_URL=your_neon_postgres_url
GROQ_LLM_API=your_groq_api_key

# New for Conversational RAG
REDIS_URL=redis://localhost:6379/0
```

### Start Redis (if not running):
```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis
```

---

## 📁 Database Schema

### `interview_bookings` Table:
```sql
CREATE TABLE interview_bookings (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    date VARCHAR NOT NULL,
    time VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    session_id VARCHAR
);
```

---

## 🎯 Key Differences from Document Ingestion

| Feature | Document Ingestion | Conversational RAG |
|---------|-------------------|-------------------|
| Purpose | Store documents | Chat with AI |
| Endpoint | `/documents/upload/` | `/RAG/chat` |
| Memory | None | Redis (24h) |
| Context | Creates vectors | Retrieves vectors |
| Booking | N/A | Detects & stores |
| Multi-turn | No | Yes |

---

## 🔍 How It Works

### 1. **Conversation Flow**
   - User sends query with session_id
   - System loads Redis history for that session
   - Checks for booking intent keywords
   - Retrieves relevant context from Pinecone
   - Sends query + history + context to LLM
   - Saves response to Redis
   - Returns formatted response

### 2. **Booking Detection**
   - Keywords: "book", "schedule", "appointment", "interview"
   - LLM extracts structured data (JSON)
   - Validates all required fields present
   - Saves to PostgreSQL if complete
   - Returns confirmation message

### 3. **Memory Management**
   - Redis key format: `chat_history:{session_id}`
   - JSON array of message objects
   - Auto-trimmed to last 10 messages
   - 24-hour TTL (auto-expires)

---

## ✅ Testing Checklist

- [ ] Start Redis server
- [ ] Start FastAPI server (`uvicorn main:app --reload`)
- [ ] Test simple query (no history)
- [ ] Test multi-turn conversation (same session_id)
- [ ] Test RESTART mode (clears history)
- [ ] Test with uploaded documents (context retrieval)
- [ ] Test booking flow (complete info)
- [ ] Test booking flow (partial info - should prompt)
- [ ] Check `interview_bookings` table in Neon DB

---

## 🐛 Troubleshooting

### Redis Connection Failed
- Check Redis is running: `redis-cli ping` (should return "PONG")
- Verify `REDIS_URL` in `.env`
- System falls back gracefully (no memory, but still works)

### No Context Retrieved
- Upload documents first via `/documents/upload/`
- Check Pinecone has data: query `/documents/test-retrieval/test`

### Booking Not Saving
- Check Neon PostgreSQL connection
- Verify all fields: name, email, date (YYYY-MM-DD), time (HH:MM)
- Check database logs in terminal

---

## 🎉 Success Indicators

✅ Server starts without errors  
✅ Redis connection confirmed (green checkmark in logs)  
✅ Chat endpoint returns responses  
✅ Follow-up questions maintain context  
✅ RESTART mode clears history  
✅ Bookings save to database  
✅ Context retrieved when available  

---

## 📝 Notes

- **Completely independent** from document ingestion
- **No RetrievalQAChain** (custom implementation)
- **Session-based** (supports multiple users)
- **Graceful degradation** (works without Redis, just no memory)
- **Production-ready** with proper error handling

---

**Status**: ✅ Fully Implemented & Ready for Testing
