"""LLM + embedding provider abstraction.

Three backends, selected by LLM_PROVIDER:
- "openai": real OpenAI API.
- "azure_openai": real Azure OpenAI (PwC's own reference architecture).
- "none": offline/dev fallback, zero network calls, so the whole pipeline
  (chunking, retrieval, eval harness, agent loop) can be exercised without
  an API key. Answers are extractive/scripted, not generative -- useful for
  testing plumbing and for CI, but NOT a substitute for real eval numbers.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np

from .config import settings


@dataclass
class ChatResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = ""
    latency_s: float = 0.0


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolChatResult:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = ""
    latency_s: float = 0.0


class LLMProvider(Protocol):
    name: str

    def embed(self, texts: list[str]) -> np.ndarray: ...
    def chat(self, system: str, user: str) -> ChatResult: ...
    def chat_with_tools(self, messages: list[dict], tools: list[dict]) -> ToolChatResult: ...


def _hash_embed(texts: list[str], dim: int = 384) -> np.ndarray:
    """Deterministic bag-of-words hashing embedding -- no model, no network.

    Good enough to rank lexical overlap for the offline demo; not a
    substitute for a real embedding model when reporting eval numbers.
    """
    vectors = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        for token in text.lower().split():
            h = int(hashlib.sha1(token.encode("utf-8")).hexdigest(), 16)
            vectors[i, h % dim] += 1.0
        norm = np.linalg.norm(vectors[i])
        if norm > 0:
            vectors[i] /= norm
    return vectors


class NoLLMProvider:
    """Offline fallback -- no API key required, no network calls."""

    name = "none"

    def embed(self, texts: list[str]) -> np.ndarray:
        return _hash_embed(texts)

    def chat(self, system: str, user: str) -> ChatResult:
        start = time.perf_counter()
        text = (
            "[OFFLINE MODE - LLM_PROVIDER=none] Toto je extraktivna odpoved bez "
            "skutocneho modelu, len na overenie, ze retrieval nasiel spravny "
            "kontext. Nastav LLM_PROVIDER=openai alebo azure_openai + API kluc "
            "pre skutocnu generovanu odpoved a realne eval cisla.\n\n"
            + user[:600]
        )
        return ChatResult(text=text, model="none", latency_s=time.perf_counter() - start)

    def chat_with_tools(self, messages: list[dict], tools: list[dict]) -> ToolChatResult:
        """Deterministic scripted behaviour so the agent loop is testable offline.

        On the first call it calls the first available tool named
        ``rag_search`` (if present) using the latest user message as the
        query; once a tool result is present in the transcript it returns a
        final text answer. This is a stand-in for real tool-calling, not a
        planner.
        """
        start = time.perf_counter()
        has_tool_result = any(m.get("role") == "tool" for m in messages)
        if not has_tool_result:
            rag_tool = next((t for t in tools if t["function"]["name"] == "rag_search"), None)
            if rag_tool:
                last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
                call = ToolCall(id="offline-call-1", name="rag_search", arguments={"query": last_user})
                return ToolChatResult(content="", tool_calls=[call], model="none", latency_s=time.perf_counter() - start)
            return ToolChatResult(
                content="[OFFLINE MODE] Ziadny nastroj na zavolanie, vraciam prazdnu odpoved.",
                model="none",
                latency_s=time.perf_counter() - start,
            )
        tool_text = next((m["content"] for m in reversed(messages) if m["role"] == "tool"), "")
        content = (
            "[OFFLINE MODE - LLM_PROVIDER=none] Zhrnutie vysledku nastroja "
            "(bez skutocneho modelu):\n\n" + tool_text[:500]
        )
        return ToolChatResult(content=content, model="none", latency_s=time.perf_counter() - start)


class OpenAIProvider:
    """Works for both api.openai.com and Azure OpenAI (same SDK, different client ctor)."""

    def __init__(self):
        from openai import AzureOpenAI, OpenAI

        if settings.llm_provider == "azure_openai":
            self.client = AzureOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )
            self.chat_model = settings.azure_openai_chat_deployment
            self.embedding_model = settings.azure_openai_embedding_deployment
            self.name = "azure_openai"
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.chat_model = settings.openai_chat_model
            self.embedding_model = settings.openai_embedding_model
            self.name = "openai"

    def embed(self, texts: list[str]) -> np.ndarray:
        resp = self.client.embeddings.create(model=self.embedding_model, input=texts)
        vecs = np.array([d.embedding for d in resp.data], dtype=np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vecs / norms

    def chat(self, system: str, user: str) -> ChatResult:
        start = time.perf_counter()
        resp = self.client.chat.completions.create(
            model=self.chat_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        latency = time.perf_counter() - start
        choice = resp.choices[0]
        usage = resp.usage
        return ChatResult(
            text=choice.message.content or "",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            model=self.chat_model,
            latency_s=latency,
        )

    def chat_with_tools(self, messages: list[dict], tools: list[dict]) -> ToolChatResult:
        import json

        start = time.perf_counter()
        resp = self.client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        latency = time.perf_counter() - start
        choice = resp.choices[0]
        usage = resp.usage
        tool_calls = [
            ToolCall(id=tc.id, name=tc.function.name, arguments=json.loads(tc.function.arguments or "{}"))
            for tc in (choice.message.tool_calls or [])
        ]
        return ToolChatResult(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            model=self.chat_model,
            latency_s=latency,
        )


def get_provider() -> LLMProvider:
    if settings.llm_provider in ("openai", "azure_openai"):
        return OpenAIProvider()
    return NoLLMProvider()
