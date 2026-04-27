# Contributing

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Adding a chunking strategy

1. Add function to `chunkers.py`
2. Wire into `rag_engine.py`
3. Add a test
