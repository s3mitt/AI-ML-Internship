"""Centralized error handling and standardized response structures for all tools."""

from __future__ import annotations
from typing import Any, Dict, Optional


class ToolError(Exception):
    """Base exception for all tool execution errors."""

    def __init__(self, message: str, tool_name: str = "unknown", error_type: str = "ToolError"):
        super().__init__(message)
        self.message = message
        self.tool_name = tool_name
        self.error_type = error_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": False,
            "error": {
                "type": self.error_type,
                "message": self.message,
                "tool": self.tool_name,
            },
        }


class ValidationError(ToolError):
    """Raised when input parameters fail validation constraints."""

    def __init__(self, message: str, tool_name: str = "unknown"):
        super().__init__(message=message, tool_name=tool_name, error_type="ValidationError")


class SecurityError(ToolError):
    """Raised when an operation violates security boundaries (e.g. traversal, unsafe SQL)."""

    def __init__(self, message: str, tool_name: str = "unknown"):
        super().__init__(message=message, tool_name=tool_name, error_type="SecurityError")


class ResourceNotFoundError(ToolError):
    """Raised when a requested resource (file, record, tool) does not exist."""

    def __init__(self, message: str, tool_name: str = "unknown"):
        super().__init__(message=message, tool_name=tool_name, error_type="ResourceNotFoundError")


class ExternalServiceError(ToolError):
    """Raised when an external API or service times out, rate limits, or fails."""

    def __init__(self, message: str, tool_name: str = "unknown"):
        super().__init__(message=message, tool_name=tool_name, error_type="ExternalServiceError")


def make_error_response(error_type: str, message: str, tool: str) -> Dict[str, Any]:
    """Helper to generate standardized JSON-compatible error payload."""
    return {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "tool": tool,
        },
    }


def make_success_response(data: Any, tool: str) -> Dict[str, Any]:
    """Helper to generate standardized JSON-compatible success payload."""
    return {
        "success": True,
        "data": data,
        "tool": tool,
    }
