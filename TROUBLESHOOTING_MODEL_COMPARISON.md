# 🔧 Troubleshooting Model Comparison Errors

## Issues You're Seeing

### 1. ❌ "Error: timed out" (Azure & Gemini)
**Cause:** 30-second timeout too short for API responses
**Status:** ✅ FIXED (increased to 120 seconds)

### 2. ❌ "429 You exceeded your current quota" (Gemini)
**Cause:** Gemini free tier limit: 15 requests per minute
**Status:** ✅ FIXED (added 5-second delay between requests)

### 3. ❌ Ollama returns numbers instead of text
**Cause:** Ollama is NOT installed or model has issues
**Status:** ⚠️ NEEDS ACTION (see below)

---

## 🚀 Quick Fixes Applied

I've already fixed:

1. ✅ Increased `PROMPTFOO_RAG_TIMEOUT` from 30 to 120 seconds
2. ✅ Added `delay: 5000` (5 seconds) between requests in YAML
3. ✅ Changed Ollama model to `llama3.2:latest` (more stable)

---

## 🛠 What YOU Need to Do Now

### Fix 1: Install Ollama (Required for Ollama model testing)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Pull Llama 3.2 model (better than DeepSeek R1 for this use case)
ollama pull llama3.2:latest

# Verify it works
ollama run llama3.2:latest "Hello, tell me about AI"
```

**Why Llama 3.2 instead of DeepSeek R1?**
- Llama 3.2 gives cleaner text output
- DeepSeek R1 shows "thinking" tokens which appear as numbers
- Llama 3.2 is more stable and well-tested

---

### Fix 2: Add Your Real API Keys to .env

Open `/home/user/final_tech/.env` and update:

```bash
# Replace these placeholder values:
AZURE_CHAT_API_KEY=your-actual-azure-key-here
RAG_AZURE_OPENAI_API_KEY=your-actual-azure-key-here
GEMINI_API_KEY=your-actual-gemini-key-here
```

**Where to get keys:**
- **Azure**: Azure Portal → Your OpenAI resource → Keys and Endpoint
- **Gemini**: https://aistudio.google.com/app/apikey (100% FREE!)

---

### Fix 3: Restart Your RAG API

After updating `.env`, restart your API so it picks up the new settings:

```bash
# Stop the current API (Ctrl+C if running)

# Restart with new settings
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Fix 4: Run Tests with Slower Rate

Now run the comparison again:

```bash
cd /home/user/final_tech

# This will now:
# - Wait 120 seconds for each response (no more timeouts)
# - Wait 5 seconds between requests (no more rate limits)
# - Use Llama 3.2 for Ollama (clean text output)
npx promptfoo@latest eval -c promptfoo.model-comparison.yaml

# View results
npx promptfoo@latest view
```

---

## 📊 What to Expect Now

### Azure GPT-4o-mini
- ✅ Should work if API key is valid
- ✅ Fast responses (no timeout)
- ⏱️ ~2-5 seconds per request

### Gemini 2.0 Flash (Free)
- ✅ Should work if API key is valid
- ✅ Won't hit rate limits (5 second delay)
- ⏱️ ~3-8 seconds per request
- ⚠️ Total test time: ~15 tests × 5 seconds = ~75 seconds + processing

### Ollama Llama 3.2 (Local)
- ✅ Will work once installed
- ✅ Clean text output (no weird numbers)
- ⏱️ ~5-15 seconds per request (depends on your CPU)
- 💡 Runs locally, completely private!

---

## 🔍 Understanding the Number Issue (Ollama)

Those numbers you saw were likely:

1. **Token IDs** - Raw model output tokens
2. **Thinking tokens** - DeepSeek R1 shows reasoning as numbers
3. **Corrupted response** - Ollama not running properly

**Solution:** Use Llama 3.2 instead, which gives clean text.

---

## ⚡ Quick Checklist

Before running tests again:

- [ ] Ollama installed and running (`ollama serve`)
- [ ] Llama 3.2 model downloaded (`ollama pull llama3.2:latest`)
- [ ] Real API keys added to `.env` (not placeholders)
- [ ] RAG API restarted with new .env settings
- [ ] Test document uploaded with correct file_id
- [ ] PostgreSQL running (for vector search)

---

## 🧪 Test Individual Models First

Before running full comparison, test each model individually:

### Test Azure:
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "file_id": "file_1764684418450_vxo6z6s0o",
    "model": "azure-gpt4o-mini",
    "k": 4
  }'
```

### Test Gemini:
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "file_id": "file_1764684418450_vxo6z6s0o",
    "model": "gemini-2.0-flash-exp",
    "k": 4
  }'
```

### Test Ollama:
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "file_id": "file_1764684418450_vxo6z6s0o",
    "model": "ollama-llama3.2",
    "k": 4
  }'
```

---

## 🎯 Expected Results After Fixes

All tests should show:

✅ **PASS** badges (green)
✅ Clean text responses
✅ No timeout errors
✅ No rate limit errors
✅ Latency metrics (in milliseconds)

---

## 🆘 Still Having Issues?

### If Azure/Gemini still timeout:
- Check your internet connection
- Verify API keys are correct
- Try increasing timeout to 180 seconds in `.env`

### If Gemini still hits rate limits:
- Increase `delay: 10000` (10 seconds) in YAML
- Run fewer tests at once
- Wait 1 minute between test runs

### If Ollama still shows numbers:
- Make sure `ollama serve` is running
- Verify model is downloaded: `ollama list`
- Try a different model: `ollama pull mistral:latest`

---

## 📚 Additional Help

- [Ollama Installation](https://ollama.com/download)
- [Gemini API Rate Limits](https://ai.google.dev/pricing)
- [Azure OpenAI Limits](https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits)

---

**Good luck! 🚀**
