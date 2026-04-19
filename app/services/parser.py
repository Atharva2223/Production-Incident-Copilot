from typing import Dict, List, Tuple
from pathlib import Path
from app.models.log_record import LogRecord, ParseStatus


def _is_metadata_token(token: str) -> bool:
    return "=" in token and not token.startswith("=") and not token.endswith("=")


def _split_message_and_metadata(tokens: List[str]) -> Tuple[str, Dict[str, str]]:
    message_parts: List[str] = []
    metadata: Dict[str, str] = {}

    for token in tokens:
        if _is_metadata_token(token):
            key, value = token.split("=", 1)
            metadata[key] = value
        else:
            message_parts.append(token)

    message = " ".join(message_parts).strip()
    return message, metadata

def parse_log_file(file_path: str) -> list[LogRecord]:
    records: list[LogRecord] = []
    path = Path(file_path)

    with path.open("r", encoding = "utf-8") as log_file:
        for line_number, raw_line in enumerate(log_file, start=1):
            record = parse_log_line(
            raw_line=raw_line,
            line_number=line_number,
            source_file=path.name,
            )
            records.append(record)
        return records

def parse_log_line(
    raw_line: str,
    line_number: int | None = None,
    source_file: str | None = None,
) -> LogRecord:
    stripped_line = raw_line.strip()

    if not stripped_line:
        return LogRecord(
            raw_line=raw_line,
            parse_status=ParseStatus.FAILED,
            line_number=line_number,
            source_file=source_file,
        )

    tokens = stripped_line.split()

    if len(tokens) < 4:
        return LogRecord(
            raw_line=raw_line,
            parse_status=ParseStatus.FAILED,
            line_number=line_number,
            source_file=source_file,
        )

    timestamp = f"{tokens[0]} {tokens[1]}"
    level = tokens[2]
    service = tokens[3]
    remaining_tokens = tokens[4:]

    message, metadata = _split_message_and_metadata(remaining_tokens)

    parse_status = ParseStatus.SUCCESS
    if not message:
        parse_status = ParseStatus.PARTIAL

    return LogRecord(
        raw_line=raw_line,
        timestamp=timestamp,
        level=level,
        service=service,
        message=message if message else None,
        metadata=metadata,
        parse_status=parse_status,
        line_number=line_number,
        source_file=source_file,
    )