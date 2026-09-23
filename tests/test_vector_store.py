import numpy as np

from fintech_rag.vector_store import Chunk, VectorStore


def test_search_ranks_by_cosine_similarity():
    store = VectorStore()
    chunks = [
        Chunk(id="a", text="dora", source="dora.md", chunk_index=0),
        Chunk(id="b", text="gdpr", source="gdpr.md", chunk_index=0),
    ]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    store.add(chunks, vectors)

    results = store.search(np.array([1.0, 0.0], dtype=np.float32), top_k=2)

    assert results[0][0].id == "a"
    assert results[0][1] > results[1][1]


def test_save_and_load_roundtrip(tmp_path):
    store = VectorStore()
    store.add(
        [Chunk(id="a", text="hello", source="x.md", chunk_index=0)],
        np.array([[0.5, 0.5]], dtype=np.float32),
    )
    path = tmp_path / "index.json"
    store.save(path)

    loaded = VectorStore.load(path)

    assert len(loaded.chunks) == 1
    assert loaded.chunks[0].text == "hello"
    assert loaded.vectors.shape == (1, 2)


def test_load_missing_file_returns_empty_store(tmp_path):
    store = VectorStore.load(tmp_path / "does-not-exist.json")
    assert store.chunks == []
    assert store.search(np.array([1.0]), top_k=3) == []
