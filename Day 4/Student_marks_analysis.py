import numpy as np

# 1. Dataset Setup
students = np.array(["Alice", "Bob", "Charlie", "Diana", "Evan"])
subjects = np.array(["Math", "Physics", "Chemistry", "English"])

# Shape: (5 students, 4 subjects)
marks = np.array([
    [85, 78, 92, 88],  # Alice
    [70, 65, 58, 74],  # Bob
    [95, 89, 94, 91],  # Charlie
    [60, 52, 64, 59],  # Diana
    [78, 81, 79, 85]   # Evan
])

# 2. Student-wise Computations (axis=1: across columns)
total_per_student = np.sum(marks, axis=1)
avg_per_student = np.mean(marks, axis=1)

# 3. Subject-wise Computations (axis=0: across rows)
avg_per_subject = np.mean(marks, axis=0)
max_per_subject = np.max(marks, axis=0)
min_per_subject = np.min(marks, axis=0)

# 4. Top Performer
top_student_idx = np.argmax(total_per_student)
top_student = students[top_student_idx]

# 5. Grading & Filtering
# Passing threshold: average >= 60 and no subject < 55
all_passed_subjects = np.all(marks >= 55, axis=1)
passed_students = students[(avg_per_student >= 60) & all_passed_subjects]

# Display Results
print("--- Overall Student Performance ---")
for name, total, avg in zip(students, total_per_student, avg_per_student):
    print(f"{name:<8} | Total: {total:<3} | Average: {avg:.2f}")

print("\n--- Subject Breakdown ---")
for subj, mean_val, high, low in zip(subjects, avg_per_subject, max_per_subject, min_per_subject):
    print(f"{subj:<10} | Mean: {mean_val:.1f} | Highest: {high:<2} | Lowest: {low:<2}")

print(f"\nTop Scorer: {top_student} ({total_per_student[top_student_idx]} marks)")
print(f"Passed All Criteria: {', '.join(passed_students)}")