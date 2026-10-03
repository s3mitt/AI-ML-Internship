# PR #1: Feature A - Note Storage Engine

## Description
This pull request introduces the core persistence module `storage.py` for the Smart Notes CLI application.
It provides functions to:
- Add a new note with an incremental ID and ISO timestamp.
- List all stored notes.
- Retrieve a single note by its ID.
- Delete a note by its ID.
- Read and write notes safely to a JSON file (`notes.json`), gracefully handling missing or corrupted files.

## Files Changed
- `storage.py`: Core CRUD operations and JSON persistence.
- `pytest.ini`: Configured test runner paths.
- `tests/test_storage.py`: Unit test coverage for adding, listing, fetching, deleting, and edge cases (corrupted files).

## Testing Notes
- Run `pytest` to execute all tests.
- All 4 storage unit tests passed successfully.
