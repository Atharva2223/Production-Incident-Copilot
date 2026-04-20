from datetime import datetime, timedelta
from typing import List

from app.models.log_chunk import LogChunk
from app.models.log_record import LogRecord
from app.services.chunker import chunk_logs_by_time_window


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _parse_timestamp(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, TIME_FORMAT)


def _build_chunk(chunk_id: int, records: List[LogRecord]) -> LogChunk:
    combined_text = "\n".join(record.raw_line.strip() for record in records)

    services = sorted({record.service for record in records if record.service})
    levels = sorted({record.level for record in records if record.level})

    start_time = records[0].timestamp if records else None
    end_time = records[-1].timestamp if records else None

    return LogChunk(
        chunk_id=f"chunk_{chunk_id}",
        start_time=start_time,
        end_time=end_time,
        records=records,
        combined_text=combined_text,
        services=services,
        levels=levels,
    )


def chunk_logs_by_time_window(
    records: List[LogRecord],
    window_seconds: int = 60,
) -> List[LogChunk]:
    valid_records = [record for record in records if record.timestamp]

    if not valid_records:
        return []

    chunks: List[LogChunk] = []
    current_chunk_records: List[LogRecord] = []
    chunk_start_time = _parse_timestamp(valid_records[0].timestamp)
    window_delta = timedelta(seconds=window_seconds)
    chunk_id = 1

    for record in valid_records:
        record_time = _parse_timestamp(record.timestamp)

        if record_time - chunk_start_time < window_delta:
            current_chunk_records.append(record)
        else:
            chunks.append(_build_chunk(chunk_id, current_chunk_records))
            chunk_id += 1
            current_chunk_records = [record]
            chunk_start_time = record_time

    if current_chunk_records:
        chunks.append(_build_chunk(chunk_id, current_chunk_records))

    return chunks

def test_chunk_logs_by_time_window_groups_records_within_same_window() -> None:
    records = [
        LogRecord(
            raw_line="2026-04-11 10:01:01 INFO OrderService Creating order",
            timestamp="2026-04-11 10:01:01",
            level="INFO",
            service="OrderService",
            message="Creating order",
            metadata={},
            parse_status=ParseStatus.SUCCESS,
            line_number=1,
            source_file="orders.log",
        ),
        LogRecord(
            raw_line="2026-04-11 10:01:20 INFO PaymentService Initiating payment",
            timestamp="2026-04-11 10:01:20",
            level="INFO",
            service="PaymentService",
            message="Initiating payment",
            metadata={},
            parse_status=ParseStatus.SUCCESS,
            line_number=2,
            source_file="orders.log",
        ),
        LogRecord(
            raw_line="2026-04-11 10:01:50 ERROR PaymentService Timeout while acquiring DB connection",
            timestamp="2026-04-11 10:01:50",
            level="ERROR",
            service="PaymentService",
            message="Timeout while acquiring DB connection",
            metadata={},
            parse_status=ParseStatus.SUCCESS,
            line_number=3,
            source_file="orders.log",
        ),
    ]

    chunks = chunk_logs_by_time_window(records, window_seconds=60)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "chunk_1"
    assert chunks[0].start_time == "2026-04-11 10:01:01"
    assert chunks[0].end_time == "2026-04-11 10:01:50"
    assert len(chunks[0].records) == 3
    assert chunks[0].services == ["OrderService", "PaymentService"]
    assert chunks[0].levels == ["ERROR", "INFO"]
    assert "Creating order" in chunks[0].combined_text
    assert "Initiating payment" in chunks[0].combined_text
    assert "Timeout while acquiring DB connection" in chunks[0].combined_text


def test_chunk_logs_by_time_window_splits_records_across_multiple_chunks() -> None:
    records = [
        LogRecord(
            raw_line="2026-04-11 10:01:01 INFO OrderService Creating order",
            timestamp="2026-04-11 10:01:01",
            level="INFO",
            service="OrderService",
            message="Creating order",
            metadata={},
            parse_status=ParseStatus.SUCCESS,
            line_number=1,
            source_file="orders.log",
        ),
        LogRecord(
            raw_line="2026-04-11 10:01:40 INFO PaymentService Initiating payment",
            timestamp="2026-04-11 10:01:40",
            level="INFO",
            service="PaymentService",
            message="Initiating payment",
            metadata={},
            parse_status=ParseStatus.SUCCESS,
            line_number=2,
            source_file="orders.log",
        ),
        LogRecord(
            raw_line="2026-04-11 10:02:20 ERROR PaymentService Timeout while acquiring DB connection",
            timestamp="2026-04-11 10:02:20",
            level="ERROR",
            service="PaymentService",
            message="Timeout while acquiring DB connection",
            metadata={},
            parse_status=ParseStatus.SUCCESS,
            line_number=3,
            source_file="orders.log",
        ),
    ]

    chunks = chunk_logs_by_time_window(records, window_seconds=60)

    assert len(chunks) == 2

    assert chunks[0].chunk_id == "chunk_1"
    assert chunks[0].start_time == "2026-04-11 10:01:01"
    assert chunks[0].end_time == "2026-04-11 10:01:40"
    assert len(chunks[0].records) == 2

    assert chunks[1].chunk_id == "chunk_2"
    assert chunks[1].start_time == "2026-04-11 10:02:20"
    assert chunks[1].end_time == "2026-04-11 10:02:20"
    assert len(chunks[1].records) == 1
    assert chunks[1].levels == ["ERROR"]


def test_chunk_logs_by_time_window_ignores_records_without_timestamps() -> None:
    records = [
        LogRecord(
            raw_line="2026-04-11 10:01:01 INFO OrderService Creating order",
            timestamp="2026-04-11 10:01:01",
            level="INFO",
            service="OrderService",
            message="Creating order",
            metadata={},
            parse_status=ParseStatus.SUCCESS,
            line_number=1,
            source_file="orders.log",
        ),
        LogRecord(
            raw_line="bad line without timestamp",
            timestamp=None,
            level="ERROR",
            service="PaymentService",
            message="Something failed",
            metadata={},
            parse_status=ParseStatus.FAILED,
            line_number=2,
            source_file="orders.log",
        ),
    ]

    chunks = chunk_logs_by_time_window(records, window_seconds=60)

    assert len(chunks) == 1
    assert len(chunks[0].records) == 1
    assert chunks[0].records[0].timestamp == "2026-04-11 10:01:01"


def test_chunk_logs_by_time_window_returns_empty_list_for_no_valid_timestamps() -> None:
    records = [
        LogRecord(
            raw_line="bad line 1",
            timestamp=None,
            level=None,
            service=None,
            message=None,
            metadata={},
            parse_status=ParseStatus.FAILED,
            line_number=1,
            source_file="bad.log",
        ),
        LogRecord(
            raw_line="bad line 2",
            timestamp=None,
            level=None,
            service=None,
            message=None,
            metadata={},
            parse_status=ParseStatus.FAILED,
            line_number=2,
            source_file="bad.log",
        ),
    ]

    chunks = chunk_logs_by_time_window(records, window_seconds=60)

    assert chunks == []