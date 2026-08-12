"""Evaluate RAG pipeline quality."""

EVAL_PAIRS = [
    {"question": "What is machine learning?", "expected_keywords": ["subset", "AI", "data", "learn"]},
    {"question": "What are common AI applications?", "expected_keywords": ["NLP", "vision", "recommendation"]},
]

def score_answer(answer: str, expected: list) -> float:
    found = sum(1 for kw in expected if kw.lower() in answer.lower())
    return found / len(expected) if expected else 0.0

if __name__ == "__main__":
    print("RAG Evaluation (requires running server)")
    for pair in EVAL_PAIRS:
        print(f"  Q: {pair['question']}")
