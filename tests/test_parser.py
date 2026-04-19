from app.models.log_record import ParseStatus, LogRecord
from app.services.parser import parse_log_file, parse_log_line
from app.services.preprocessor import normalize_log_record,normalize_log_records

def test_parse_log_file_returns_all_records(tmp_path) -> None:
    log_content = (
        "2026-04-11 10:01:01 INFO OrderService Creating order order_id=101\n"
        "2026-04-11 10:01:02 ERROR PaymentService Timeout while acquiring DB connection order_id=101\n"
    )

    log_file = tmp_path / "payment_failure.log"
    log_file.write_text(log_content, encoding="utf-8")

    records = parse_log_file(str(log_file))

    assert len(records) == 2

    assert records[0].line_number == 1
    assert records[0].source_file == "payment_failure.log"
    assert records[0].level == "INFO"
    assert records[0].service == "OrderService"
    assert records[0].metadata == {"order_id": "101"}

    assert records[1].line_number == 2
    assert records[1].source_file == "payment_failure.log"
    assert records[1].level == "ERROR"
    assert records[1].service == "PaymentService"
    assert records[1].metadata == {"order_id": "101"}


def test_parse_log_file_handles_invalid_lines(tmp_path) -> None:
    log_content = (
        "2026-04-11 10:01:01 INFO OrderService Creating order order_id=101\n"
        "\n"
        "ERROR PaymentService failed\n"
    )

    log_file = tmp_path / "mixed_logs.log"
    log_file.write_text(log_content, encoding="utf-8")

    records = parse_log_file(str(log_file))

    assert len(records) == 3

    assert records[0].parse_status == ParseStatus.SUCCESS
    assert records[0].line_number == 1

    assert records[1].parse_status == ParseStatus.FAILED
    assert records[1].line_number == 2
    assert records[1].source_file == "mixed_logs.log"

    assert records[2].parse_status == ParseStatus.FAILED
    assert records[2].line_number == 3
    assert records[2].source_file == "mixed_logs.log"

def test_parse_valid_log_line_with_metadata() -> None:
    raw_line = (
        "2026-04-11 10:01:04 ERROR PaymentService "
        "Timeout while acquiring DB connection order_id=101 timeout_ms=3000"
    )

    record = parse_log_line(
        raw_line=raw_line,
        line_number=7,
        source_file="payment_failure.log",
    )

    assert record.raw_line == raw_line
    assert record.timestamp == "2026-04-11 10:01:04"
    assert record.level == "ERROR"
    assert record.service == "PaymentService"
    assert record.message == "Timeout while acquiring DB connection"
    assert record.metadata == {"order_id": "101", "timeout_ms": "3000"}
    assert record.parse_status == ParseStatus.SUCCESS
    assert record.line_number == 7
    assert record.source_file == "payment_failure.log"


def test_parse_valid_log_line_without_metadata() -> None:
    raw_line = "2026-04-11 10:01:01 INFO OrderService Creating order"

    record = parse_log_line(raw_line=raw_line)

    assert record.timestamp == "2026-04-11 10:01:01"
    assert record.level == "INFO"
    assert record.service == "OrderService"
    assert record.message == "Creating order"
    assert record.metadata == {}
    assert record.parse_status == ParseStatus.SUCCESS


def test_parse_empty_log_line() -> None:
    raw_line = "   "

    record = parse_log_line(raw_line=raw_line, line_number=3)

    assert record.raw_line == raw_line
    assert record.timestamp is None
    assert record.level is None
    assert record.service is None
    assert record.message is None
    assert record.metadata == {}
    assert record.parse_status == ParseStatus.FAILED
    assert record.line_number == 3


def test_parse_incomplete_log_line() -> None:
    raw_line = "ERROR PaymentService failed"

    record = parse_log_line(raw_line=raw_line)

    assert record.raw_line == raw_line
    assert record.timestamp is None
    assert record.level is None
    assert record.service is None
    assert record.message is None
    assert record.metadata == {}
    assert record.parse_status == ParseStatus.FAILED


def test_parse_log_line_with_metadata_only_after_service() -> None:
    raw_line = "2026-04-11 10:01:05 WARN RetryService retry_count=2 order_id=101"

    record = parse_log_line(raw_line=raw_line)

    assert record.timestamp == "2026-04-11 10:01:05"
    assert record.level == "WARN"
    assert record.service == "RetryService"
    assert record.message is None
    assert record.metadata == {"retry_count": "2", "order_id": "101"}
    assert record.parse_status == ParseStatus.PARTIAL


def test_normalize_log_record_strips_whitespace_and_uppercases_level() -> None:
    record = LogRecord(
        raw_line=" 2026-04-11 10:01:04 error PaymentService Timeout ",
        timestamp=" 2026-04-11 10:01:04 ",
        level=" error ",
        service=" PaymentService ",
        message=" Timeout while acquiring DB connection ",
        metadata={" order_id ": " 101 ", " timeout_ms ": " 3000 "},
        parse_status=ParseStatus.SUCCESS,
        line_number=1,
        source_file="payment_failure.log",
    )

    normalized = normalize_log_record(record)

    assert normalized.timestamp == "2026-04-11 10:01:04"
    assert normalized.level == "ERROR"
    assert normalized.service == "PaymentService"
    assert normalized.message == "Timeout while acquiring DB connection"
    assert normalized.metadata == {"order_id": "101", "timeout_ms": "3000"}
    assert normalized.parse_status == ParseStatus.SUCCESS
    assert normalized.line_number == 1
    assert normalized.source_file == "payment_failure.log"


def test_normalize_log_record_removes_empty_metadata_keys_and_values() -> None:
    record = LogRecord(
        raw_line="test line",
        timestamp="2026-04-11 10:01:04",
        level="WARN",
        service="RetryService",
        message="Retry attempt recorded",
        metadata={
            " retry_count ": " 2 ",
            " ": "should_be_removed",
            "empty_value": " ",
            " valid_key ": " valid_value ",
        },
        parse_status=ParseStatus.SUCCESS,
        line_number=2,
        source_file="retry.log",
    )

    normalized = normalize_log_record(record)

    assert normalized.metadata == {
        "retry_count": "2",
        "valid_key": "valid_value",
    }


def test_normalize_log_records_normalizes_multiple_records() -> None:
    records = [
        LogRecord(
            raw_line="line 1",
            timestamp=" 2026-04-11 10:01:01 ",
            level=" info ",
            service=" OrderService ",
            message=" Creating order ",
            metadata={" order_id ": " 101 "},
            parse_status=ParseStatus.SUCCESS,
            line_number=1,
            source_file="orders.log",
        ),
        LogRecord(
            raw_line="line 2",
            timestamp=" 2026-04-11 10:01:02 ",
            level=" error ",
            service=" PaymentService ",
            message=" Payment failed ",
            metadata={" order_id ": " 101 ", " status_code ": " 500 "},
            parse_status=ParseStatus.SUCCESS,
            line_number=2,
            source_file="orders.log",
        ),
    ]

    normalized_records = normalize_log_records(records)

    assert len(normalized_records) == 2

    assert normalized_records[0].level == "INFO"
    assert normalized_records[0].service == "OrderService"
    assert normalized_records[0].message == "Creating order"
    assert normalized_records[0].metadata == {"order_id": "101"}

    assert normalized_records[1].level == "ERROR"
    assert normalized_records[1].service == "PaymentService"
    assert normalized_records[1].message == "Payment failed"
    assert normalized_records[1].metadata == {
        "order_id": "101",
        "status_code": "500",
    }