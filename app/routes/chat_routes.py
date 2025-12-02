# # app/routes/chat_routes.py
# import os
# from typing import List
# from fastapi import APIRouter, Request, HTTPException, status
# from openai import AzureOpenAI
# import google.generativeai as genai
# import ollama

# from app.config import logger, vector_store
# from app.models import ChatRequest, ChatResponse, SourceDocument
# from app.services.vector_store.async_pg_vector import AsyncPgVector

# router = APIRouter()


# def get_azure_client():
#     """Initialize Azure OpenAI client for chat completions."""
#     endpoint = os.getenv("AZURE_CHAT_ENDPOINT", "https://ai-40mini.cognitiveservices.azure.com/")
#     api_key = os.getenv("AZURE_CHAT_API_KEY", "")

#     if not api_key:
#         raise ValueError("AZURE_CHAT_API_KEY environment variable not set")

#     return AzureOpenAI(
#         api_version="2024-12-01-preview",
#         azure_endpoint=endpoint,
#         api_key=api_key
#     )


# def get_gemini_client(model_name: str = 'gemini-2.5-flash'):
#     """Initialize Google Gemini client."""
#     api_key = os.getenv("GEMINI_API_KEY", "")

#     if not api_key:
#         raise ValueError("GEMINI_API_KEY environment variable not set")

#     genai.configure(api_key=api_key)
#     return genai.GenerativeModel(model_name)


# def format_sources_for_context(sources: List[tuple]) -> str:
#     """Format retrieved sources into a context string for the LLM."""
#     context_parts = []
#     for idx, (doc, score) in enumerate(sources, 1):
#         context_parts.append(f"[Source {idx}] (Relevance: {score:.3f})\n{doc.page_content}\n")
#     return "\n".join(context_parts)


# def create_rag_prompt(query: str, context: str) -> str:
#     """Create a RAG prompt that instructs the LLM to answer based on context."""
#     return f"""You are a helpful AI assistant that answers questions based on the provided document context.

# IMPORTANT INSTRUCTIONS:
# 1. Answer the question using ONLY the information from the provided sources below
# 2. If the answer cannot be found in the sources, say "I cannot find this information in the provided document"
# 3. Be specific and cite which source number you're using when possible
# 4. If sources contradict each other, mention both perspectives
# 5. Keep your answer concise but complete

# SOURCES:
# {context}

# QUESTION:
# {query}

# ANSWER:"""


# def create_chat_messages(query: str, context: str) -> List[dict]:
#     """Create messages for chat completion API."""
#     system_prompt = """You are a helpful AI assistant specialized in answering questions about documents.
# You must ONLY use the information provided in the sources to answer questions.
# If the information is not in the sources, clearly state that you cannot answer based on the provided documents.
# Be accurate, concise, and always cite your sources when possible."""

#     user_prompt = f"""Based on the following sources from the document, please answer the question.

# SOURCES:
# {context}

# QUESTION: {query}"""

#     return [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": user_prompt}
#     ]


# async def retrieve_relevant_documents(
#     query: str,
#     file_id: str,
#     k: int,
#     request: Request
# ) -> List[tuple]:
#     """Retrieve relevant documents from vector store."""
#     try:
#         # Get embedding for the query
#         embedding = vector_store.embedding_function.embed_query(query)

#         # Search for similar documents
#         if isinstance(vector_store, AsyncPgVector):
#             documents = await vector_store.asimilarity_search_with_score_by_vector(
#                 embedding,
#                 k=k,
#                 filter={"file_id": file_id},
#                 executor=request.app.state.thread_pool,
#             )
#         else:
#             documents = vector_store.similarity_search_with_score_by_vector(
#                 embedding, k=k, filter={"file_id": file_id}
#             )

#         return documents
#     except Exception as e:
#         logger.error(f"Error retrieving documents: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to retrieve documents: {str(e)}"
#         )


