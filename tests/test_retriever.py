from app.models.embedded_chunk import EmbeddedChunk
from app.services.embedding_service import generate_embedding
from app.services.retriever import retrieve_relevant_chunks
from app.services.vector_store import store_embedded_chunks


def test_retrieve_relevant_chunks_returns_structured_results(tmp_path) -> None:
    chroma_path = str(tmp_path / "chroma_test_db")
    collection_name = "test_retriever_chunks"

    chunk_1_text = "PaymentService timeout while acquiring DB connection"
    chunk_2_text = "OrderService created order successfully"

    chunks = [
        EmbeddedChunk(
            chunk_id="chunk_1",
            embedding=generate_embedding(chunk_1_text),
            combined_text=chunk_1_text,
            start_time="2026-04-11 10:01:01",
            end_time="2026-04-11 10:01:50",
            services=["PaymentService"],
            levels=["ERROR"],
        ),
        EmbeddedChunk(
            chunk_id="chunk_2",
            embedding=generate_embedding(chunk_2_text),
            combined_text=chunk_2_text,
            start_time="2026-04-11 10:02:01",
            end_time="2026-04-11 10:02:10",
            services=["OrderService"],
            levels=["INFO"],
        ),
    ]

    store_embedded_chunks(
        chunks=chunks,
        chroma_path=chroma_path,
        collection_name=collection_name,
    )

    results = retrieve_relevant_chunks(
        query_text="database timeout in payment service",
        n_results=2,
        chroma_path=chroma_path,
        collection_name=collection_name,
    )

    assert len(results) >= 1

    top_result = results[0]
    assert top_result.chunk_id == "chunk_1"
    assert "PaymentService timeout" in top_result.document
    assert top_result.metadata["services"] == "PaymentService"