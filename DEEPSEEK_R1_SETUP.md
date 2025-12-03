# 🤖 DeepSeek R1 Setup & Usage Guide

## What is DeepSeek R1?

DeepSeek R1 is a powerful reasoning model that shows its "thinking process" before providing answers. This makes it unique but requires special handling.

---

## 🚀 Installation Steps

### 1. Install Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &
```

### 2. Download DeepSeek R1

```bash
# Pull the model (this will take a few minutes - it's ~40GB)
ollama pull deepseek-r1:latest

# Verify installation
ollama list
# Should show: deepseek-r1:latest

# Test it
ollama run deepseek-r1:latest "What is 2+2?"
```

---

## 🔧 Configuration

Your `.env` is already configured:

```bash
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:latest
```

Your YAML is set to use:

```yaml
defaultModel: ollama-deepseek-r1
```

---

## 🎯 How DeepSeek R1 Works

### Normal Output Format

DeepSeek R1 may output:
```
<think>
Let me analyze this step by step...
First, I need to consider...
Therefore, the answer is...
</think>

The document discusses ACME Corporation's strategic plan...
```

### What We Do

The API automatically:
1. **Detects** `<think>...</think>` tags
2. **Extracts** only the final answer (after `</think>`)
3. **Returns** clean text without thinking tokens

---

## ⚠️ About Those Numbers You Saw

The numbers you saw earlier (like "2610, 525, 264, 10950...") were likely:

1. **Token IDs** - Raw model output before processing
2. **Encoding issues** - Model response not properly decoded
3. **Missing tags** - DeepSeek R1 didn't wrap thinking in tags

### How We Fixed It

Updated `chat_routes.py` line 513-521 to:
- Parse `<think>` tags properly
- Extract clean final answer
- Remove any thinking tokens

---

## 🧪 Testing DeepSeek R1

### Test via API directly:

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
  "answer": "The document discusses ACME Corporation...",
  "sources": [...],
  "model_used": "Ollama (deepseek-r1:latest)"
}
```

**NOT:**
```
2610, 525, 264, 10950, 15235... (numbers)
```

---

## 🏃 Running Model Comparison

Now you can run the full comparison:

```bash
cd /home/user/final_tech

# Make sure Ollama is running
ollama serve &

# Run comparison (this takes ~10-15 minutes with rate limiting)
npx promptfoo@latest eval -c promptfoo.model-comparison.yaml

# View results
npx promptfoo@latest view
```

---

## 📊 What to Expect from DeepSeek R1

### Strengths:
- ✅ **Reasoning**: Excellent at multi-step logic
- ✅ **Free**: Runs locally, no API costs
- ✅ **Privacy**: Your data never leaves your machine
- ✅ **Quality**: Comparable to GPT-4 for reasoning tasks

### Considerations:
- ⏱️ **Slower**: 10-20 seconds per response (CPU dependent)
- 💾 **Large**: 40GB model size
- 🔋 **Resource intensive**: Uses significant RAM/CPU
- 📝 **Verbose**: May produce longer answers (shows reasoning)

---

## 🔍 Troubleshooting

### Issue: Still seeing numbers

**Solution:**
1. Restart your RAG API to load the new code:
   ```bash
   # Stop the API (Ctrl+C)
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Test directly with Ollama:
   ```bash
   ollama run deepseek-r1:latest "Explain AI in one sentence"
   ```

   If this shows numbers, try re-pulling the model:
   ```bash
   ollama rm deepseek-r1:latest
   ollama pull deepseek-r1:latest
   ```

### Issue: Ollama connection refused

**Solution:**
```bash
# Make sure Ollama is running
ps aux | grep ollama

# If not running:
ollama serve &

# Check it's listening:
curl http://localhost:11434/api/tags
```

### Issue: Too slow

**Solution:**
- Use a smaller model: `ollama pull qwen2.5:7b`
- Update `.env`: `OLLAMA_MODEL=qwen2.5:7b`
- Or increase timeout: `PROMPTFOO_RAG_TIMEOUT=180`

---

## 💡 Alternative Models (If DeepSeek R1 is too slow)

```bash
# Smaller, faster alternatives:
ollama pull llama3.2:latest      # 3GB, very fast
ollama pull qwen2.5:7b           # 5GB, fast
ollama pull mistral:latest        # 4GB, balanced

# Update .env to use them:
OLLAMA_MODEL=llama3.2:latest
```

---

## 🎯 Performance Comparison

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| DeepSeek R1 | 40GB | Slow (10-20s) | Excellent | Complex reasoning |
| Llama 3.2 | 3GB | Fast (2-5s) | Good | General Q&A |
| Qwen 2.5 | 5GB | Medium (5-10s) | Very Good | Balanced |
| Mistral | 4GB | Fast (3-7s) | Good | Quick responses |

---

## ✅ Checklist Before Running

- [ ] Ollama installed (`ollama --version`)
- [ ] Ollama running (`ollama serve`)
- [ ] DeepSeek R1 downloaded (`ollama list`)
- [ ] RAG API restarted with new code
- [ ] Test document uploaded
- [ ] API responds correctly (test with curl)

---

## 🔗 Resources

- [DeepSeek R1 Model Card](https://huggingface.co/deepseek-ai/DeepSeek-R1)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [DeepSeek Official Site](https://www.deepseek.com/)

---

**Ready to test! 🚀**

Your setup is now optimized for DeepSeek R1 with proper thinking tag parsing.
