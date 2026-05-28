"""Centralized AI service implementation."""

import httpx
import json
import logging
from typing import Any, Dict, List, Optional, AsyncGenerator

logger = logging.getLogger(__name__)

# This would ideally come from settings, but we use the service name 'assistant' for docker
ASSISTANT_URL = "http://assistant:8500/assistant/stream"

def extract_text_content(content: Any) -> str:
    """Extract plain text from LLM response content (handles lists, dicts, thoughts)."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return str(content.get("content") or "").strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
        return "\n".join(parts).strip()
    return ""

async def complete_chat(
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    max_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    """Non-streaming chat completion via Assistant service."""
    # For simplicity, we just use the streaming endpoint and collect the results
    full_content = ""
    async for chunk in stream_chat(messages, tools=tools, max_tokens=max_tokens):
        if chunk.get("type") == "chunk":
            full_content += chunk.get("content", "")
    
    return {"role": "assistant", "content": full_content}

async def stream_chat(
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    max_tokens: Optional[int] = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Streaming chat completion via Assistant service."""
    # This proxies the request to the dedicated Assistant container
    last_user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    
    payload = {
        "message": last_user_message,
        # We don't have full session info here yet, but the Assistant handles its own auth/session if needed
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", ASSISTANT_URL, json=payload) as response:
                if response.status_code != 200:
                    yield {"type": "error", "content": f"Assistant error: {response.status_code}"}
                    return

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    
                    data_str = line[6:].strip()
                    if not data_str:
                        continue
                    
                    try:
                        data = json.loads(data_str)
                        # Map Assistant SSE events to what the centralized_ai router expects
                        event_type = "chunk" # Default
                        yield {"type": event_type, "content": data.get("content", "")}
                    except Exception as e:
                        logger.error(f"Error parsing SSE chunk: {e}")

    except Exception as e:
        logger.error(f"Assistant connection error: {e}")
        yield {"type": "error", "content": f"Connection error: {str(e)}"}
