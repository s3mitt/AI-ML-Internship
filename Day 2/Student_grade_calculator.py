"""
Student Grade Calculator
-------------------------
Takes marks for a number of subjects, calculates the total,
average percentage, and assigns a letter grade.
"""


def get_marks():
    """Ask the user how many subjects and collect marks for each."""
    while True:
        try:
            num_subjects = int(input("Enter number of subjects: "))
            if num_subjects <= 0:
                print("Please enter a number greater than 0.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    marks = []
    for i in range(1, num_subjects + 1):
        while True:
            try:
                mark = float(input(f"Enter marks for subject {i} (out of 100): "))
                if mark < 0 or mark > 100:
                    print("Marks must be between 0 and 100.")
                    continue
                marks.append(mark)
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

    return marks


def calculate_total(marks):
    """Return the sum of all marks."""
    return sum(marks)


def calculate_average(marks):
    """Return the average percentage."""
    return calculate_total(marks) / len(marks)


def get_grade(average):
    """Return a letter grade based on the average percentage."""
    if average >= 90:
        return "A+"
    elif average >= 80:
        return "A"
    elif average >= 70:
        return "B"
    elif average >= 60:
        return "C"
    elif average >= 50:
        return "D"
    else:
        return "F"


def display_result(marks, total, average, grade):
    """Print a neat summary of the results."""
    print("\n----- Grade Report -----")
    for i, mark in enumerate(marks, start=1):
        print(f"Subject {i}: {mark}")
    print("-------------------------")
    print(f"Total Marks : {total}/{len(marks) * 100}")
    print(f"Average     : {average:.2f}%")
    print(f"Grade       : {grade}")
    print("-------------------------")


def main():
    print("=== Student Grade Calculator ===\n")
    name = input("Enter student name: ")
    marks = get_marks()

    total = calculate_total(marks)
    average = calculate_average(marks)
    grade = get_grade(average)

    print(f"\nResult for {name}:")
    display_result(marks, total, average, grade)


if __name__ == "__main__":
    main()