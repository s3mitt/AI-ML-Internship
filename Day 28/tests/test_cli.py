import os
import pytest
from main import cmd_add, cmd_list, cmd_delete, cmd_search, cmd_summarize, main
import storage


def test_cli_add_and_validation(tmp_path):
    test_file = str(tmp_path / "notes.json")
    
    # Valid note
    assert cmd_add("My first CLI note", filepath=test_file) == 0
    notes = storage.list_notes(filepath=test_file)
    assert len(notes) == 1

    # Empty content
    assert cmd_add("", filepath=test_file) == 1
    assert cmd_add("   ", filepath=test_file) == 1


def test_cli_list(tmp_path, capsys):
    test_file = str(tmp_path / "notes.json")
    
    # Empty list
    assert cmd_list(filepath=test_file) == 0
    captured = capsys.readouterr()
    assert "No notes found" in captured.out

    # Non-empty list
    storage.add_note("Note A", filepath=test_file)
    assert cmd_list(filepath=test_file) == 0
    captured = capsys.readouterr()
    assert "[1] Note A" in captured.out


def test_cli_delete(tmp_path, capsys):
    test_file = str(tmp_path / "notes.json")
    note = storage.add_note("To be deleted", filepath=test_file)

    # Valid deletion
    assert cmd_delete(note["id"], filepath=test_file) == 0
    
    # Deleting non-existent note
    assert cmd_delete(999, filepath=test_file) == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_cli_search(tmp_path, capsys):
    test_file = str(tmp_path / "notes.json")
    storage.add_note("Quantum computing breakthrough", filepath=test_file)

    # Empty keyword
    assert cmd_search("", filepath=test_file) == 1
    assert cmd_search("   ", filepath=test_file) == 1

    # Matching search
    assert cmd_search("quantum", filepath=test_file) == 0
    captured = capsys.readouterr()
    assert "Found 1 matching note(s)" in captured.out

    # No match
    assert cmd_search("biology", filepath=test_file) == 0
    captured = capsys.readouterr()
    assert "No notes found matching" in captured.out


def test_cli_summarize(tmp_path, capsys):
    test_file = str(tmp_path / "notes.json")
    long_note = (
        "Python is used widely across machine learning and data science. "
        "Python has an intuitive syntax that developers love. "
        "The language ecosystem supports web development and automation. "
        "Python developers enjoy huge community support."
    )
    note = storage.add_note(long_note, filepath=test_file)

    # Invalid ID
    assert cmd_summarize(999, filepath=test_file) == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err

    # Valid ID
    assert cmd_summarize(note["id"], num_sentences=2, filepath=test_file) == 0
    captured = capsys.readouterr()
    assert f"Summary for Note [{note['id']}]" in captured.out
