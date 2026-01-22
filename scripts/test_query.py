"""
Quick script to test the /query endpoint locally.

Usage:
    uv run python scripts/test_query.py "What is PHI under HIPAA?"
"""

import sys

import httpx


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/test_query.py 'your question here'")
        sys.exit(1)
    
    question = sys.argv[1]
    
    response = httpx.post(
        "http://localhost:8000/query",
        json={"question": question},
        timeout=30.0,
    )

    if response.status_code == 200:
        data = response.json()
        print(f"\nQuestion: {question}")
        print(f"\nAnswer: {data['answer']}")
        print("\nSources:")
        for source in data["sources"]:
            print(f"  - {source['source']} (score: {source['score']:.3f})")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    main()
