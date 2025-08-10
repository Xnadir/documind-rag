"""
DocuMind — FastAPI server for RAG Knowledge Base
Run with: python app.py
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from rag_engine import ingest_document, generate_answer, get_stats, parse_pdf

app = FastAPI(title="DocuMind RAG")
app.mount("/static", StaticFiles(directory="static"), name="static")


class QuestionInput(BaseModel):
    question: str
    chat_history: list[dict] = []


class TextInput(BaseModel):
    text: str
    source_name: str = "Pasted Text"


@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    source_name: str = Form("")
):
    """Upload a PDF or TXT file to the knowledge base."""
    name = source_name or file.filename

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 20MB)")

    if file.filename.lower().endswith(".pdf"):
        try:
            text = parse_pdf(content)
        except Exception as e:
            raise HTTPException(400, f"Failed to parse PDF: {e}")
    else:
        text = content.decode("utf-8", errors="ignore")

    if not text.strip():
        raise HTTPException(400, "No text could be extracted from the file")

    num_chunks = ingest_document(text, name)
    return {"message": f"Indexed '{name}' — {num_chunks} chunks created", "chunks": num_chunks}


@app.post("/api/add-text")
async def add_text(body: TextInput):
    """Add text content directly to the knowledge base."""
    if not body.text.strip():
        raise HTTPException(400, "Text cannot be empty")
    num_chunks = ingest_document(body.text.strip(), body.source_name)
    return {"message": f"Indexed '{body.source_name}' — {num_chunks} chunks", "chunks": num_chunks}


@app.post("/api/ask")
async def ask_question(body: QuestionInput):
    """Ask a question about the uploaded documents."""
    if not body.question.strip():
        raise HTTPException(400, "Question cannot be empty")
    try:
        result = generate_answer(body.question.strip(), body.chat_history)
        return result
    except Exception as e:
        raise HTTPException(500, f"Failed to generate answer: {str(e)}")


@app.get("/api/stats")
async def stats():
    return get_stats()


if __name__ == "__main__":
    print("\n📚 Starting DocuMind RAG Knowledge Base...")
    print("   Open http://localhost:8000 in your browser\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
