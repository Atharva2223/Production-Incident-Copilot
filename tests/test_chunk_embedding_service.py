from app.models.log_chunk import LogChunk
from app.services.chunk_embedding_service import embed_chunks


def test_embed_chunks_returns_empty_list_for_empty_input() -> None:
    embedded_chunks = embed_chunks([])

    assert embedded_chunks == []


def test_embed_chunks_returns_one_embedded_chunk_per_input_chunk() -> None:
    chunks = [
        LogChunk(
            chunk_id="chunk_1",
            start_time="2026-04-11 10:01:01",
            end_time="2026-04-11 10:01:50",
            records=[],
            combined_text=(
                "2026-04-11 10:01:01 INFO OrderService Creating order\n"
                "2026-04-11 10:01:50 ERROR PaymentService Timeout while acquiring DB connection"
            ),
            services=["OrderService", "PaymentService"],
            levels=["ERROR", "INFO"],
        ),
        LogChunk(
            chunk_id="chunk_2",
            start_time="2026-04-11 10:02:10",
            end_time="2026-04-11 10:02:40",
            records=[],
            combined_text=(
                "2026-04-11 10:02:10 WARN RetryService Retrying payment authorization\n"
                "2026-04-11 10:02:40 ERROR OrderService Payment failed"
            ),
            services=["OrderService", "RetryService"],
            levels=["ERROR", "WARN"],
        ),
    ]

    embedded_chunks = embed_chunks(chunks)

    assert len(embedded_chunks) == 2

    assert embedded_chunks[0].chunk_id == "chunk_1"
    assert embedded_chunks[0].combined_text == chunks[0].combined_text
    assert embedded_chunks[0].services == ["OrderService", "PaymentService"]
    assert embedded_chunks[0].levels == ["ERROR", "INFO"]
    assert isinstance(embedded_chunks[0].embedding, list)
    assert len(embedded_chunks[0].embedding) > 0
    assert all(isinstance(value, float) for value in embedded_chunks[0].embedding)

    assert embedded_chunks[1].chunk_id == "chunk_2"
    assert embedded_chunks[1].combined_text == chunks[1].combined_text
    assert embedded_chunks[1].services == ["OrderService", "RetryService"]
    assert embedded_chunks[1].levels == ["ERROR", "WARN"]
    assert isinstance(embedded_chunks[1].embedding, list)
    assert len(embedded_chunks[1].embedding) > 0
    assert all(isinstance(value, float) for value in embedded_chunks[1].embedding)