# Chunking Strategies

| Strategy   | Best for                       | Config          |
|-----------|--------------------------------|------------------|
| Fixed-size| General text                   | `CHUNK_SIZE=500` |
| Paragraph | Well-structured documents      | —                |
| Sentence  | Conversational content         | `MAX_SENTENCES=5`|

## How it works

1. Text extracted from document
2. Split into chunks
3. Each chunk embedded with sentence transformer
4. Stored in ChromaDB for retrieval
