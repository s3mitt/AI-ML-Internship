"""Email Tool: Validated email dispatch engine with safe sandbox demonstration mode."""

from __future__ import annotations
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Union
from core.errors import ExternalServiceError, ValidationError
from tools.base import BaseTool

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class EmailTool(BaseTool):
    """Drafts, validates, and dispatches emails with safe local sandbox containment."""

    name = "email"
    description = (
        "Send or draft an email. Validates recipient address, subject, body, "
        "and optional CC/BCC. Runs in safe sandbox mode by default to avoid unwanted outbound mail."
    )
    parameters = {
        "type": "object",
        "properties": {
            "recipient": {
                "type": "string",
                "description": "Recipient email address (e.g. 'mentor@example.com').",
            },
            "subject": {
                "type": "string",
                "description": "Subject line of the email.",
            },
            "body": {
                "type": "string",
                "description": "Body message text of the email.",
            },
            "cc": {
                "type": "array",
                "description": "Optional list of CC email addresses.",
            },
            "bcc": {
                "type": "array",
                "description": "Optional list of BCC email addresses.",
            },
            "force_send": {
                "type": "boolean",
                "description": "If true and SMTP credentials exist, dispatches via SMTP. Defaults to false (safe sandbox).",
            },
        },
        "required": ["recipient", "subject", "body"],
    }
    examples = [
        {
            "recipient": "mentor@example.com",
            "subject": "Internship Update - Day 20",
            "body": "Hi mentor, today I implemented tool chaining and function calling.",
        },
        {
            "recipient": "team@example.com",
            "subject": "Weather Report",
            "body": "The current temperature in Kolkata is 28.5 C.",
            "cc": ["lead@example.com"],
        },
    ]

    def _validate_email_syntax(self, address: str, field_name: str = "recipient") -> None:
        """Validate email format with regex."""
        if not address or not isinstance(address, str) or not EMAIL_REGEX.match(address.strip()):
            raise ValidationError(f"Invalid email address '{address}' in field '{field_name}'.", tool_name=self.name)

    def _send_live_smtp(self, recipient: str, subject: str, body: str, cc: List[str], bcc: List[str]) -> Dict[str, Any]:
        """Dispatch real email through configured SMTP server environment variables."""
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        if not smtp_host or not smtp_user or not smtp_pass:
            raise ExternalServiceError(
                "SMTP configuration missing (SMTP_HOST, SMTP_USER, SMTP_PASS). Cannot perform live dispatch.",
                tool_name=self.name,
            )

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = recipient
        msg["Subject"] = subject
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg.attach(MIMEText(body, "plain"))

        all_recipients = [recipient] + cc + bcc

        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, all_recipients, msg.as_string())
            return {
                "status": "delivered",
                "recipient": recipient,
                "subject": subject,
                "mode": "live_smtp",
            }
        except smtplib.SMTPAuthenticationError:
            raise ExternalServiceError("SMTP Authentication failed: invalid username or password.", tool_name=self.name)
        except Exception as e:
            raise ExternalServiceError(f"SMTP delivery failure: {str(e)}", tool_name=self.name)

    def run(
        self,
        recipient: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        force_send: bool = False,
        simulate_error: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Validate and safely record or send email."""
        # Validate recipient
        self._validate_email_syntax(recipient, "recipient")

        # Validate subject & body
        if not subject or not subject.strip():
            raise ValidationError("Email subject line cannot be empty.", tool_name=self.name)
        if not body or not body.strip():
            raise ValidationError("Email body message cannot be empty.", tool_name=self.name)

        # Validate CC / BCC
        clean_cc = []
        if cc:
            for c in cc:
                self._validate_email_syntax(c, "cc")
                clean_cc.append(c.strip())

        clean_bcc = []
        if bcc:
            for b in bcc:
                self._validate_email_syntax(b, "bcc")
                clean_bcc.append(b.strip())

        # Error simulation hook for testing
        if simulate_error == "auth_failure":
            raise ExternalServiceError("SMTP Authentication failed: Bad credentials.", tool_name=self.name)
        if simulate_error == "provider_failure":
            raise ExternalServiceError("Email provider connection timeout (SMTP 421).", tool_name=self.name)

        # Always default to sandbox unless explicit force_send is requested
        if force_send and os.getenv("SMTP_HOST"):
            return self._send_live_smtp(recipient.strip(), subject.strip(), body.strip(), clean_cc, clean_bcc)

        # Sandbox mode (Standard safe demonstration)
        return {
            "status": "queued_sandbox",
            "mode": "sandbox (safe mode - no outbound email transmitted)",
            "envelope": {
                "to": recipient.strip(),
                "cc": clean_cc,
                "bcc": clean_bcc,
                "subject": subject.strip(),
            },
            "body_length_chars": len(body.strip()),
            "body_preview": body.strip()[:100] + ("..." if len(body.strip()) > 100 else ""),
            "full_body": body.strip(),
        }
