"""Tests for the RAG engine."""

import pytest


def test_placeholder():
    """Placeholder test — real tests need a test ChromaDB instance."""
    assert True


def test_chunk_size_config():
    """Verify chunking config loads defaults."""
    from config import CHUNK_SIZE, CHUNK_OVERLAP
    assert CHUNK_SIZE > 0
    assert CHUNK_OVERLAP >= 0
    assert CHUNK_OVERLAP < CHUNK_SIZE
