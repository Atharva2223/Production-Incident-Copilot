from app.models.retrieval_result import RetrievalResult
from app.services.prompt_builder import build_incident_analysis_prompt


def test_build_incident_analysis_prompt_includes_question_and_context() -> None:
    question = "Why are payments failing?"
    chunks = [
        RetrievalResult(
            chunk_id="chunk_1",
            document="PaymentService timeout while acquiring DB connection",
            metadata={"services": "PaymentService", "levels": "ERROR"},
            distance=0.12,
        )
    ]

    prompt = build_incident_analysis_prompt(question=question, retrieved_chunks=chunks)

    assert "Why are payments failing?" in prompt
    assert "chunk_1" in prompt
    assert "PaymentService timeout while acquiring DB connection" in prompt