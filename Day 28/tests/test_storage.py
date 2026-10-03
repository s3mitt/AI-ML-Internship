import os
from storage import add_note, list_notes, get_note, delete_note, load_notes, save_notes


def test_add_and_list_notes(tmp_path):
    test_file = str(tmp_path / "notes.json")
    note1 = add_note("First note", filepath=test_file)
    note2 = add_note("Second note", filepath=test_file)

    assert note1["id"] == 1
    assert note2["id"] == 2
    assert note1["content"] == "First note"

    all_notes = list_notes(filepath=test_file)
    assert len(all_notes) == 2
    assert all_notes[0]["content"] == "First note"
    assert all_notes[1]["content"] == "Second note"


def test_get_note(tmp_path):
    test_file = str(tmp_path / "notes.json")
    created = add_note("Important meeting memo", filepath=test_file)
    
    fetched = get_note(created["id"], filepath=test_file)
    assert fetched is not None
    assert fetched["content"] == "Important meeting memo"

    missing = get_note(999, filepath=test_file)
    assert missing is None


def test_delete_note(tmp_path):
    test_file = str(tmp_path / "notes.json")
    n1 = add_note("Note 1", filepath=test_file)
    n2 = add_note("Note 2", filepath=test_file)

    assert delete_note(n1["id"], filepath=test_file) is True
    assert delete_note(n1["id"], filepath=test_file) is False

    remaining = list_notes(filepath=test_file)
    assert len(remaining) == 1
    assert remaining[0]["id"] == n2["id"]


def test_corrupted_or_missing_file(tmp_path):
    missing_file = str(tmp_path / "nonexistent.json")
    assert load_notes(missing_file) == []

    corrupted_file = str(tmp_path / "bad.json")
    with open(corrupted_file, "w") as f:
        f.write("{invalid_json:")
    assert load_notes(corrupted_file) == []
