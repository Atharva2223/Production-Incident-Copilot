from typing import Any, Dict

from pydantic import BaseModel, Field


class RetrievalResult(BaseModel):
    chunk_id: str = Field(..., description="Unique identifier of the retrieved chunk")
    document: str = Field(..., description="Retrieved chunk text")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata associated with the retrieved chunk",
    )
    distance: float | None = Field(
        default=None,
        description="Similarity distance returned by the vector store",
    )