# async def generate_azure_response(messages: List[dict], temperature: float) -> str:
#     """Generate response using Azure OpenAI."""
#     try:
#         client = get_azure_client()
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages,
#             temperature=temperature,
#             max_tokens=1000
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         logger.error(f"Azure OpenAI error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Azure OpenAI error: {str(e)}"
#         )


# async def generate_gemini_response(prompt: str, temperature: float, model_name: str = 'gemini-2.5-flash') -> str:
#     """Generate response using Google Gemini - simple and straightforward like Azure."""
#     try:
#         model = get_gemini_client(model_name)

#         generation_config = {
#             "temperature": temperature,
#             "max_output_tokens": 1000,
#         }

#         response = model.generate_content(
#             prompt,
#             generation_config=generation_config
#         )

#         # Simple text extraction with graceful error handling
#         try:
#             return response.text
#         except (ValueError, AttributeError):
#             # Gemini blocked the response - return friendly message
#             return "I apologize, but I cannot generate a response for this query at the moment. Please try rephrasing your question or try a different query."

#     except Exception as e:
#         logger.error(f"Gemini API error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Gemini API error: {str(e)}"
#         )


# async def generate_ollama_response(prompt: str, temperature: float) -> str:
#     """Generate response using Ollama (DeepSeek R1) - local LLM."""
#     try:
#         ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
#         ollama_model = os.getenv("OLLAMA_MODEL", "deepseek-r1:latest")

#         # Create Ollama client with custom host
#         client = ollama.Client(host=ollama_host)

#         # Generate response
#         response = client.generate(
#             model=ollama_model,
#             prompt=prompt,
#             options={
#                 "temperature": temperature,
#                 "num_predict": 1000,  # max tokens
#             }
#         )

#         return response['response']

#     except Exception as e:
#         logger.error(f"Ollama error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Ollama error: {str(e)}"
#         )


# @router.post("/chat", response_model=ChatResponse)
# async def chat_with_documents(request: Request, body: ChatRequest):
#     """
#     Chat endpoint that retrieves relevant documents and generates AI responses.

#     Supports:
#     - Azure OpenAI GPT-4o-mini
#     - Google Gemini
#     """
#     try:
#         # Retrieve relevant documents
#         logger.info(f"Retrieving documents for query: {body.query[:50]}...")
#         documents = await retrieve_relevant_documents(
#             body.query,
#             body.file_id,
#             body.k,
#             request
#         )

#         if not documents:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="No relevant documents found for the query"
#             )

#         # Format context from retrieved documents
#         context = format_sources_for_context(documents)
#         logger.info(f"Retrieved {len(documents)} relevant documents")

#         # Generate response based on selected model
#         if body.model == "azure-gpt4o-mini":
#             messages = create_chat_messages(body.query, context)
#             answer = await generate_azure_response(messages, body.temperature)
#             model_used = "Azure GPT-4o-mini"
#         elif body.model in ["gemini", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
#             # Map generic "gemini" to the default model
#             actual_model = "gemini-2.5-flash" if body.model == "gemini" else body.model
#             prompt = create_rag_prompt(body.query, context)
#             answer = await generate_gemini_response(prompt, body.temperature, actual_model)
#             model_used = f"Google Gemini ({actual_model})"
#         elif body.model in ["ollama", "deepseek-r1", "deepseek-r1:latest"]:
#             prompt = create_rag_prompt(body.query, context)
#             answer = await generate_ollama_response(prompt, body.temperature)
#             ollama_model = os.getenv("OLLAMA_MODEL", "deepseek-r1:latest")
#             model_used = f"Ollama ({ollama_model})"
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Unsupported model: {body.model}"
#             )

#         # Prepare sources for response
#         sources = [
#             SourceDocument(
#                 content=doc.page_content,
#                 score=float(score),
#                 metadata=doc.metadata
#             )
#             for doc, score in documents
#         ]

#         logger.info(f"Generated response using {model_used}")

#         return ChatResponse(
#             answer=answer,
#             sources=sources,
#             model_used=model_used
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error in chat endpoint: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An unexpected error occurred: {str(e)}"
#         )


#################################working------------

# app/routes/chat_routes.py
import os
import re
from typing import List
from fastapi import APIRouter, Request, HTTPException, status
from openai import AzureOpenAI
import google.generativeai as genai
import ollama

from app.config import logger, vector_store
from app.models import ChatRequest, ChatResponse, SourceDocument
from app.services.vector_store.async_pg_vector import AsyncPgVector

router = APIRouter()

# -----------------------
# Moderate secret-blocking (B): allow names/emails but block high-risk secrets
# -----------------------

# Query keywords that should block the request (user asked explicitly for secrets)
SENSITIVE_QUERY_KEYWORDS = [
    "password", "passwd", "passphrase", "ssn", "social security",
    "api key", "secret", "secret key", "access key", "aws access", "aws secret",
    "stripe", "credit card", "card number", "cvv", "private key", "ssh key", "jwt",
    "token"
]

# Regex patterns that indicate secrets in text (will be redacted)
SENSITIVE_PATTERNS = {
    # Common API key prefixes (striped examples). This will match typical key patterns.
    r'\bsk_live_[A-Za-z0-9_\-]{8,}\b': '[REDACTED_API_KEY]',
    r'\bsk_test_[A-Za-z0-9_\-]{8,}\b': '[REDACTED_API_KEY]',
    r'\bsk-[A-Za-z0-9_\-]{8,}\b': '[REDACTED_API_KEY]',
    r'\bAKIA[0-9A-Z]{8,}\b': '[REDACTED_AWS_KEY]',
    r'\bA3T[A-Z0-9]{8,}\b': '[REDACTED_AWS_KEY]',
    # AWS secret-ish (long base64-like)
    r'\b[A-Za-z0-9\/+]{30,}\={0,2}\b': '[REDACTED_POTENTIAL_SECRET]',
    # Generic "secret" forms
    r'(?i)secret[_\-\s]?key[:=]\s*\S+': '[REDACTED_SECRET]',
    r'(?i)api[_\-\s]?key[:=]\s*\S+': '[REDACTED_API_KEY]',
    r'(?i)access[_\-\s]?token[:=]\s*\S+': '[REDACTED_TOKEN]',
    # Private key blocks
    r'-----BEGIN PRIVATE KEY-----[\s\S]+?-----END PRIVATE KEY-----': '[REDACTED_PRIVATE_KEY]',
    r'ssh-rsa\s+[A-Za-z0-9+/=]{50,}': '[REDACTED_SSH_KEY]',
    # Credit cards (very permissive) - redacted
    r'\b(?:\d[ -]*?){13,19}\b': '[REDACTED_CREDIT_CARD]',
    # SSN pattern
    r'\b\d{3}-\d{2}-\d{4}\b': '[REDACTED_SSN]',
    # JWT-like (header.payload.signature)
    r'\beyJ[0-9A-Za-z_\-]+\.[0-9A-Za-z_\-]+\.[0-9A-Za-z_\-]+\b': '[REDACTED_JWT]'
}

# Patterns we should NOT redact under 'moderate' mode:
# - Names and emails are allowed (do NOT include them in SENSITIVE_PATTERNS).
# - We intentionally avoid over-redacting short tokens or normal words.

# Compile regexes for speed
_COMPILED_SENSITIVE_RE = [(re.compile(pat, flags=re.IGNORECASE | re.DOTALL), repl)
                          for pat, repl in SENSITIVE_PATTERNS.items()]


def redact_sensitive_data(text: str) -> str:
    """
    Redact high-risk secrets from text. This is applied:
     - to document context before sending to model (so model doesn't *see* raw secrets)
     - to model outputs before returning to client (so we never leak)
    We preserve emails and normal names (user wanted that).
    """
    if not text:
        return text
    redacted = text
    for cre, repl in _COMPILED_SENSITIVE_RE:
        redacted = cre.sub(repl, redacted)
    return redacted


def contains_sensitive_query(query: str) -> bool:
    """Return True if the user query appears to be requesting secrets explicitly."""
    if not query:
        return False
    qlow = query.lower()
    for kw in SENSITIVE_QUERY_KEYWORDS:
        if kw in qlow:
            return True
    return False


# ----------------------- LLM Clients -----------------------
def get_azure_client():
    endpoint = os.getenv("AZURE_CHAT_ENDPOINT", "https://ai-40mini.cognitiveservices.azure.com/")
    api_key = os.getenv("AZURE_CHAT_API_KEY", "")
    if not api_key:
        raise ValueError("AZURE_CHAT_API_KEY environment variable not set")
    return AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=endpoint,
        api_key=api_key
    )


