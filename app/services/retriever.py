from typing import List

from app.models.retrieval_result import RetrievalResult
from app.services.vector_store import query_similar_chunks


def retrieve_relevant_chunks(
    query_text: str,
    n_results: int = 3,
    chroma_path: str = "chroma_db",
    collection_name: str = "log_chunks",
) -> List[RetrievalResult]:
    raw_results = query_similar_chunks(
        query_text=query_text,
        n_results=n_results,
        chroma_path=chroma_path,
        collection_name=collection_name,
    )

    ids = raw_results.get("ids", [[]])
    documents = raw_results.get("documents", [[]])
    metadatas = raw_results.get("metadatas", [[]])
    distances = raw_results.get("distances", [[]])

    result_count = len(ids[0]) if ids and ids[0] else 0
    results: List[RetrievalResult] = []

    for index in range(result_count):
        result = RetrievalResult(
            chunk_id=ids[0][index],
            document=documents[0][index],
            metadata=metadatas[0][index] if metadatas and metadatas[0] else {},
            distance=distances[0][index] if distances and distances[0] else None,
        )
        results.append(result)

    return results