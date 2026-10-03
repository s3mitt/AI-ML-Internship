# Smart Notes CLI

A lightweight, intelligent command-line tool built in Python for managing text notes and deriving instant insights through keyword relevance ranking and extractive frequency-based summarization.

---

## Architecture & Project Structure

```text
Day 28/
├── exceptions.py          # Custom domain exceptions (NoteError, ValidationError, etc.)
├── main.py                # Command-line interface and subcommand dispatching
├── storage.py             # Feature A: JSON persistence layer & CRUD operations
├── search.py              # Feature B: Keyword search & extractive summarization
├── pytest.ini             # Pytest configuration
├── README.md              # Project documentation and user manual
├── CODE_REVIEW_REPORT.md  # Comprehensive Senior Engineer Code Review Report
├── PULL_REQUEST_A.md      # Feature A pull request documentation
├── PULL_REQUEST_B.md      # Feature B & Refactoring pull request documentation
└── tests/
    ├── test_storage.py    # Unit tests for storage engine
    └── test_search.py     # Unit tests for search, summarization & edge cases
```

---

## Features

- **Note Storage (Feature A)**:
  - Add notes with automatic incremental IDs and ISO-8601 timestamps.
  - List all stored notes.
  - Retrieve and delete notes by unique ID.
  - Robust JSON persistence with atomic writes and corrupted-file recovery.
- **Search & Extractive Summarization (Feature B)**:
  - **Relevance-Ranked Keyword Search**: Ranks matching notes based on term frequency across content.
  - **Extractive Summarizer**: Tokenizes sentences, computes word frequency distribution (filtering stop-words), scores candidate sentences, and selects the most informative top sentences while preserving chronological flow.
- **Unified Modular CLI**:
  - Clean command structure powered by `argparse`.
  - Comprehensive input validation and meaningful exit codes (`0` for success, `1` for error).

---

## Installation & Requirements

- **Python**: Version 3.10 or higher.
- **Dependencies**: Only the Python Standard Library is required to run the CLI.
- **Testing**: `pytest` for executing unit and edge-case tests.

```bash
# Verify Python version
python --version

# Verify pytest installation
pytest --version
```

---

## CLI Usage Guide

### 1. Adding a Note
```bash
python main.py add "Python is a modern programming language with clean syntax. It is widely used in AI, data science, and web development. Python has an extensive standard library."
```

### 2. Listing All Notes
```bash
python main.py list
```
*Output:*
```text
Total notes: 1
[1] Python is a modern programming language with clean syntax. It is widely used in AI, data science, and web development. Python has an extensive standard library.
```

### 3. Searching Notes by Keyword
```bash
python main.py search "python"
```
*Output:*
```text
Found 1 matching note(s):
[1] Python is a modern programming language with clean syntax. It is widely used in AI, data science, and web development. Python has an extensive standard library.
```

### 4. Summarizing a Note
```bash
# Default summary (up to 3 sentences)
python main.py summarize 1

# Custom summary sentence count
python main.py summarize 1 --count 2
```

### 5. Deleting a Note
```bash
python main.py delete 1
```

---

## Running Tests

Run the test suite with `pytest`:

```bash
# Run all tests
pytest

# Run tests with detailed output
pytest -v
```
