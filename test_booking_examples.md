# Interview Booking - Date Context Examples

## ✅ Updated: Now Handles Relative Dates!

The system now understands relative date terms like "tomorrow", "next Monday", etc., and automatically calculates the correct YYYY-MM-DD date based on today's date.

---

## 📅 Current Date Context

The LLM now receives:
- **Today's date**: e.g., `2025-11-22 (Saturday)`
- **Tomorrow**: Automatically calculated as `2025-11-23`
- **Day after tomorrow**: Automatically calculated as `2025-11-24`

---

## 🧪 Test Examples

### Example 1: Book for Tomorrow
```bash
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want to book an interview for tomorrow at 2 PM. My name is John Doe and email is john@example.com",
    "session_id": "test_tomorrow"
  }'
```

**Expected Result:**
- LLM interprets "tomorrow" as `2025-11-23` (if today is 2025-11-22)
- Extracts: name, email, date (calculated), time
- Saves to database with correct date

---

### Example 2: Book for Day After Tomorrow
```bash
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Schedule an interview for the day after tomorrow at 10:00 AM. Name: Jane Smith, Email: jane@test.com",
    "session_id": "test_day_after"
  }'
```

**Expected Result:**
- Calculates correct date (today + 2 days)
- Converts "10:00 AM" to 24-hour format: "10:00"

---

### Example 3: Multi-Turn Conversation with "Tomorrow"
```bash
# First message
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I need to schedule an interview",
    "session_id": "multi_turn"
  }'

# LLM asks for details...

# Second message
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tomorrow at 3 PM works for me",
    "session_id": "multi_turn"
  }'

# Third message
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My name is Alex Brown, email alex@company.com",
    "session_id": "multi_turn"
  }'
```

**Expected Result:**
- LLM extracts "tomorrow" from conversation history
- Calculates date correctly
- Combines info from multiple messages
- Books when all fields are complete

---

### Example 4: Specific Date (Still Works)
```bash
curl -X POST "http://127.0.0.1:8000/RAG/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Book interview for 2025-12-01 at 14:00 for Sarah Lee, sarah@email.com",
    "session_id": "specific_date"
  }'
```

**Expected Result:**
- Uses exact date provided
- No calculation needed

---

## 🔍 What Changed

### 1. **Extraction Prompt Enhancement**
```python
IMPORTANT DATE CONTEXT:
- Today's date is: 2025-11-22 (Saturday)
- Use this to calculate relative dates like "tomorrow", "next Monday", etc.

Examples:
- "tomorrow" = 2025-11-23
- "day after tomorrow" = 2025-11-24
```

### 2. **Conversation Prompts Enhancement**
```python
CURRENT DATE: 2025-11-22 (Saturday)

Instructions:
- For relative dates (tomorrow, next week), calculate from today's date
```

### 3. **Dynamic Date Calculation**
- System automatically calculates:
  - Tomorrow: `today + timedelta(days=1)`
  - Day after tomorrow: `today + timedelta(days=2)`
- Provides examples directly in the prompt

---

## 🎯 Supported Relative Terms

The LLM can now interpret:
- ✅ **"tomorrow"**
- ✅ **"day after tomorrow"**
- ✅ **"next Monday/Tuesday/etc."** (LLM calculates)
- ✅ **"in 3 days"** (LLM calculates)
- ✅ **"next week"** (LLM calculates)

---

## ✅ Testing Checklist

1. **Test "tomorrow"**: Should calculate correct date
2. **Test "day after tomorrow"**: Should calculate correct date
3. **Test multi-turn with relative dates**: Should maintain context
4. **Test specific dates**: Should still work as before
5. **Check database**: Verify dates are in YYYY-MM-DD format

---

## 📊 Example Response

```json
{
  "response": "Great! I've scheduled your interview for John Doe on 2025-11-23 at 14:00. A confirmation will be sent to john@example.com.",
  "session_id": "test_tomorrow",
  "mode": "continue",
  "retrieved_chunks": 0,
  "booking_created": true
}
```

---

## 🗄️ Database Entry

```sql
SELECT * FROM interview_bookings WHERE name = 'John Doe';

-- Result:
id | name      | email           | date       | time  | created_at          | session_id
1  | John Doe  | john@example.com| 2025-11-23 | 14:00 | 2025-11-22 10:30:00 | test_tomorrow
```

---

## 🚀 Ready to Test!

The system is now fully date-aware and can handle natural language date references. Test it with:

1. Start your server (should auto-reload)
2. Try: `"book interview for tomorrow at 2 PM, name: Test User, email: test@test.com"`
3. Check database to verify correct date was saved!

---

**Status**: ✅ Date Context Fully Implemented
