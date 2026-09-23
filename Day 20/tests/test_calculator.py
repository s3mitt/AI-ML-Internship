"""Unit tests for the Calculator tool."""

import pytest
from tools.calculator import CalculatorTool
from core.errors import ValidationError, SecurityError


@pytest.fixture
def calc():
    return CalculatorTool()


def test_calculator_basic_arithmetic(calc):
    res = calc.execute(expression="25 * 48")
    assert res["success"] is True
    assert res["data"]["result"] == 1200


def test_calculator_division_and_parentheses(calc):
    res1 = calc.execute(expression="100 / 4")
    assert res1["success"] is True
    assert res1["data"]["result"] == 25

    res2 = calc.execute(expression="(25 + 15) * 2")
    assert res2["success"] is True
    assert res2["data"]["result"] == 80


def test_calculator_percentage(calc):
    res = calc.execute(expression="15% of 800")
    assert res["success"] is True
    assert res["data"]["result"] == 120


def test_calculator_average(calc):
    res = calc.execute(expression="Average of 10, 20, 30")
    assert res["success"] is True
    assert res["data"]["result"] == 20


def test_calculator_division_by_zero(calc):
    res = calc.execute(expression="50 / 0")
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"
    assert "Division by zero" in res["error"]["message"]


def test_calculator_malformed_expression(calc):
    res = calc.execute(expression="25 * + / 10")
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"


def test_calculator_empty_input(calc):
    res = calc.execute(expression="")
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"


def test_calculator_security_blocks_code_execution(calc):
    res = calc.execute(expression="__import__('os').system('dir')")
    assert res["success"] is False
    assert res["error"]["type"] in ("SecurityError", "ValidationError")
