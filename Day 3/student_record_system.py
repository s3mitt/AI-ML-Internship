"""
Student Record Management System
---------------------------------
A menu-driven console application that stores and retrieves student
records from a plain text file (students.txt).

Storage format:
    Each record is stored on a single line, with fields separated by
    the pipe character "|":

        roll_no|name|age|course|marks

Run:
    python student_record_system.py
"""

import os

DATA_FILE = "students.txt"
DELIMITER = "|"
FIELDS = ["Roll No", "Name", "Age", "Course", "Marks"]


# --------------------------------------------------------------------------- #
# File helpers
# --------------------------------------------------------------------------- #
def ensure_data_file():
    """Create the data file if it doesn't already exist."""
    if not os.path.exists(DATA_FILE):
        open(DATA_FILE, "w", encoding="utf-8").close()


def load_records():
    """Read all records from the text file into a list of dicts."""
    ensure_data_file()
    records = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(DELIMITER)
            if len(parts) != len(FIELDS):
                continue  # skip malformed lines
            record = {
                "roll_no": parts[0],
                "name": parts[1],
                "age": parts[2],
                "course": parts[3],
                "marks": parts[4],
            }
            records.append(record)
    return records


def save_records(records):
    """Overwrite the text file with the given list of record dicts."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for r in records:
            line = DELIMITER.join(
                [r["roll_no"], r["name"], r["age"], r["course"], r["marks"]]
            )
            f.write(line + "\n")


# --------------------------------------------------------------------------- #
# Core operations
# --------------------------------------------------------------------------- #
def add_record():
    print("\n--- Add New Student Record ---")
    roll_no = input("Roll No: ").strip()

    records = load_records()
    if any(r["roll_no"] == roll_no for r in records):
        print(f"Error: A record with Roll No '{roll_no}' already exists.")
        return

    name = input("Name: ").strip()
    age = input("Age: ").strip()
    course = input("Course: ").strip()
    marks = input("Marks: ").strip()

    if not roll_no or not name:
        print("Error: Roll No and Name cannot be empty. Record not saved.")
        return

    records.append(
        {"roll_no": roll_no, "name": name, "age": age, "course": course, "marks": marks}
    )
    save_records(records)
    print(f"Record for '{name}' added successfully.")


def view_all_records():
    records = load_records()
    print("\n--- All Student Records ---")
    if not records:
        print("No records found.")
        return
    print_table(records)


def search_record():
    query = input("\nEnter Roll No or Name to search: ").strip().lower()
    records = load_records()
    matches = [
        r for r in records
        if query in r["roll_no"].lower() or query in r["name"].lower()
    ]
    if not matches:
        print("No matching records found.")
        return
    print_table(matches)


def update_record():
    roll_no = input("\nEnter Roll No of the record to update: ").strip()
    records = load_records()
    for r in records:
        if r["roll_no"] == roll_no:
            print(f"Current data: {r}")
            name = input(f"New Name [{r['name']}]: ").strip()
            age = input(f"New Age [{r['age']}]: ").strip()
            course = input(f"New Course [{r['course']}]: ").strip()
            marks = input(f"New Marks [{r['marks']}]: ").strip()

            if name:
                r["name"] = name
            if age:
                r["age"] = age
            if course:
                r["course"] = course
            if marks:
                r["marks"] = marks

            save_records(records)
            print("Record updated successfully.")
            return
    print(f"No record found with Roll No '{roll_no}'.")


def delete_record():
    roll_no = input("\nEnter Roll No of the record to delete: ").strip()
    records = load_records()
    filtered = [r for r in records if r["roll_no"] != roll_no]

    if len(filtered) == len(records):
        print(f"No record found with Roll No '{roll_no}'.")
        return

    confirm = input("Are you sure you want to delete this record? (y/n): ").strip().lower()
    if confirm == "y":
        save_records(filtered)
        print("Record deleted successfully.")
    else:
        print("Deletion cancelled.")


# --------------------------------------------------------------------------- #
# Display helper
# --------------------------------------------------------------------------- #
def print_table(records):
    col_widths = {
        "roll_no": max(len(FIELDS[0]), *(len(r["roll_no"]) for r in records)),
        "name": max(len(FIELDS[1]), *(len(r["name"]) for r in records)),
        "age": max(len(FIELDS[2]), *(len(r["age"]) for r in records)),
        "course": max(len(FIELDS[3]), *(len(r["course"]) for r in records)),
        "marks": max(len(FIELDS[4]), *(len(r["marks"]) for r in records)),
    }

    header = (
        f"{FIELDS[0]:<{col_widths['roll_no']}}  "
        f"{FIELDS[1]:<{col_widths['name']}}  "
        f"{FIELDS[2]:<{col_widths['age']}}  "
        f"{FIELDS[3]:<{col_widths['course']}}  "
        f"{FIELDS[4]:<{col_widths['marks']}}"
    )
    print(header)
    print("-" * len(header))

    for r in records:
        print(
            f"{r['roll_no']:<{col_widths['roll_no']}}  "
            f"{r['name']:<{col_widths['name']}}  "
            f"{r['age']:<{col_widths['age']}}  "
            f"{r['course']:<{col_widths['course']}}  "
            f"{r['marks']:<{col_widths['marks']}}"
        )


# --------------------------------------------------------------------------- #
# Menu / main loop
# --------------------------------------------------------------------------- #
MENU = """
==========================================
   STUDENT RECORD MANAGEMENT SYSTEM
==========================================
1. Add Student Record
2. View All Records
3. Search Record
4. Update Record
5. Delete Record
6. Exit
==========================================
"""


def main():
    ensure_data_file()
    while True:
        print(MENU)
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            add_record()
        elif choice == "2":
            view_all_records()
        elif choice == "3":
            search_record()
        elif choice == "4":
            update_record()
        elif choice == "5":
            delete_record()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()