def get_gemini_client(model_name: str = 'gemini-2.5-flash'):
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


# ----------------------- RAG Prompt & Messages -----------------------
def format_sources_for_context(sources: List[tuple]) -> str:
    """
    Format and redact secrets from retrieved documents. We redact secret patterns
    but keep normal textual content (including emails/names).
    """
    context_parts = []
    for idx, (doc, score) in enumerate(sources, 1):
        # redact secrets in page content
        clean_content = redact_sensitive_data(doc.page_content)
        context_parts.append(f"[Source {idx}] (Relevance: {score:.3f})\n{clean_content}\n")
    return "\n".join(context_parts)


def create_rag_prompt(query: str, context: str) -> str:
    return f"""You are a helpful AI assistant that answers questions based on the provided document context.

INSTRUCTIONS (strict):
1. Use ONLY the information in the provided sources to answer.
2. If the information is NOT present in the sources, reply: "I cannot find this information in the provided document."
3. NEVER output secrets (API keys, passwords, private keys, tokens, credit card numbers, SSNs). If asked for them, refuse:
   "I’m sorry, but I cannot provide confidential information."
4. Cite source numbers when possible.
5. Keep answers concise.

SOURCES:
{context}

QUESTION:
{query}

ANSWER:"""


def create_chat_messages(query: str, context: str) -> List[dict]:
    system_prompt = (
        "You are a secure assistant specialized in answering questions about documents. "
        "Only use the provided sources. Never reveal secrets such as API keys, passwords, "
        "private keys, JWTs, access tokens, credit card numbers, or SSNs. If asked for such data, "
        "respond: \"I’m sorry, but I cannot provide confidential information.\""
    )
    user_prompt = f"SOURCES:\n{context}\nQUESTION: {query}"
    return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]


