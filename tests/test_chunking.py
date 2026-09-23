from fintech_rag.ingest import chunk_text


def test_short_text_becomes_single_chunk():
    text = "Para one.\n\nPara two."
    chunks = chunk_text(text, source="doc.md", chunk_size=800, overlap=100)
    assert len(chunks) == 1
    assert "Para one." in chunks[0].text
    assert "Para two." in chunks[0].text


def test_long_text_splits_into_multiple_chunks_with_overlap():
    paragraphs = [f"Paragraph number {i} with some filler content to add length." for i in range(20)]
    text = "\n\n".join(paragraphs)

    chunks = chunk_text(text, source="doc.md", chunk_size=200, overlap=50)

    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk.source == "doc.md"
        assert chunk.chunk_index == i
        assert chunk.id == f"doc.md::{i}"

    # overlap: the tail of chunk N should reappear at the start of chunk N+1
    tail_of_first = chunks[0].text[-50:]
    assert any(tail_of_first[-10:] in c.text for c in chunks[1:2])


def test_empty_text_produces_no_chunks():
    assert chunk_text("\n\n   \n\n", source="doc.md", chunk_size=100, overlap=10) == []
