from app.models.log_record import LogRecord

def normalize_log_record(record: LogRecord) -> LogRecord:
    normalized_metadata = {
        key.strip(): value.strip()
        for key,value in record.metadata.items()
        if key.strip() and value.strip()
    }

    return LogRecord(
        raw_line=record.raw_line,
        timestamp=record.timestamp.strip() if record.timestamp else None,
        level=record.level.strip().upper() if record.level else None,
        service=record.service.strip() if record.service else None,
        message=record.message.strip() if record.message else None,
        metadata=normalized_metadata,
        parse_status=record.parse_status,
        line_number=record.line_number,
        source_file=record.source_file,
    )
def normalize_log_records(records: list[LogRecord]) -> list[LogRecord]:
    return [normalize_log_record(record) for record in records]