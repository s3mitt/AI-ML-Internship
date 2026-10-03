"""Storage and JSON persistence layer for Smart Notes CLI."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Optional

from exceptions import ValidationError

logger = logging.getLogger(__name__)

DEFAULT_FILE = "notes.json"


def load_notes(filepath: str = DEFAULT_FILE) -> list[dict[str, Any]]:
    """Load notes list from a JSON file.

    Returns an empty list if the file is missing or corrupted.
    """
    if not os.path.exists(filepath):
        logger.debug("Storage file '%s' does not exist yet. Returning empty list.", filepath)
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                logger.warning("Storage file '%s' did not contain a JSON list. Resetting.", filepath)
                return []
            return data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to decode JSON from '%s': %s. Returning empty list.", filepath, e)
        return []


def save_notes(notes: list[dict[str, Any]], filepath: str = DEFAULT_FILE) -> None:
    """Save notes list atomically to a JSON file."""
    temp_filepath = f"{filepath}.tmp"
    with open(temp_filepath, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2)
    os.replace(temp_filepath, filepath)


def add_note(content: str, filepath: str = DEFAULT_FILE) -> dict[str, Any]:
    """Add a new note with an auto-incremented ID and timestamp.

    Raises:
        ValidationError: If content is empty or contains only whitespace.
    """
    if not content or not content.strip():
        raise ValidationError("Note content cannot be empty or only whitespace.")

    notes = load_notes(filepath)
    next_id = max([n.get("id", 0) for n in notes], default=0) + 1
    new_note = {
        "id": next_id,
        "content": content.strip(),
        "created_at": datetime.now().isoformat()
    }
    notes.append(new_note)
    save_notes(notes, filepath)
    logger.info("Created note #%d in '%s'", next_id, filepath)
    return new_note


def list_notes(filepath: str = DEFAULT_FILE) -> list[dict[str, Any]]:
    """Return all notes from storage."""
    return load_notes(filepath)


def get_note(note_id: int, filepath: str = DEFAULT_FILE) -> Optional[dict[str, Any]]:
    """Retrieve a single note by ID, or None if not found."""
    notes = load_notes(filepath)
    for n in notes:
        if n.get("id") == note_id:
            return n
    return None


def delete_note(note_id: int, filepath: str = DEFAULT_FILE) -> bool:
    """Delete a note by ID. Returns True if deleted, False if not found."""
    notes = load_notes(filepath)
    initial_len = len(notes)
    notes = [n for n in notes if n.get("id") != note_id]
    if len(notes) < initial_len:
        save_notes(notes, filepath)
        logger.info("Deleted note #%d from '%s'", note_id, filepath)
        return True
    return False
