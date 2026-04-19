from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class ParseStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class LogRecord(BaseModel):
    raw_line: str = Field(..., description="Original unmodified log line")
    timestamp: Optional[str] = Field(
        default=None,
        description="Timestamp extracted from the log line",
    )
    level: Optional[str] = Field(
        default=None,
        description="Log severity level such as INFO, WARN, or ERROR",
    )
    service: Optional[str] = Field(
        default=None,
        description="Service or component that generated the log",
    )
    message: Optional[str] = Field(
        default=None,
        description="Human-readable log message",
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Key-value metadata extracted from the log line",
    )
    parse_status: ParseStatus = Field(
        ...,
        description="Parsing outcome for this log line",
    )
    line_number: Optional[int] = Field(
        default=None,
        description="Line number in the source file",
    )
    source_file: Optional[str] = Field(
        default=None,
        description="Name of the source log file",
    )