from app.services.embedding_service import generate_embedding, generate_embeddings


def test_generate_embedding_returns_non_empty_vector() -> None:
    text = "PaymentService timeout while acquiring DB connection"
    embedding = generate_embedding(text)

    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(value, float) for value in embedding)


def test_generate_embeddings_returns_one_vector_per_input_text() -> None:
    texts = [
        "PaymentService timeout while acquiring DB connection",
        "OrderService marked order as failed",
    ]

    embeddings = generate_embeddings(texts)

    assert isinstance(embeddings, list)
    assert len(embeddings) == 2
    assert all(isinstance(embedding, list) for embedding in embeddings)
    assert all(len(embedding) > 0 for embedding in embeddings)
    assert all(isinstance(value, float) for embedding in embeddings for value in embedding)