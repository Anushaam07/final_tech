# 🔄 Model Comparison Setup Guide

This guide will help you set up and run model comparison between **Azure GPT-4o-mini**, **Gemini 2.0 Flash (Free)**, and **Ollama DeepSeek R1 (Local)**.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step-by-Step Configuration](#step-by-step-configuration)
3. [Running Model Comparison](#running-model-comparison)
4. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11+
- ✅ Node.js 18+ (for Promptfoo)
- ✅ PostgreSQL with pgvector extension running
- ✅ RAG API server running on `http://127.0.0.1:8000`

---

## 🔧 Step-by-Step Configuration

### Step 1: Get API Keys

#### 1.1 Azure OpenAI (GPT-4o-mini) - PAID
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to your Azure OpenAI resource
3. Under "Keys and Endpoint", copy:
   - **Key** (either Key 1 or Key 2)
   - **Endpoint URL**

#### 1.2 Google Gemini (Free) - FREE
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Get API Key"** or **"Create API Key"**
3. Copy your API key

**Note:** Gemini offers free tier with generous limits:
- ✅ 15 requests per minute
- ✅ 1 million tokens per minute
- ✅ 1,500 requests per day
- ✅ **No credit card required!**

#### 1.3 Ollama (Local/Free) - FREE

1. **Install Ollama:**
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.com/install.sh | sh

   # Windows
   # Download from https://ollama.com/download
   ```

2. **Pull DeepSeek R1 model:**
   ```bash
   ollama pull deepseek-r1:latest
   ```

3. **Start Ollama server:**
   ```bash
   ollama serve
   ```

   This will run on `http://localhost:11434` by default.

4. **Verify it's working:**
   ```bash
   ollama list  # Should show deepseek-r1:latest
   ```

---

### Step 2: Configure .env File

Open `/home/user/final_tech/.env` and update these values:

```bash
# =============================================================================
# CHAT MODELS CONFIGURATION
# =============================================================================

# 1. Azure OpenAI (REQUIRED for Azure comparison)
AZURE_CHAT_ENDPOINT=https://ai-40mini.cognitiveservices.azure.com/
AZURE_CHAT_API_KEY=YOUR_AZURE_KEY_HERE

# Also update embeddings if using Azure
RAG_AZURE_OPENAI_API_KEY=YOUR_AZURE_KEY_HERE
RAG_AZURE_OPENAI_ENDPOINT=https://ai-40mini.cognitiveservices.azure.com/
RAG_AZURE_OPENAI_API_VERSION=2024-02-01

# 2. Google Gemini (REQUIRED for Gemini comparison)
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

# 3. Ollama (REQUIRED for Ollama comparison)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:latest

# =============================================================================
# PROMPTFOO TESTING CONFIGURATION
# =============================================================================

# Make sure your API is accessible
PROMPTFOO_RAG_BASE_URL=http://127.0.0.1:8000
PROMPTFOO_RAG_FILE_ID=file_1764684418450_vxo6z6s0o
PROMPTFOO_RAG_ENTITY_ID=test1

# Optional: OpenAI key for LLM-graded assertions
OPENAI_API_KEY=sk-your-openai-key-for-testing
```

**Important Notes:**
- Replace `YOUR_AZURE_KEY_HERE` with your actual Azure API key
- Replace `YOUR_GEMINI_API_KEY_HERE` with your actual Gemini API key
- Keep `OLLAMA_HOST=http://localhost:11434` if Ollama is running locally
- The file ID must match a document you've uploaded to your RAG system

---

### Step 3: Prepare Your RAG System

1. **Start your RAG API:**
   ```bash
   cd /home/user/final_tech
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Upload a test document** (via UI at http://localhost:8000 or API):
   ```bash
   # Example using curl
   curl -X POST "http://127.0.0.1:8000/add-document" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_test_document.pdf" \
     -F "file_id=file_1764684418450_vxo6z6s0o" \
     -F "entity_id=test1"
   ```

3. **Verify document is indexed:**
   ```bash
   curl "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "test query",
       "file_id": "file_1764684418450_vxo6z6s0o",
       "k": 4
     }'
   ```

---

## 🚀 Running Model Comparison

### Option 1: Run Comparison (Recommended)

```bash
cd /home/user/final_tech
npx promptfoo@latest eval -c promptfoo.model-comparison.yaml
```

This will:
- ✅ Test all 3 models (Azure, Gemini, Ollama)
- ✅ Run comprehensive tests (quality, performance, safety, etc.)
- ✅ Generate side-by-side comparison results

### Option 2: View Results in UI

```bash
npx promptfoo@latest view
```

This opens an interactive web UI at `http://localhost:15500` where you can:
- 📊 Compare responses side-by-side
- 📈 View performance metrics
- ✅ See test pass/fail status
- 💰 Compare costs (if applicable)

### Option 3: Generate HTML Report

```bash
npx promptfoo@latest eval -c promptfoo.model-comparison.yaml --output promptfoo-output/model-comparison.html
```

Open `promptfoo-output/model-comparison.html` in your browser.

---

## 🧪 What Gets Tested

The comparison tests 6 dimensions across all models:

### 1. **Quality**
- Factual accuracy
- Completeness of answers
- Conciseness

### 2. **Performance**
- Response latency (simple queries)
- Response latency (complex queries)

### 3. **Safety**
- Harmful content refusal
- PII protection
- Jailbreak resistance

### 4. **Style**
- Professional tone
- Uncertainty handling
- Toxic input handling

### 5. **Capabilities**
- Multi-step reasoning
- Contextual understanding
- Instruction following

### 6. **Cost & Efficiency**
- Token usage
- Cost per query (where applicable)

---

## 🔍 Expected Results

### Azure GPT-4o-mini
- ✅ High quality responses
- ✅ Fast performance
- ✅ Strong safety
- ❌ Costs money per API call

### Gemini 2.0 Flash (Free)
- ✅ Good quality responses
- ✅ Fast performance
- ✅ Good safety
- ✅ **FREE** (with rate limits)

### Ollama DeepSeek R1 (Local)
- ✅ Decent quality
- ⚠️ Slower (runs on your machine)
- ✅ **FREE** and **PRIVATE**
- ✅ No internet required after download

---

## 🛠 Troubleshooting

### Issue: "Azure OpenAI error"

**Solution:**
1. Verify `AZURE_CHAT_API_KEY` is correct in `.env`
2. Check `AZURE_CHAT_ENDPOINT` matches your Azure resource
3. Ensure your Azure deployment name is `gpt-4o-mini`

```bash
# Test Azure connectivity
curl https://ai-40mini.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-12-01-preview \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_KEY" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

---

### Issue: "Gemini API error"

**Solution:**
1. Verify `GEMINI_API_KEY` is correct in `.env`
2. Check you haven't exceeded free tier limits (15 RPM)
3. Ensure the API key is enabled in Google AI Studio

```bash
# Test Gemini connectivity
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}'
```

---

### Issue: "Ollama error" or "Connection refused"

**Solution:**
1. Verify Ollama is running:
   ```bash
   ollama serve
   ```

2. Check model is downloaded:
   ```bash
   ollama list
   # Should show: deepseek-r1:latest
   ```

3. Test Ollama:
   ```bash
   ollama run deepseek-r1:latest "Hello, test"
   ```

4. Verify host in `.env`:
   ```bash
   OLLAMA_HOST=http://localhost:11434
   ```

---

### Issue: "File not found" or "No documents retrieved"

**Solution:**
1. Verify the `file_id` in your `.env` matches an uploaded document:
   ```bash
   PROMPTFOO_RAG_FILE_ID=file_1764684418450_vxo6z6s0o
   ```

2. Upload a document with this ID (see Step 3 above)

3. Update `defaultFileId` in `promptfoo.model-comparison.yaml` to match

---

### Issue: Promptfoo can't find the provider

**Solution:**
1. Make sure you're running from the project root:
   ```bash
   cd /home/user/final_tech
   ```

2. Verify the provider file exists:
   ```bash
   ls -la promptfoo/providers/chat_target.py
   ```

3. Check Python is available:
   ```bash
   python3 --version
   ```

---

## 📊 Interpreting Results

After running the comparison, you'll see:

### Pass/Fail Metrics
- ✅ Green: Test passed
- ❌ Red: Test failed
- ⚠️ Yellow: Partial pass

### Performance Metrics
- **Latency**: Lower is better
- **Token count**: Lower is more efficient
- **Cost**: Lower is better (Azure costs money, Gemini/Ollama are free)

### Quality Scores
- **Accuracy**: 0.0 - 1.0 (higher is better)
- **Completeness**: 0.0 - 1.0 (higher is better)
- **Safety**: Pass/Fail (fail = security risk)

---

## 🎯 Next Steps

1. **Review Results**: Open the HTML report or view in Promptfoo UI
2. **Adjust Tests**: Modify `promptfoo.model-comparison.yaml` for your use case
3. **Choose Model**: Select based on cost, quality, and performance needs
4. **Production**: Update your main application to use the selected model

---

## 📚 Additional Resources

- [Promptfoo Documentation](https://promptfoo.dev/docs/intro)
- [Azure OpenAI Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Ollama Documentation](https://github.com/ollama/ollama)

---

## ✅ Quick Checklist

Before running comparison:

- [ ] All API keys added to `.env`
- [ ] Ollama running (if testing local model)
- [ ] RAG API running on port 8000
- [ ] Test document uploaded with correct file_id
- [ ] PostgreSQL/pgvector running
- [ ] Node.js installed for Promptfoo

If all checked, run:
```bash
npx promptfoo@latest eval -c promptfoo.model-comparison.yaml
npx promptfoo@latest view
```

---

**Happy Testing! 🚀**
