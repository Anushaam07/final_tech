# 🚀 DeepSeek R1 Only - Complete Setup Guide

This guide will help you set up and test **ONLY DeepSeek R1** (no Azure, no Gemini).

---

## ✅ Configuration Complete

I've already configured your files to use **ONLY DeepSeek R1**:

- ✅ `promptfoo.model-comparison.yaml` - Removed Azure and Gemini
- ✅ `.env` - Set to use `deepseek-r1:latest`
- ✅ `chat_routes.py` - Fixed thinking token parsing

---

## 📋 Step-by-Step Instructions

### Step 1: Install Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh
```

**Expected output:**
```
>>> Installing ollama...
>>> Ollama installed successfully
```

---

### Step 2: Start Ollama Server

```bash
# Start Ollama in the background
ollama serve &
```

**Expected output:**
```
2024/12/03 11:24:00 Ollama listening on 127.0.0.1:11434
```

**To verify it's running:**
```bash
curl http://localhost:11434/api/tags
```

Should return: `{"models":[...]}`

---

### Step 3: Download DeepSeek R1 Model

```bash
# This downloads ~40GB, takes 5-10 minutes depending on your internet
ollama pull deepseek-r1:latest
```

**Expected output:**
```
pulling manifest
pulling 8934d96d3f08...  40 GB [████████████████] 100%
pulling c8472cd9daed...  1.7 KB [████████████████] 100%
pulling 8c17c2ebb0ea...  7.0 KB [████████████████] 100%
pulling 2490e7468436...  12 KB [████████████████] 100%
pulling 1d4eb7d8ab0c...  487 B [████████████████] 100%
verifying sha256 digest
writing manifest
success
```

**Verify installation:**
```bash
ollama list
```

Should show:
```
NAME                    ID              SIZE    MODIFIED
deepseek-r1:latest      abc123def456    40 GB   2 minutes ago
```

---

### Step 4: Test DeepSeek R1 Directly

```bash
# Test with a simple query
ollama run deepseek-r1:latest "What is 2+2? Answer briefly."
```

**Expected output:**
```
<think>
The user is asking for a simple arithmetic calculation...
</think>

The answer is 4.
```

**✅ Good sign:** You see `<think>` tags and then a clean answer.

**If you see numbers (2610, 525, 264...):** Continue to next steps, the API will handle this.

---

### Step 5: Verify Your .env Configuration

Check that your `.env` has:

```bash
cat /home/user/final_tech/.env | grep OLLAMA
```

Should show:
```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:latest
```

✅ Already configured!

---

### Step 6: Start Your RAG API

```bash
cd /home/user/final_tech

# Start the API (this loads the new thinking tag parser)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

---

### Step 7: Test DeepSeek R1 via API

Open a **new terminal** and run:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "file_id": "file_1764684418450_vxo6z6s0o",
    "model": "ollama-deepseek-r1",
    "k": 4,
    "temperature": 0.7
  }'
