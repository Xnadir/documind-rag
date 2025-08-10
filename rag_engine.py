"""
RAG Engine — handles document chunking, embedding, retrieval, and AI answer generation.
This is the core of the RAG (Retrieval-Augmented Generation) pipeline.
"""

import os
import json
import hashlib
import fitz  # PyMuPDF
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_model = None
_collection = None
_chroma = None

EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def _init():
    global _model, _collection, _chroma
    if _model is not None:
        return
    print("Loading embedding model...")
    _model = SentenceTransformer(EMBED_MODEL)
    _chroma = chromadb.PersistentClient(path="./rag_db")
    _collection = _chroma.get_or_create_collection("rag_docs", metadata={"hnsw:space": "cosine"})
    print(f"Ready. {_collection.count()} chunks indexed.")


# --- Document Processing ---

def parse_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(page.get_text("text") for page in doc)
    doc.close()
    return text.strip()


def chunk_text(text: str, source: str = "") -> list[dict]:
    """Split text into overlapping chunks with metadata."""
    chunks = []
    start = 0
    idx = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunk_id = hashlib.md5(f"{source}_{idx}".encode()).hexdigest()[:12]
            chunks.append({
                "id": chunk_id,
                "text": chunk,
                "source": source,
                "chunk_index": idx,
            })
            idx += 1

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def ingest_document(text: str, source_name: str) -> int:
    """Chunk, embed, and store a document. Returns number of chunks created."""
    _init()

    chunks = chunk_text(text, source_name)
    if not chunks:
        return 0

    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    embeddings = _model.encode(texts).tolist()
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    _collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return len(chunks)


# --- Retrieval ---

def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """Find the most relevant chunks for a query."""
    _init()

    if _collection.count() == 0:
        return []

    query_vec = _model.encode(query).tolist()
    results = _collection.query(
        query_embeddings=[query_vec],
        n_results=min(top_k, _collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i].get("source", ""),
            "score": round((1 - results["distances"][0][i]) * 100, 1),
        })
    return chunks


# --- Generation ---

def generate_answer(query: str, chat_history: list[dict] = None) -> dict:
    """Retrieve relevant chunks and generate an answer with citations."""
    chunks = retrieve(query, top_k=4)

    if not chunks:
        return {
            "answer": "I don't have any documents to search through yet. Please upload some documents first.",
            "sources": [],
        }

    # build context from retrieved chunks
    context_parts = []
    for i, c in enumerate(chunks):
        context_parts.append(f"[Source {i+1}: {c['source']}]\n{c['text']}")
    context = "\n\n".join(context_parts)

    # build conversation history
    history_text = ""
    if chat_history:
        for msg in chat_history[-6:]:  # last 6 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided document excerpts. If the answer is not in the documents, say so.

Always cite your sources using [Source N] notation.

DOCUMENT EXCERPTS:
{context}

{f"CONVERSATION HISTORY:{chr(10)}{history_text}" if history_text else ""}

USER QUESTION: {query}

Provide a clear, well-structured answer with citations. Use markdown for formatting."""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt, generation_config=genai.GenerationConfig(temperature=0.2, max_output_tokens=2048))

    return {
        "answer": response.text,
        "sources": [{"text": c["text"][:200], "source": c["source"], "score": c["score"]} for c in chunks],
    }


def get_stats():
    _init()
    return {"total_chunks": _collection.count()}
