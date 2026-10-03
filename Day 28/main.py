"""Command-Line Interface for Smart Notes CLI."""

import argparse
import sys
from typing import Optional

import search
import storage
from exceptions import ValidationError


def cmd_add(text: str, filepath: str = storage.DEFAULT_FILE) -> int:
    """Add a new note to storage."""
    try:
        note = storage.add_note(text, filepath=filepath)
        print(f"Added note [{note['id']}]: \"{note['content']}\"")
        return 0
    except ValidationError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1


def cmd_list(filepath: str = storage.DEFAULT_FILE) -> int:
    """List all stored notes."""
    notes = storage.list_notes(filepath=filepath)
    if not notes:
        print("No notes found. Create one with: python main.py add \"<text>\"")
        return 0

    print(f"Total notes: {len(notes)}")
    for note in notes:
        print(f"[{note['id']}] {note['content']}")
    return 0


def cmd_delete(note_id: int, filepath: str = storage.DEFAULT_FILE) -> int:
    """Delete a note by ID."""
    deleted = storage.delete_note(note_id, filepath=filepath)
    if deleted:
        print(f"Deleted note [{note_id}].")
        return 0
    print(f"Error: Note with ID {note_id} not found.", file=sys.stderr)
    return 1


def cmd_search(keyword: str, filepath: str = storage.DEFAULT_FILE) -> int:
    """Search notes matching keyword, ranked by occurrence count."""
    clean_keyword = keyword.strip()
    if not clean_keyword:
        print("Error: Search keyword cannot be empty.", file=sys.stderr)
        return 1

    notes = storage.list_notes(filepath=filepath)
    if not notes:
        print("No notes available in storage to search.")
        return 0

    results = search.search_notes(clean_keyword, notes)
    if not results:
        print(f"No notes found matching query: '{clean_keyword}'.")
        return 0

    print(f"Found {len(results)} matching note(s):")
    for note in results:
        print(f"[{note['id']}] {note['content']}")
    return 0


def cmd_summarize(
    note_id: int,
    num_sentences: int = search.DEFAULT_SUMMARY_SENTENCE_COUNT,
    filepath: str = storage.DEFAULT_FILE
) -> int:
    """Generate extractive summary for a note by ID."""
    note = storage.get_note(note_id, filepath=filepath)
    if note is None:
        print(f"Error: Note with ID {note_id} not found.", file=sys.stderr)
        return 1

    content = note.get("content", "").strip()
    if not content:
        print(f"Note [{note_id}] has no text content to summarize.")
        return 0

    summary = search.summarize(content, num_sentences=num_sentences)
    print(f"--- Summary for Note [{note_id}] ---")
    print(summary)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="smart-notes",
        description="Smart Notes CLI: Manage and extract insights from your text notes."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new text note")
    add_parser.add_argument("text", help="Content of the note")

    # list
    subparsers.add_parser("list", help="List all notes")

    # delete
    del_parser = subparsers.add_parser("delete", help="Delete a note by ID")
    del_parser.add_argument("id", type=int, help="Numeric note ID to remove")

    # search
    search_parser = subparsers.add_parser("search", help="Search notes by keyword")
    search_parser.add_argument("keyword", help="Search keyword or term")

    # summarize
    sum_parser = subparsers.add_parser("summarize", help="Summarize a note by ID")
    sum_parser.add_argument("id", type=int, help="Numeric note ID to summarize")
    sum_parser.add_argument(
        "-n", "--count",
        type=int,
        default=search.DEFAULT_SUMMARY_SENTENCE_COUNT,
        help="Number of sentences for the summary (default: 3)"
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        return cmd_add(args.text)
    elif args.command == "list":
        return cmd_list()
    elif args.command == "delete":
        return cmd_delete(args.id)
    elif args.command == "search":
        return cmd_search(args.keyword)
    elif args.command == "summarize":
        return cmd_summarize(args.id, num_sentences=args.count)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