# ----------------------- Document Retrieval -----------------------
async def retrieve_relevant_documents(query: str, file_id: str, k: int, request: Request) -> List[tuple]:
    try:
        embedding = vector_store.embedding_function.embed_query(query)
        if isinstance(vector_store, AsyncPgVector):
            documents = await vector_store.asimilarity_search_with_score_by_vector(
                embedding,
                k=k,
                filter={"file_id": file_id},
                executor=request.app.state.thread_pool,
            )
        else:
            documents = vector_store.similarity_search_with_score_by_vector(
                embedding, k=k, filter={"file_id": file_id}
            )
        return documents
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


# ----------------------- LLM Response Generation -----------------------
async def generate_azure_response(messages: List[dict], temperature: float) -> str:
    try:
        client = get_azure_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=1000
        )
        # redact any secrets in model output
        return redact_sensitive_data(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Azure OpenAI error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Azure OpenAI error: {str(e)}"
        )


async def generate_gemini_response(prompt: str, temperature: float, model_name: str = 'gemini-2.5-flash') -> str:
    try:
        model = get_gemini_client(model_name)
        generation_config = {"temperature": temperature, "max_output_tokens": 1000}
        response = model.generate_content(prompt, generation_config=generation_config)
        text = getattr(response, "text", None)
        if text is None:
            # defensive fallback
            return "I cannot generate a response for this query at the moment."
        return redact_sensitive_data(text)
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini API error: {str(e)}"
        )


async def generate_ollama_response(prompt: str, temperature: float) -> str:
    try:
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "deepseek-r1:latest")
        client = ollama.Client(host=ollama_host)
        response = client.generate(
            model=ollama_model,
            prompt=prompt,
            options={
                "temperature": temperature,
                "num_predict": 1000,
            }
        )
        # Ollama returns dict with 'response' or similar
        resp_text = response.get("response") if isinstance(response, dict) else str(response)
        return redact_sensitive_data(resp_text)
    except Exception as e:
        logger.error(f"Ollama error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ollama error: {str(e)}"
        )


# ----------------------- Chat Endpoint -----------------------
@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(request: Request, body: ChatRequest):
    try:
        # Block queries that explicitly ask for secrets
        if contains_sensitive_query(body.query):
            raise HTTPException(
                status_code=400,
                detail="This request cannot be completed due to policy restrictions."
            )

        # Retrieve and sanitize documents (secrets redacted from context)
        logger.info(f"Retrieving documents for query: {body.query[:80]}...")
        documents = await retrieve_relevant_documents(body.query, body.file_id, body.k, request)
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant documents found for the query"
            )

        context = format_sources_for_context(documents)
        logger.info(f"Retrieved {len(documents)} relevant documents (sanitized)")

        # Generate response using selected model
        if body.model and body.model.lower().startswith("azure"):
            messages = create_chat_messages(body.query, context)
            answer = await generate_azure_response(messages, body.temperature)
            model_used = "Azure GPT-4o-mini"
        elif body.model and body.model.lower().startswith("gemini"):
            prompt = create_rag_prompt(body.query, context)
            answer = await generate_gemini_response(prompt, body.temperature, body.model)
            model_used = f"Google Gemini ({body.model})"
        elif body.model and body.model.lower().startswith("ollama"):
            prompt = create_rag_prompt(body.query, context)
            answer = await generate_ollama_response(prompt, body.temperature)
            model_used = f"Ollama ({os.getenv('OLLAMA_MODEL', 'deepseek-r1:latest')})"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported model: {body.model}"
            )

        # Sanitize sources returned to client (secrets redacted)
        sources = [
            SourceDocument(
                content=redact_sensitive_data(doc.page_content),
                score=float(score),
                metadata=doc.metadata
            )
            for doc, score in documents
        ]

        logger.info(f"Generated response using {model_used}")
        return ChatResponse(
            answer=answer,
            sources=sources,
            model_used=model_used
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in chat endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
