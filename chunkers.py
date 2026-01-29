"""Document chunking strategies for the RAG pipeline."""
from typing import List

def fixed_size_chunks(text: str, size: int = 500, overlap: int = 50) -> List[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start+size])
        start += size - overlap
    return chunks

def paragraph_chunks(text: str) -> List[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]

def sentence_chunks(text: str, max_sentences: int = 5) -> List[str]:
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [" ".join(sentences[i:i+max_sentences]) for i in range(0, len(sentences), max_sentences) if sentences[i:i+max_sentences]]
