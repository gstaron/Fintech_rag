"""Ingest fintech documents (data/docs/*.md) into the vector store."""
from __future__ import annotations

from .config import DATA_DIR, INDEX_PATH, settings
from .llm import get_provider
from .vector_store import Chunk, VectorStore


def chunk_text(text: str, source: str, chunk_size: int, overlap: int) -> list[Chunk]:
    """Paragraph-aware chunking with a trailing-character overlap.

    Splits on blank lines first so headings stay attached to their section,
    then packs paragraphs into chunks up to ``chunk_size`` characters,
    carrying the last ``overlap`` characters of a chunk into the next one
    so a fact split across the boundary is still retrievable from either
    side.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[Chunk] = []
    buffer = ""
    idx = 0
    for para in paragraphs:
        if buffer and len(buffer) + len(para) + 2 > chunk_size:
            chunks.append(Chunk(id=f"{source}::{idx}", text=buffer, source=source, chunk_index=idx))
            idx += 1
            tail = buffer[-overlap:] if overlap else ""
            buffer = f"{tail}\n\n{para}".strip()
        else:
            buffer = f"{buffer}\n\n{para}".strip() if buffer else para
    if buffer:
        chunks.append(Chunk(id=f"{source}::{idx}", text=buffer, source=source, chunk_index=idx))
    return chunks


def run_ingest() -> VectorStore:
    provider = get_provider()
    store = VectorStore()
    doc_paths = sorted(DATA_DIR.glob("*.md"))
    if not doc_paths:
        raise FileNotFoundError(f"No .md documents found in {DATA_DIR}")

    all_chunks: list[Chunk] = []
    for path in doc_paths:
        text = path.read_text(encoding="utf-8")
        all_chunks.extend(chunk_text(text, path.name, settings.chunk_size, settings.chunk_overlap))

    vectors = provider.embed([c.text for c in all_chunks])
    store.add(all_chunks, vectors)
    store.save(INDEX_PATH)
    print(
        f"Ingested {len(doc_paths)} documents -> {len(all_chunks)} chunks "
        f"(provider={provider.name}) -> {INDEX_PATH}"
    )
    return store


if __name__ == "__main__":
    run_ingest()