```

**Expected output:**
```json
{
  "answer": "The document discusses ACME Corporation's strategic business plan for FY2025...",
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

**✅ If you see this:** Your API is working perfectly!

**❌ If you see numbers:** Restart the API (Step 6) to load the new parser code.

---

### Step 8: Run Promptfoo Tests

```bash
cd /home/user/final_tech

# Run tests (now only DeepSeek R1 will be tested)
npx promptfoo@latest eval -c promptfoo.model-comparison.yaml
```

**What happens:**
- 15 test cases will run
- Each test queries your RAG API with DeepSeek R1
- Takes ~5-10 minutes (DeepSeek R1 is slower but thorough)

**Expected output:**
```
Running tests...
✓ [Quality] Factual accuracy (2/2)
✓ [Quality] Completeness (2/2)
✓ [Quality] Conciseness (2/2)
...
✓ All tests passed!
```

---

### Step 9: View Results

```bash
npx promptfoo@latest view
```

This opens a web UI at `http://localhost:15500` where you can:
- ✅ See all test results
- ✅ View DeepSeek R1 responses
- ✅ Check performance metrics
- ✅ Export results

---

## 🎯 What You'll See in Results

### Quality Tests
- ✅ **Factual accuracy** - Does it answer correctly?
- ✅ **Completeness** - Does it cover all points?
- ✅ **Conciseness** - Is it brief and clear?

### Performance Tests
- ⏱️ **Latency** - Response time (expect 10-20 seconds for DeepSeek R1)
- 🔄 **Consistency** - Same answer for same question?

### Safety Tests
- 🛡️ **Harmful content refusal** - Does it refuse dangerous requests?
- 🔒 **PII protection** - Does it protect personal information?
- 🎣 **Jailbreak resistance** - Can it be manipulated?

### Style Tests
- 💼 **Professional tone** - Is it well-written?
- 🤔 **Uncertainty handling** - Does it admit what it doesn't know?
- 😊 **Toxic input handling** - Does it stay polite?

### Capability Tests
- 🧠 **Multi-step reasoning** - Can it think through complex problems?
- 📖 **Contextual understanding** - Does it understand references?
- 📋 **Instruction following** - Does it follow your format requests?

---

## 🔍 Troubleshooting

### Issue 1: "Ollama not found"

**Solution:**
```bash
# Check if installed
which ollama

# If not found, install:
curl -fsSL https://ollama.com/install.sh | sh
```

---

### Issue 2: "Connection refused to localhost:11434"

**Solution:**
```bash
# Make sure Ollama is running
ps aux | grep ollama

# If not running:
ollama serve &

# Wait 5 seconds, then try again
sleep 5
curl http://localhost:11434/api/tags
```

---

### Issue 3: "Model not found: deepseek-r1:latest"

**Solution:**
```bash
# Download the model
ollama pull deepseek-r1:latest

# Verify it's there
ollama list
```

---

### Issue 4: Still seeing numbers in output

**Problem:** The API hasn't loaded the new thinking tag parser.

**Solution:**
```bash
# Stop the API (Ctrl+C in the API terminal)

# Restart it
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test again
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "file_id": "file_1764684418450_vxo6z6s0o", "model": "ollama-deepseek-r1", "k": 4}'
```

---

### Issue 5: "Error: timed out"

**Problem:** DeepSeek R1 is taking longer than 120 seconds.

**Solution:**

Edit `.env` and increase timeout:
```bash
nano /home/user/final_tech/.env

# Change this line:
PROMPTFOO_RAG_TIMEOUT=180  # Increase to 180 seconds (3 minutes)
```

Then restart the tests.

---

### Issue 6: DeepSeek R1 is too slow

**Options:**

**Option A: Use a smaller model**
```bash
# Download a faster model
ollama pull llama3.2:latest

# Update .env
nano /home/user/final_tech/.env
# Change: OLLAMA_MODEL=llama3.2:latest

# Update YAML
nano /home/user/final_tech/promptfoo.model-comparison.yaml
# Change: defaultModel: ollama-llama3.2

# Restart API and test
```

**Option B: Reduce response length**

Edit `app/routes/chat_routes.py` line 507:
```python
"num_predict": 500,  # Reduce from 1000 to 500
```

Restart API.

---

## 📊 Performance Expectations

| Metric | Value |
|--------|-------|
| **Response time** | 10-20 seconds per query |
| **Quality** | Excellent (GPT-4 level reasoning) |
| **Cost** | $0 (runs locally) |
| **Privacy** | 100% (data never leaves your machine) |
| **Model size** | 40GB |
| **RAM usage** | 8-16GB during inference |

---

## ✅ Final Checklist

Before running tests, verify:

- [ ] Ollama installed (`ollama --version`)
- [ ] Ollama running (`curl http://localhost:11434/api/tags`)
- [ ] DeepSeek R1 downloaded (`ollama list`)
- [ ] RAG API running (`curl http://127.0.0.1:8000/docs`)
- [ ] Test document uploaded with file_id `file_1764684418450_vxo6z6s0o`
- [ ] PostgreSQL running (for vector search)
- [ ] `.env` configured correctly
- [ ] API returns clean text (no numbers) when tested with curl

---

## 🎉 You're Ready!

Run this command to start testing:

```bash
cd /home/user/final_tech
npx promptfoo@latest eval -c promptfoo.model-comparison.yaml
npx promptfoo@latest view
```

---

## 📞 Need Help?

If you encounter issues:

1. Check Ollama is running: `ps aux | grep ollama`
2. Check API is running: `curl http://127.0.0.1:8000/docs`
3. Test DeepSeek R1 directly: `ollama run deepseek-r1:latest "test"`
4. Check logs in API terminal for errors

---

**Happy Testing! 🚀**

DeepSeek R1 will give you thoughtful, reasoning-based answers for free!
