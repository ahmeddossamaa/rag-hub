"""
Script to ingest HIPAA documents into Weaviate.

Usage:
    uv run python scripts/ingest_docs.py

Place your documents in data/hipaa_docs/
"""

import asyncio
from pathlib import Path

from src.clients.embeddings.gemini import GeminiEmbeddingClient
from src.clients.vector_db.weaviate import WeaviateClient
from src.config import get_settings


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
    return chunks


async def ingest_documents():
    settings = get_settings()
    
    # Initialize clients
    embedding_client = GeminiEmbeddingClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )
    weaviate_client = WeaviateClient(
        url=settings.weaviate_url,
        collection_name=settings.weaviate_collection,
        dimensions=settings.embedding_dimensions,
    )
    
    await weaviate_client.connect()
    
    # Find documents
    docs_dir = Path("data/hipaa_docs")
    if not docs_dir.exists():
        print(f"Directory {docs_dir} not found. Creating it...")
        docs_dir.mkdir(parents=True, exist_ok=True)
        print("Add your HIPAA documents (.txt files) to this directory and run again.")
        return
    
    txt_files = list(docs_dir.glob("*.txt"))
    if not txt_files:
        print("No .txt files found in data/hipaa_docs/")
        print("Add your HIPAA documents and run again.")
        return
    
    # Process each document
    for doc_path in txt_files:
        print(f"Processing {doc_path.name}...")
        text = doc_path.read_text()
        chunks = chunk_text(text)
        
        print(f"  Split into {len(chunks)} chunks")
        
        # Embed chunks
        print("  Generating embeddings...")
        vectors = await embedding_client.embed_batch(chunks)
        
        # Prepare metadata
        metadatas = [
            {"source": doc_path.name, "chunk_index": i}
            for i in range(len(chunks))
        ]
        
        # Insert into Weaviate
        print("  Inserting into Weaviate...")
        await weaviate_client.insert_batch(chunks, vectors, metadatas)
        
        print(f"  Done! Inserted {len(chunks)} chunks.")
    
    await weaviate_client.disconnect()
    print("\nIngestion complete!")


if __name__ == "__main__":
    asyncio.run(ingest_documents())
