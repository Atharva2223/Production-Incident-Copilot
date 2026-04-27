from app.models.analysis_result import AnalysisResult
from app.services.llm_service import generate_llm_response
from app.services.prompt_builder import build_incident_analysis_prompt
from app.services.retriever import retrieve_relevant_chunks


def analyze_incident(
    question: str,
    n_results: int = 3,
    chroma_path: str = "chroma_db",
    collection_name: str = "log_chunks",
) -> AnalysisResult:
    retrieved_chunks = retrieve_relevant_chunks(
        query_text=question,
        n_results=n_results,
        chroma_path=chroma_path,
        collection_name=collection_name,
    )

    prompt = build_incident_analysis_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks,
    )

    answer = generate_llm_response(prompt)

    return AnalysisResult(
        question=question,
        answer=answer,
        retrieved_chunks=retrieved_chunks,
    )