"""Unit tests for the Email tool."""

import pytest
from tools.email_tool import EmailTool


@pytest.fixture
def email_tool():
    return EmailTool()


def test_email_valid_sandbox_dispatch(email_tool):
    res = email_tool.execute(
        recipient="abc@example.com",
        subject="Internship Update",
        body="Progress on Day 20 tasks.",
    )
    assert res["success"] is True
    data = res["data"]
    assert data["status"] == "queued_sandbox"
    assert data["envelope"]["to"] == "abc@example.com"
    assert data["envelope"]["subject"] == "Internship Update"


def test_email_with_cc_and_bcc(email_tool):
    res = email_tool.execute(
        recipient="lead@example.com",
        subject="Status Report",
        body="Weekly accomplishments.",
        cc=["mentor@example.com"],
        bcc=["archive@example.com"],
    )
    assert res["success"] is True
    data = res["data"]
    assert "mentor@example.com" in data["envelope"]["cc"]
    assert "archive@example.com" in data["envelope"]["bcc"]


def test_email_invalid_recipient_address(email_tool):
    res = email_tool.execute(
        recipient="not-an-email-address",
        subject="Test",
        body="Hello",
    )
    assert res["success"] is False
    assert res["error"]["type"] == "ValidationError"


def test_email_missing_subject_or_body(email_tool):
    res1 = email_tool.execute(recipient="abc@example.com", subject="", body="Body text")
    assert res1["success"] is False
    assert res1["error"]["type"] == "ValidationError"

    res2 = email_tool.execute(recipient="abc@example.com", subject="Subject", body="")
    assert res2["success"] is False
    assert res2["error"]["type"] == "ValidationError"


def test_email_simulated_auth_failure(email_tool):
    res = email_tool.execute(
        recipient="abc@example.com",
        subject="Test",
        body="Test message",
        simulate_error="auth_failure",
    )
    assert res["success"] is False
    assert res["error"]["type"] == "ExternalServiceError"
