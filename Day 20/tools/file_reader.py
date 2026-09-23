"""File Reader Tool: Sandboxed file reader supporting .txt, .md, .json, and .csv formats."""

from __future__ import annotations
import csv
import io
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from core.errors import ResourceNotFoundError, SecurityError, ValidationError
from tools.base import BaseTool

ALLOWED_EXTENSIONS = {".txt", ".md", ".json", ".csv"}
DEFAULT_BASE_DIR = Path(__file__).resolve().parent.parent


class FileReaderTool(BaseTool):
    """Safely reads and parses local files (.txt, .md, .json, .csv) with sandbox traversal guards."""

    name = "file_reader"
    description = (
        "Read contents of local files (.txt, .md, .json, .csv). "
        "Automatically parses JSON and CSV formats while enforcing directory sandboxing."
    )
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Relative or absolute path to the target file.",
            },
            "base_dir": {
                "type": "string",
                "description": "Optional base directory for sandboxing (defaults to project root).",
            },
        },
        "required": ["file_path"],
    }
    examples = [
        {"file_path": "data/employees.csv"},
        {"file_path": "data/sample.json"},
        {"file_path": "data/internship_notes.md"},
    ]

    def __init__(self, allowed_base_dir: Optional[Path] = None):
        super().__init__()
        self.allowed_base_dir = (allowed_base_dir or DEFAULT_BASE_DIR).resolve()

    def _resolve_and_validate_path(self, path_str: str, custom_base_dir: Optional[str] = None) -> Path:
        """Resolve path and guard against directory traversal attacks."""
        base = Path(custom_base_dir).resolve() if custom_base_dir else self.allowed_base_dir
        target = (base / path_str).resolve() if not Path(path_str).is_absolute() else Path(path_str).resolve()

        # Check path traversal
        try:
            target.relative_to(base)
        except ValueError:
            # Check if target is inside the overall project root
            try:
                target.relative_to(DEFAULT_BASE_DIR)
            except ValueError:
                raise SecurityError(
                    f"Path traversal access denied: '{path_str}' is outside allowed directory '{base}'.",
                    tool_name=self.name,
                )

        # If not found directly, check if it resides in the data/ subdirectory
        if not target.exists() and (base / "data" / path_str).exists():
            target = (base / "data" / path_str).resolve()

        if not target.exists():
            raise ResourceNotFoundError(f"File not found: '{path_str}' (resolved to '{target}').", tool_name=self.name)

        if not target.is_file():
            raise ValidationError(f"Target path '{path_str}' is a directory, not a file.", tool_name=self.name)

        ext = target.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Unsupported file format '{ext}'. Allowed extensions are: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                tool_name=self.name,
            )

        return target

    def run(self, file_path: str, base_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Read and parse the requested file safely."""
        if not file_path or not file_path.strip():
            raise ValidationError("File path cannot be empty.", tool_name=self.name)

        target = self._resolve_and_validate_path(file_path.strip(), base_dir)
        ext = target.suffix.lower()
        file_size = target.stat().st_size

        try:
            with open(target, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except UnicodeDecodeError:
            raise ValidationError(f"Failed to decode '{target.name}'. Ensure file is UTF-8 encoded text.", tool_name=self.name)

        parsed_content: Union[str, Dict[str, Any], list]
        metadata: Dict[str, Any] = {"size_bytes": file_size, "extension": ext}

        if ext == ".json":
            try:
                parsed_content = json.loads(raw_text)
            except json.JSONDecodeError as jde:
                raise ValidationError(f"Malformed JSON in '{target.name}': {jde.msg} (line {jde.lineno})", tool_name=self.name)

        elif ext == ".csv":
            try:
                reader = csv.DictReader(io.StringIO(raw_text))
                headers = reader.fieldnames or []
                rows = list(reader)
                metadata["columns"] = headers
                metadata["total_rows"] = len(rows)
                parsed_content = {
                    "headers": headers,
                    "rows": rows,
                    "raw_text": raw_text,
                }
            except Exception as e:
                raise ValidationError(f"Malformed CSV in '{target.name}': {str(e)}", tool_name=self.name)

        else:
            # .txt and .md
            parsed_content = raw_text

        return {
            "filename": target.name,
            "relative_path": str(target.relative_to(DEFAULT_BASE_DIR)),
            "metadata": metadata,
            "content": parsed_content,
        }
