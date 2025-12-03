"""
Promptfoo HTTP provider for the /chat-metrics endpoint.
Returns token usage and cost information for model comparison.

Environment variables supported:
- PROMPTFOO_RAG_BASE_URL (default http://127.0.0.1:8000)
- PROMPTFOO_RAG_JWT (optional bearer token)
- PROMPTFOO_RAG_FILE_ID (default testid1)
- PROMPTFOO_RAG_ENTITY_ID (default promptfoo-tester)
- PROMPTFOO_RAG_K (default 4)
- PROMPTFOO_RAG_TIMEOUT (default 180)
"""

from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict

# Defaults
DEFAULT_BASE_URL = os.getenv("PROMPTFOO_RAG_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_FILE_ID = os.getenv("PROMPTFOO_RAG_FILE_ID", "file_1764752210133_5sjhkobm3")
DEFAULT_ENTITY_ID = os.getenv("PROMPTFOO_RAG_ENTITY_ID", "test1")
DEFAULT_K = int(os.getenv("PROMPTFOO_RAG_K", "4"))
DEFAULT_TIMEOUT = float(os.getenv("PROMPTFOO_RAG_TIMEOUT", "180"))
JWT_TOKEN = os.getenv("PROMPTFOO_RAG_JWT")


def _build_payload(prompt: str, config: Dict[str, Any], context: Dict[str, Any]):
    vars_ctx = (context or {}).get("vars", {})
    payload = {
        "query": prompt,
        "file_id": vars_ctx.get("file_id") or config.get("defaultFileId") or DEFAULT_FILE_ID,
        "entity_id": vars_ctx.get("entity_id") or config.get("defaultEntityId") or DEFAULT_ENTITY_ID,
        "k": vars_ctx.get("k") or config.get("defaultK") or DEFAULT_K,
        "model": vars_ctx.get("model") or config.get("defaultModel") or "gemini",
        "temperature": vars_ctx.get("temperature") or config.get("defaultTemperature") or 0.7,
    }
    body_extras = config.get("bodyExtras")
    if isinstance(body_extras, dict):
        payload.update(body_extras)
    return payload


def _format_output(parsed: Any) -> str:
    """
    Format chat response with metrics - show answer and usage stats.
    """
    if parsed is None:
        return "(empty response)"

    if isinstance(parsed, str):
        return parsed

    if isinstance(parsed, dict):
        answer = parsed.get("answer", "(no answer)")
        model_used = parsed.get("model_used", "unknown")
        usage = parsed.get("usage", {})
        cost = parsed.get("estimated_cost", 0.0)

        output_lines = [
            f"Answer: {answer}",
            "",
            f"Model: {model_used}",
            f"Tokens: {usage.get('total_tokens', 0)} (prompt: {usage.get('prompt_tokens', 0)}, completion: {usage.get('completion_tokens', 0)})",
            f"Estimated Cost: ${cost:.6f} USD"
        ]
        return "\n".join(output_lines)

    return json.dumps(parsed, indent=2)


def call_api(prompt: str, options: Dict[str, Any] | None = None,
             context: Dict[str, Any] | None = None):

    options = options or {}
    config = options.get("config", {})

    base_url = config.get("baseUrl", DEFAULT_BASE_URL).rstrip("/")
    endpoint = config.get("endpoint", "/chat-metrics")
    method = config.get("method", "POST").upper()
    url = f"{base_url}{endpoint}"

    payload = _build_payload(prompt, config, context or {})
    data = json.dumps(payload).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if config.get("includeAuth", True) and JWT_TOKEN:
        headers["Authorization"] = f"Bearer {JWT_TOKEN}"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            raw_body = response.read().decode("utf-8")

            try:
                parsed_json = json.loads(raw_body)
            except json.JSONDecodeError:
                parsed_json = raw_body

            # Format for UI display
            formatted_output = _format_output(parsed_json)

            return {
                "output": formatted_output,  # Shown in Promptfoo UI
                "raw": parsed_json,          # Used for assertions (includes usage/cost)
                "cost": parsed_json.get("estimated_cost", 0.0) if isinstance(parsed_json, dict) else 0.0,
                "tokenUsage": parsed_json.get("usage", {}) if isinstance(parsed_json, dict) else {}
            }

    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="ignore")
        return {"output": f"HTTP {err.code}: {body}", "raw": None, "cost": 0.0, "tokenUsage": {}}

    except Exception as exc:
        return {"output": f"Error: {str(exc)}", "raw": None, "cost": 0.0, "tokenUsage": {}}
