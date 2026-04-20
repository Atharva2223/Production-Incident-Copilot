from typing import List

from pydantic import BaseModel, Field

from app.models.log_record import LogRecord


class LogChunk(BaseModel):
    chunk_id: str = Field(..., description = "Unique identifier for the chunk")
    start_time: str | None = Field(
        default =  None,
        description = "Start timestamp of the chunk",
    )
    end_time: str | None = Field(
        default= None,
        desription="End timestamp of the chunk",
    )
    records: List[LogRecord] = Field(
        default_factory=list,
        description="Log records included in this chunk",
    )
    combined_text: str = Field(
        ...,
        description="Combined text representation of the chunk",
    )
    services: List[str] = Field(
        default_factory=list,
        description="Unique services present in the chunk",
    )
    levels: List[str] = Field(
        default_factory=list,
        description="Unique log levels present in the chunk",
    )

