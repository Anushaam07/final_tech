# Token Usage & Cost Tracking Implementation

## Overview

This implementation adds comprehensive token usage and cost tracking to the RAG application's model comparison features. It resolves the issue where Promptfoo model comparison tests couldn't detect token counts or costs.

## What Was Implemented

### 1. **New Response Model** (`app/models.py`)

```python
class ChatResponseWithMetrics(BaseModel):
    """Chat response with token usage and cost metrics"""
    answer: str
    model_used: str
    usage: Optional[dict] = None  # {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int}
    estimated_cost: Optional[float] = None  # USD
```

### 2. **New API Endpoint** (`/chat-metrics`)

**Location:** `app/routes/chat_routes.py:1915`

**Purpose:** Returns chat responses with full token usage and cost metrics

**Request:**
```json
{
  "query": "What are the main topics?",
  "file_id": "file_12345",
  "entity_id": "test1",
  "model": "azure-gpt4o-mini",
  "k": 4,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "answer": "The main topics are...",
  "model_used": "Azure GPT-4o-mini",
  "usage": {
    "prompt_tokens": 450,
    "completion_tokens": 120,
    "total_tokens": 570
  },
  "estimated_cost": 0.000139
}
```

### 3. **Cost Calculation** (`app/routes/chat_routes.py:1801`)

**Current Pricing (2025):**
- **Azure GPT-4o-mini:** $0.15/1M input tokens, $0.60/1M output tokens
- **Gemini 2.0/2.5 Flash:** Free (RPM limited)
- **Ollama (local):** Free

**Formula:**
```python
cost = (prompt_tokens × input_price) + (completion_tokens × output_price)
```

### 4. **Token Extraction Functions**

Three provider-specific functions extract usage data:

- `generate_azure_response_with_metrics()` - Extracts from `response.usage`
- `generate_gemini_response_with_metrics()` - Extracts from `response.usage_metadata`
- `generate_ollama_response_with_metrics()` - Extracts from `response.prompt_eval_count` and `response.eval_count`

### 5. **New Promptfoo Provider** (`promptfoo/providers/chat_metrics_target.py`)

Custom provider that:
- Calls `/chat-metrics` endpoint
- Returns structured data with `cost` and `tokenUsage` fields
- Formats output for human-readable Promptfoo UI

**Usage in Config:**
```yaml
providers:
  - id: file://promptfoo/providers/chat_metrics_target.py
    label: "Azure GPT-4o-mini"
    config:
      endpoint: /chat-metrics
      defaultModel: azure-gpt4o-mini
```

### 6. **Updated Model Comparison Tests** (`promptfoo.model-comparison.yaml`)

**New Test Categories:**

#### Token Count Validation
```yaml
- name: "[Tokens] Simple query token count"
  assertions:
    - type: javascript
      value: |
        const usage = context.vars.tokenUsage || output?.tokenUsage;
        return usage.total_tokens < 1000 && usage.total_tokens > 0;
```

#### Token Breakdown Accuracy
```yaml
- name: "[Tokens] Detailed breakdown available"
  assertions:
    - type: javascript
      value: |
        return usage.total_tokens === (usage.prompt_tokens + usage.completion_tokens);
```

#### Cost Verification per Model
```yaml
- name: "[Cost] Azure has cost (paid model)"
  assertions:
    - type: javascript
      value: |
        const cost = context.vars.cost || output?.cost;
        return cost && cost > 0;  // Azure should cost money

- name: "[Cost] Gemini is free"
  assertions:
    - type: javascript
      value: |
        return cost === 0;  // Gemini is free
```

## Usage

### Starting the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Testing the New Endpoint Directly

```bash
curl -X POST "http://localhost:8000/chat-metrics" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize this document",
    "file_id": "file_1764753989277_bju6rhwkt",
    "entity_id": "test2",
    "model": "azure-gpt4o-mini",
    "k": 4,
    "temperature": 0.7
  }'
```

**Expected Response:**
```json
{
  "answer": "This document discusses...",
  "model_used": "Azure GPT-4o-mini",
  "usage": {
    "prompt_tokens": 523,
    "completion_tokens": 87,
    "total_tokens": 610
  },
  "estimated_cost": 0.000131
}
```

### Running Model Comparison Tests

```bash
# Run the updated model comparison
npm run test:models

# Or directly
npx promptfoo@latest eval --config promptfoo.model-comparison.yaml
```

### Viewing Results

```bash
# View latest results
npm run view:latest

# Or
npx promptfoo@latest view
```

## Cost Analysis Example

Given a query with 500 prompt tokens and 100 completion tokens:

| Model | Prompt Cost | Completion Cost | Total Cost |
|-------|-------------|-----------------|------------|
| **Azure GPT-4o-mini** | $0.000075 | $0.000060 | **$0.000135** |
| **Gemini 2.0 Flash** | $0.00 | $0.00 | **$0.00** (free) |
| **Ollama DeepSeek R1** | $0.00 | $0.00 | **$0.00** (local) |

**Monthly Cost Estimate (1M tokens/month):**
- Azure: ~$200/month
- Gemini: $0 (free tier)
- Ollama: $0 (infrastructure costs only)

## Test Output Example

When running `npm run test:models`, you'll now see:

```
✓ [Tokens] Simple query token count
  Azure GPT-4o-mini: 458 tokens ✓
  Gemini 2.0 Flash: 512 tokens ✓
  Ollama DeepSeek R1: 1,234 tokens ✓

✓ [Cost] Azure has cost (paid model)
  Cost: $0.000132 ✓

✓ [Cost] Gemini is free
  Cost: $0.000000 ✓

✓ [Cost] Ollama is free (local)
  Cost: $0.000000 ✓
```

## Troubleshooting

### "usage is undefined"

**Cause:** Old `/chat` endpoint doesn't return metrics.

**Solution:** Ensure config uses `/chat-metrics`:
```yaml
config:
  endpoint: /chat-metrics  # Not /chat
```

### "cost is null"

**Cause:** Model name not matching pricing dictionary.

**Solution:** Check `calculate_cost()` function (chat_routes.py:1801) includes your model.

### Gemini usage showing 0 tokens

**Cause:** Gemini API not returning usage metadata.

**Solution:** Ensure you're using the latest `google-generativeai` library:
```bash
pip install --upgrade google-generativeai
```

### Ollama usage showing 0 tokens

**Cause:** Ollama response format varies by version.

**Solution:** Check Ollama response structure and update `generate_ollama_response_with_metrics()` accordingly.

## Benefits

### 1. **Cost Optimization**
- See exact costs per query
- Compare Azure vs. free alternatives
- Project monthly expenses

### 2. **Performance Insights**
- Identify token-heavy queries
- Optimize prompt engineering
- Reduce unnecessary context

### 3. **Model Selection**
- Data-driven comparison
- Cost vs. quality tradeoffs
- Latency vs. token usage analysis

### 4. **Budget Tracking**
- Real-time cost monitoring
- Usage forecasting
- Department chargebacks

## API Documentation

Access the interactive API docs at:
```
http://localhost:8000/docs
```

Look for the `/chat-metrics` endpoint with the `ChatResponseWithMetrics` response model.

## Future Enhancements

- [ ] Add cumulative cost tracking (store in database)
- [ ] Real-time cost dashboard
- [ ] Budget alerts when exceeding thresholds
- [ ] Per-user cost attribution
- [ ] Historical cost trends
- [ ] Token caching metrics
- [ ] Add more model pricing (GPT-4, Claude, etc.)

## Files Modified

1. `app/models.py` - Added `ChatResponseWithMetrics` model
2. `app/routes/chat_routes.py` - Added `/chat-metrics` endpoint and helper functions
3. `promptfoo/providers/chat_metrics_target.py` - New provider (created)
4. `promptfoo.model-comparison.yaml` - Updated with cost/token assertions

## Related Documentation

- [Promptfoo Model Comparison Guide](./promptfoo/README.md)
- [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)
- [Google Gemini Pricing](https://ai.google.dev/pricing)
