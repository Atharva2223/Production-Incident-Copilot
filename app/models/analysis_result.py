from typing import List

from pydantic import BaseModel, Field

from app.models.retrieval_result import RetrievalResult


class AnalysisResult(BaseModel):
    question: str = Field(..., description="User question about the incident")
    answer: str = Field(..., description="LLM-generated answer")
    retrieved_chunks: List[RetrievalResult] = Field(
        default_factory=list,
        description="Retrieved chunks used as context",
    )