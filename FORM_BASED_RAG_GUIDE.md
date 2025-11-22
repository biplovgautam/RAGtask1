# Form-Based Conversational RAG - Updated Guide

## ✅ Changes Implemented

The `/RAG/chat` endpoint now uses **Form data** (like the upload endpoint) with **selectable dropdowns** in Swagger UI!

---

## 🎯 New Features

### 1. **Form-Based Parameters** (Like Upload Endpoint)
- `query`: Text input (required)
- `mode`: Dropdown selector (CONTINUE / RESTART)
- `knowledge_base`: Dropdown selector (YES / NO)
- `session_id`: Text input (default: "default")

### 2. **Knowledge Base Toggle**
- **YES**: Retrieves context from Pinecone vector DB (full RAG)
- **NO**: Skips vector retrieval (pure LLM conversation)

---

## 📊 API Usage

### Endpoint: `POST /RAG/chat`

#### Form Fields (in Swagger UI):

| Field | Type | Options | Default | Description |
|-------|------|---------|---------|-------------|
| `query` | text | - | required | User's message/question |
| `mode` | dropdown | `continue`, `restart` | `continue` | Memory management |
| `knowledge_base` | dropdown | `yes`, `no` | `yes` | Use vector DB or not |
| `session_id` | text | - | `default` | Session identifier |

---

## 🧪 Testing in Swagger UI

### 1. Go to: http://127.0.0.1:8000/docs
### 2. Find: `POST /RAG/chat`
### 3. Click "Try it out"

### Example 1: With Knowledge Base (RAG Mode)
```
query: "What is machine learning?"
mode: continue (dropdown)
knowledge_base: yes (dropdown)
session_id: test1
```
**Result**: Will search Pinecone for relevant documents and answer using context

---

### Example 2: Without Knowledge Base (Pure Chat)
```
query: "Tell me a joke"
mode: continue (dropdown)
knowledge_base: no (dropdown)
session_id: test2
```
**Result**: Direct LLM response without vector search (faster, no context needed)

---

### Example 3: Restart Conversation
```
query: "Start fresh conversation"
mode: restart (dropdown)
knowledge_base: yes (dropdown)
session_id: test1
```
**Result**: Clears Redis history for test1, starts new conversation

---

### Example 4: Interview Booking (No KB Needed)
```
query: "Book interview for John Doe, john@test.com, 2025-11-25, 14:00"
mode: continue (dropdown)
knowledge_base: no (dropdown)
session_id: booking1
```
**Result**: Extracts info and saves booking (no vector search needed)

---

## 📄 Response Format

```json
{
  "response": "Machine learning is a subset of AI...",
  "session_id": "test1",
  "mode": "continue",
  "knowledge_base_used": true,
  "retrieved_chunks": 3,
  "booking_created": false
}
```

**New Field**: `knowledge_base_used` - tells you if context was retrieved

---

## 🔄 Comparison: Knowledge Base ON vs OFF

### Knowledge Base = YES (RAG Mode)
```
User: "What did Biplov study?"
↓
1. Search Pinecone for "Biplov study"
2. Find relevant chunks (e.g., "biplov gautam bsc computer science")
3. LLM answers using context
↓
Response: "Biplov studied BSc Hons Computer Science with AI"
```

### Knowledge Base = NO (Chat Mode)
```
User: "What did Biplov study?"
↓
1. Skip Pinecone search
2. LLM uses only conversation history
↓
Response: "I don't have that information in our conversation"
```

---

## 🎯 When to Use Each Mode

### Use `knowledge_base = YES`:
- ✅ Questions about uploaded documents
- ✅ Fact-based queries
- ✅ Need accurate information from your knowledge base
- ✅ Document-specific questions

### Use `knowledge_base = NO`:
- ✅ General conversation
- ✅ Interview booking (already has all info in query)
- ✅ Math calculations
- ✅ Creative tasks (jokes, stories)
- ✅ Faster responses (no vector search delay)

---

## 🚀 cURL Examples

### With Knowledge Base:
```bash
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=What is AI?&mode=continue&knowledge_base=yes&session_id=test1"
```

### Without Knowledge Base:
```bash
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=Tell me a joke&mode=continue&knowledge_base=no&session_id=test2"
```

### Restart Mode:
```bash
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=New topic&mode=restart&knowledge_base=yes&session_id=test1"
```

---

## 📊 Performance Comparison

| Mode | Vector Search | Speed | Use Case |
|------|--------------|-------|----------|
| KB = YES | ✅ Enabled | Slower (~500-1000ms) | Document Q&A |
| KB = NO | ❌ Disabled | Faster (~200-400ms) | General chat |

---

## ✅ Benefits of This Approach

1. ✅ **User-friendly**: Dropdown selectors in Swagger UI (like chunking_strategy)
2. ✅ **Flexible**: Turn vector search on/off per request
3. ✅ **Efficient**: Save resources when context not needed
4. ✅ **Consistent**: Same Form-based approach as upload endpoint
5. ✅ **Clear**: Response shows if KB was actually used

---

## 🎉 Ready to Test!

1. Server auto-reloads with changes
2. Go to: http://127.0.0.1:8000/docs
3. Try `/RAG/chat` with dropdown selectors
4. Test both modes (yes/no) and see the difference!

---

**Status**: ✅ Form-Based RAG with Knowledge Base Toggle Implemented!
