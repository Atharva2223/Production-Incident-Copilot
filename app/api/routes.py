from fastapi import APIRouter, HTTPException

from app.models.api_models import (
    AnalyzeRequest,
    IndexLogsRequest,
    IndexLogsResponse,
)
from app.services.chunk_embedding_service import embed_chunks
from app.services.chunker import chunk_logs_by_time_window
from app.services.incident_analysis_service import analyze_incident
from app.services.parser import parse_log_file
from app.services.preprocessor import normalize_log_records
from app.services.vector_store import store_embedded_chunks


router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/index-logs", response_model=IndexLogsResponse)
def index_logs(request: IndexLogsRequest) -> IndexLogsResponse:
    try:
        parsed_records = parse_log_file(request.file_path)
        normalized_records = normalize_log_records(parsed_records)
        chunks = chunk_logs_by_time_window(
            normalized_records,
            window_seconds=request.window_seconds,
        )
        embedded_chunks = embed_chunks(chunks)

        store_embedded_chunks(
            chunks=embedded_chunks,
            chroma_path=request.chroma_path,
            collection_name=request.collection_name,
        )

        return IndexLogsResponse(
            message="Logs indexed successfully",
            total_records=len(normalized_records),
            total_chunks=len(chunks),
            total_embedded_chunks=len(embedded_chunks),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/analyze")
def analyze_logs(request: AnalyzeRequest) -> dict:
    try:
        result = analyze_incident(
            question=request.question,
            n_results=request.n_results,
            chroma_path=request.chroma_path,
            collection_name=request.collection_name,
        )
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc