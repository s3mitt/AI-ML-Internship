"""Unit tests for the Date/Time tool."""

import pytest
from tools.date_tool import DateTool


@pytest.fixture
def date_tool():
    return DateTool()


def test_date_current(date_tool):
    res = date_tool.execute(action="current")
    assert res["success"] is True
    assert "date" in res["data"]
    assert "time" in res["data"]
    assert "day_of_week" in res["data"]


def test_date_day_of_week(date_tool):
    res = date_tool.execute(action="day_of_week", date="25 September 2026")
    assert res["success"] is True
    assert res["data"]["day_of_week"] == "Friday"


def test_date_days_between(date_tool):
    res = date_tool.execute(
        action="days_between",
        start_date="2026-09-01",
        end_date="2026-09-25",
    )
    assert res["success"] is True
    assert res["data"]["days_difference"] == 24


def test_date_add_days(date_tool):
    res = date_tool.execute(
        action="add_days",
        date="2026-09-01",
        days=30,
    )
    assert res["success"] is True
    assert res["data"]["result_date"] == "2026-10-01"


def test_date_convert_format(date_tool):
    res = date_tool.execute(
        action="convert_format",
        date="2026-09-25",
        target_format="%d/%m/%Y",
    )
    assert res["success"] is True
    assert res["data"]["formatted_date"] == "25/09/2026"


def test_date_invalid_date_string(date_tool):
    res = date_tool.execute(action="day_of_week", date="invalid-non-date-xyz")
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"
