# DocuMind — RAG Knowledge Base 📚

Chat with your documents using AI. Upload PDFs, text files, or paste content — then ask questions and get accurate answers with source citations. Built using the RAG (Retrieval-Augmented Generation) pattern.

This is the most common architecture used in real-world AI applications at companies like Google, Microsoft, and OpenAI.

## Features

- **Upload documents** (PDF, TXT, or paste text directly)
- **Smart chunking** — splits documents into overlapping chunks for better retrieval
- **Semantic search** — finds the most relevant chunks for your question
- **AI answers with citations** — tells you exactly which document each fact came from
- **Conversation memory** — follow-up questions understand context
- **Source viewer** — click citations to see the original text
- Clean chat interface with dark theme

## Getting Started

```bash
git clone https://github.com/YOUR_USERNAME/documind-rag.git
cd documind-rag

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Add your Gemini API key
echo GEMINI_API_KEY=your_key_here > .env

python app.py
```

Open `http://localhost:8000`. Upload some documents and start asking questions.

## How RAG Works

```
Document Upload → Chunking → Embedding → Vector Store
                                              ↓
User Question → Embed Query → Find Similar Chunks → Send to LLM → Answer + Citations
```

1. **Ingestion** — Documents are split into chunks (~500 chars with overlap)
2. **Embedding** — Each chunk is converted to a vector using Sentence Transformers
3. **Storage** — Vectors stored in ChromaDB for fast retrieval
4. **Retrieval** — When you ask a question, the most similar chunks are found
5. **Generation** — Retrieved chunks + your question are sent to Gemini to generate an answer with citations

## Tech Stack

- **LLM:** Google Gemini API
- **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector DB:** ChromaDB
- **Backend:** Python, FastAPI
- **PDF Parsing:** PyMuPDF
- **Frontend:** HTML, CSS, JavaScript

## Project Structure

```
documind-rag/
├── app.py              # FastAPI server
├── rag_engine.py       # RAG pipeline (chunking, retrieval, generation)
├── requirements.txt
├── .env.example
├── static/
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── README.md
```

## License

MIT
