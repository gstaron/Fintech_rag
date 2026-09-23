"""Minimal flat (brute-force) vector store.

Good enough for a handful of fintech documents and a weekend project. A
real deployment would swap this for pgvector / Azure AI Search / a managed
vector DB once you need horizontal scale, metadata filtering, or well
beyond a few thousand chunks -- see docs/ARCHITECTURE.md for the trade-off
discussion (this is a deliberate, documented simplification, not an
oversight).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    chunk_index: int


class VectorStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.vectors: np.ndarray | None = None

    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        self.chunks.extend(chunks)
        self.vectors = vectors if self.vectors is None else np.vstack([self.vectors, vectors])

    def search(self, query_vector: np.ndarray, top_k: int = 4) -> list[tuple[Chunk, float]]:
        if self.vectors is None or len(self.chunks) == 0:
            return []
        sims = self.vectors @ query_vector
        top_idx = np.argsort(-sims)[:top_k]
        return [(self.chunks[i], float(sims[i])) for i in top_idx]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "chunks": [asdict(c) for c in self.chunks],
            "vectors": self.vectors.tolist() if self.vectors is not None else [],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "VectorStore":
        store = cls()
        if not path.exists():
            return store
        payload = json.loads(path.read_text(encoding="utf-8"))
        store.chunks = [Chunk(**c) for c in payload["chunks"]]
        store.vectors = np.array(payload["vectors"], dtype=np.float32) if payload["vectors"] else None
        return store
