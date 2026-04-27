from typing import Any, List

import chromadb
from chromadb.api.models.Collection import Collection

from app.models.embedded_chunk import EmbeddedChunk
from app.services.embedding_service import generate_embedding


DEFAULT_CHROMA_PATH = "chroma_db"
DEFAULT_COLLECTION_NAME = "log_chunks"


def get_chroma_collection(
    chroma_path: str = DEFAULT_CHROMA_PATH,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> Collection:
    client = chromadb.PersistentClient(path=chroma_path)
    return client.get_or_create_collection(name=collection_name)


def store_embedded_chunks(
    chunks: List[EmbeddedChunk],
    chroma_path: str = DEFAULT_CHROMA_PATH,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> None:
    if not chunks:
        return

    collection = get_chroma_collection(
        chroma_path=chroma_path,
        collection_name=collection_name,
    )

    ids = [chunk.chunk_id for chunk in chunks]
    documents = [chunk.combined_text for chunk in chunks]
    embeddings = [chunk.embedding for chunk in chunks]
    metadatas = [
        {
            "start_time": chunk.start_time or "",
            "end_time": chunk.end_time or "",
            "services": ", ".join(chunk.services),
            "levels": ", ".join(chunk.levels),
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query_similar_chunks(
    query_text: str,
    n_results: int = 3,
    chroma_path: str = DEFAULT_CHROMA_PATH,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> dict[str, Any]:
    collection = get_chroma_collection(
        chroma_path=chroma_path,
        collection_name=collection_name,
    )
    query_embedding = generate_embedding(query_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    return results