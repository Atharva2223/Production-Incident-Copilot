from typing import List

from app.models.embedded_chunk import EmbeddedChunk
from app.models.log_chunk import LogChunk
from app.services.embedding_service import generate_embeddings


def embed_chunks(chunks: List[LogChunk]) -> List[EmbeddedChunk]:
    if not chunks:
        return []

    texts = [chunk.combined_text for chunk in chunks]
    embeddings = generate_embeddings(texts)

    embedded_chunks: List[EmbeddedChunk] = []

    for chunk, embedding in zip(chunks, embeddings):
        embedded_chunk = EmbeddedChunk(
            chunk_id=chunk.chunk_id,
            embedding=embedding,
            combined_text=chunk.combined_text,
            start_time=chunk.start_time,
            end_time=chunk.end_time,
            services=chunk.services,
            levels=chunk.levels,
        )
        embedded_chunks.append(embedded_chunk)

    return embedded_chunks