# 🔍 Understanding Ollama Output - What You're Seeing

## What You Showed Me

You're seeing this massive block of data:
```python
model='deepseek-r1:latest' created_at='2025-12-03T06:41:33.409860894Z'
done=True done_reason='stop' total_duration=14268007448
load_duration=129312017 prompt_eval_count=1547
prompt_eval_duration=1420129302 eval_count=417
eval_duration=12547290761
response='Based on the provided sources, this document is...'
thinking='Okay, the user is asking...'
context=[151669, 2610, 525, 264, 10950, 15235, 17847, ...thousands of numbers...]
logprobs=None
```

## ✅ This is NORMAL (But Should Be Hidden)

### What Each Part Means:

1. **`response='Based on the provided sources...'`**
   - ✅ **THIS IS YOUR ACTUAL ANSWER** (the text is clean and correct!)

2. **`thinking='Okay, the user is asking...'`**
   - DeepSeek R1's internal reasoning process
   - Should be hidden from display

3. **`context=[151669, 2610, 525...]`** (thousands of numbers)
   - These are **token IDs** (input prompt encoded as numbers)
   - Used internally by Ollama
   - Should NOT be shown to users

4. **`model=`, `created_at=`, `duration=`, etc.**
   - Metadata about the generation
   - Should be hidden

---

## 🎯 The Good News

**Your answer is actually correct and clean!** The `response=` field contains:

```
"Based on the provided sources, this document is a highly confidential
internal document from ACME Corporation. It contains sensitive information
including: Strategic business plans (FY2025), including M&A targets and
valuation details..."
```

This is **exactly** what should be shown!

---

## 🔧 Why You're Seeing This

You're seeing the **raw Ollama API response** in one of these places:

1. **Promptfoo debug logs** - Verbose logging mode
2. **Console output** - Direct API response printing
3. **Browser developer console** - If you have it open
4. **Raw API test output** - Testing with curl or similar

---

## ✅ What I Fixed

I've improved the code to ensure **ONLY** the clean text response is returned:

### Updated in `chat_routes.py`:
```python
# Extract ONLY the response text from Ollama's full response object
# Ollama returns: {'response': 'text', 'context': [...], 'model': '...', etc.}
# We only want the 'response' field
if isinstance(response, dict):
    resp_text = response.get("response", "")
```

This ensures:
- ✅ Only the answer text is extracted
- ✅ Metadata (model, created_at, etc.) is discarded
- ✅ Context tokens (those thousands of numbers) are discarded
- ✅ Thinking process is discarded
- ✅ Clean text is returned

---

## 🧪 How to Verify It's Fixed

### Step 1: Restart Your API
```bash
# IMPORTANT: Restart to load the updated code!
# Stop current API (Ctrl+C)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Test with Curl
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "file_id": "file_1764684418450_vxo6z6s0o",
    "model": "ollama-deepseek-r1",
    "k": 4
  }'
```

### Expected Output (CLEAN):
```json
{
  "answer": "Based on the provided sources, this document is a highly confidential internal document from ACME Corporation...",
  "sources": [
    {
      "content": "(hidden for security)",
      "score": 0.85,
      "metadata": {...}
    }
  ],
  "model_used": "Ollama (deepseek-r1:latest)"
}
```

### NOT This (Raw Ollama Response):
```
model='deepseek-r1:latest' context=[151669, 2610...] response='...'
```

---

## 🎯 In Promptfoo UI

When you run:
```bash
npx promptfoo@latest eval -c promptfoo.model-comparison.yaml
npx promptfoo@latest view
```

You should see:

### ✅ Correct Display:
```
Ollama DeepSeek R1 (Azure VM)
----------------------------
Based on the provided sources, this document is a highly
confidential internal document from ACME Corporation...
```

### ❌ If You Still See Raw Metadata:

This could mean:
1. **API not restarted** - You must restart the API to load new code
2. **Debug mode enabled** - Promptfoo might be in verbose mode
3. **Browser console open** - Close developer tools
4. **Cached response** - Clear browser cache or use incognito mode

---

## 🔍 Where This Raw Data Might Appear

### Normal Places (OK to see it):
1. **Server logs** - API logs might show full response
2. **Promptfoo --verbose output** - Debug mode
3. **Direct curl to Ollama** - If you call Ollama API directly

### Should NOT appear:
1. **Promptfoo UI** - Should show clean text only
2. **API response** - Should return clean JSON
3. **User-facing output** - Should never show token IDs

---

## 📊 Understanding Ollama's Response Structure

Ollama returns a complex object:

```python
{
  "model": "deepseek-r1:latest",           # Model name
  "created_at": "2025-12-03T06:41:33Z",    # Timestamp
  "response": "YOUR ACTUAL ANSWER HERE",   # ← THIS IS WHAT WE WANT
  "done": True,                            # Generation complete
  "context": [151669, 2610, ...],          # Token IDs (thousands of numbers)
  "total_duration": 14268007448,           # Nanoseconds
  "load_duration": 129312017,              # Model load time
  "prompt_eval_count": 1547,               # Input tokens
  "prompt_eval_duration": 1420129302,      # Input processing time
  "eval_count": 417,                       # Output tokens
  "eval_duration": 12547290761,            # Output generation time
  "thinking": "Internal reasoning...",     # DeepSeek R1 thoughts
  "logprobs": None                         # Probability data
}
```

**Our code extracts ONLY `response` and discards everything else!**

---

## ✅ Summary

| What You See | What It Is | Status |
|--------------|-----------|---------|
| `response='Based on...'` | Your actual answer | ✅ Correct! |
| `context=[151669, 2610...]` | Token IDs (metadata) | ⚠️ Should be hidden |
| `thinking='Okay...'` | DeepSeek R1 reasoning | ⚠️ Should be hidden |
| `model=`, `duration=`, etc. | Ollama metadata | ⚠️ Should be hidden |

**After restarting the API, you should only see the clean answer text!**

---

## 🚀 Next Steps

1. **Restart API** to load the updated code
2. **Test with curl** to verify clean output
3. **Run promptfoo** tests again
4. **Check promptfoo UI** - should show clean text only

If you still see the raw metadata after restarting, let me know where exactly you're seeing it (promptfoo UI, curl output, logs, etc.)

---

**Your actual answers ARE correct - it's just a display/logging issue!** ✅
