"""Unit tests for Structured Logging and Correlation ID Tracking."""

import json
import logging
from pythonjsonlogger import jsonlogger
import pytest
from app.logging_config import (
    CorrelationIdFilter,
    get_correlation_id,
    get_logger,
    set_correlation_id,
    setup_logging,
)


@pytest.mark.unit
class TestLogging:
    """Test suite verifying structured logging, loggers, formatters, and correlation IDs."""

    def test_correlation_id_context(self):
        """Verify correlation ID context variable setter and getter."""
        test_id = "test-correlation-uuid-999"
        set_correlation_id(test_id)
        assert get_correlation_id() == test_id

    def test_correlation_filter_injects_metadata(self):
        """Verify filter injects request_id, service, and env into log record."""
        corr_id = "req-audit-12345"
        set_correlation_id(corr_id)

        filt = CorrelationIdFilter(service_name="test-service", env="staging")
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="User action performed",
            args=(),
            exc_info=None,
        )

        assert filt.filter(record) is True
        assert record.request_id == corr_id
        assert record.service == "test-service"
        assert record.env == "staging"

    def test_json_formatter_produces_valid_json(self):
        """Verify JSON formatter outputs parseable JSON containing all expected fields."""
        corr_id = "trace-456"
        set_correlation_id(corr_id)

        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s"
        )
        record = logging.LogRecord(
            name="worker",
            level=logging.WARNING,
            pathname="worker.py",
            lineno=25,
            msg="Queue threshold reached",
            args=(),
            exc_info=None,
        )
        record.request_id = corr_id

        output = formatter.format(record)
        data = json.loads(output)

        assert data["levelname"] == "WARNING"
        assert data["name"] == "worker"
        assert data["message"] == "Queue threshold reached"
        assert data["request_id"] == corr_id
        assert "asctime" in data

    def test_setup_logging_configuration(self):
        """Verify setup_logging properly configures root logger."""
        setup_logging(log_level="DEBUG", log_format="json", service_name="pytest-app", env="testing")
        root = logging.getLogger()
        assert root.level == logging.DEBUG
        assert len(root.handlers) >= 1

    def test_get_logger(self):
        """Verify get_logger returns logger with expected name."""
        logger = get_logger("my.custom.service")
        assert logger.name == "my.custom.service"
