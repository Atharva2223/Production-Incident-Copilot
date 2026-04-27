from typing import List

from pydantic import BaseModel, Field


class EmbeddedChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    embedding: List[float] = Field(
        default_factory=list,
        description="Vector embedding for the chunk text",
    )
    combined_text: str = Field(
        ...,
        description="Combined text used to generate the embedding",
    )
    start_time: str | None = Field(
        default=None,
        description="Start timestamp of the chunk",
    )
    end_time: str | None = Field(
        default=None,
        description="End timestamp of the chunk",
    )
    services: List[str] = Field(
        default_factory=list,
        description="Unique services present in the chunk",
    )
    levels: List[str] = Field(
        default_factory=list,
        description="Unique log levels present in the chunk",
    )