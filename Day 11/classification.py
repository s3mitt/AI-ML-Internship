"""
==============================================================
 CLASSIFICATION DEMO: Logistic Regression vs Decision Tree
==============================================================
Goal   : Predict whether a tumor is MALIGNANT (0) or BENIGN (1)
         using two classification algorithms, then compare
         their accuracy.

INPUT  : 30 numeric features per sample (X) + known label (y)
OUTPUT : Predicted label (0/1) for unseen samples + accuracy score

Run this in VS Code:
    1. Make sure Python is installed.
    2. Install required libraries (only once):
         pip install scikit-learn pandas matplotlib
    3. Run:  python classification_compare.py
==============================================================
"""

# ---------- STEP 1: Import required libraries ----------
import pandas as pd                                   # for handling tabular data
from sklearn.datasets import load_breast_cancer        # sample dataset (built into sklearn)
from sklearn.model_selection import train_test_split   # to split data into train/test
from sklearn.linear_model import LogisticRegression    # Model 1
from sklearn.tree import DecisionTreeClassifier         # Model 2
from sklearn.preprocessing import StandardScaler        # to scale features
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ---------- STEP 2: Load the dataset ----------
# This is a built-in dataset, so no need to download any CSV file.
# X = features (measurements), y = target (0 = malignant, 1 = benign)
data = load_breast_cancer()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = pd.Series(data.target, name="target")

print("STEP 2: Dataset Loaded")
print("Shape of X (rows, columns):", X.shape)
print("Class distribution:\n", y.value_counts())
print("-" * 60)

# ---------- STEP 3: Split data into Training set and Test set ----------
# 80% of data used to TRAIN the model, 20% held back to TEST it.
# random_state=42 makes the split reproducible (same result every run).
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y          # keeps class proportions similar in train & test
)

print("STEP 3: Data Split")
print("Training samples:", X_train.shape[0])
print("Testing samples :", X_test.shape[0])
print("-" * 60)

# ---------- STEP 4: Feature Scaling (needed for Logistic Regression) ----------
# Logistic Regression works better when all features are on a similar scale.
# Decision Trees do NOT need scaling, so we scale a separate copy for it.
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # learn scale from training data
X_test_scaled = scaler.transform(X_test)         # apply same scale to test data

print("STEP 4: Features Scaled (for Logistic Regression)")
print("-" * 60)

# ---------- STEP 5: Train Logistic Regression Model ----------
log_reg = LogisticRegression(max_iter=5000, random_state=42)
log_reg.fit(X_train_scaled, y_train)             # TRAINING happens here
y_pred_log = log_reg.predict(X_test_scaled)      # PREDICTION on unseen test data

acc_log = accuracy_score(y_test, y_pred_log)

print("STEP 5: Logistic Regression Trained")
print(f"Logistic Regression Accuracy: {acc_log:.4f} ({acc_log*100:.2f}%)")
print("-" * 60)

# ---------- STEP 6: Train Decision Tree Model ----------
tree = DecisionTreeClassifier(random_state=42)
tree.fit(X_train, y_train)                       # TRAINING happens here (no scaling needed)
y_pred_tree = tree.predict(X_test)               # PREDICTION on unseen test data

acc_tree = accuracy_score(y_test, y_pred_tree)

print("STEP 6: Decision Tree Trained")
print(f"Decision Tree Accuracy: {acc_tree:.4f} ({acc_tree*100:.2f}%)")
print("-" * 60)

# ---------- STEP 7: Compare Both Models ----------
print("STEP 7: MODEL COMPARISON")
print(f"{'Model':<25}{'Accuracy':<10}")
print(f"{'Logistic Regression':<25}{acc_log:.4f}")
print(f"{'Decision Tree':<25}{acc_tree:.4f}")
print("-" * 60)

if acc_log > acc_tree:
    print("Result: Logistic Regression performed BETTER on this dataset.")
elif acc_tree > acc_log:
    print("Result: Decision Tree performed BETTER on this dataset.")
else:
    print("Result: Both models performed EQUALLY well.")
print("-" * 60)

# ---------- STEP 8: Detailed Reports (optional, good for presentation) ----------
print("\nDetailed Report - Logistic Regression:")
print(classification_report(y_test, y_pred_log, target_names=data.target_names))

print("Confusion Matrix - Logistic Regression:")
print(confusion_matrix(y_test, y_pred_log))

print("\nDetailed Report - Decision Tree:")
print(classification_report(y_test, y_pred_tree, target_names=data.target_names))

print("Confusion Matrix - Decision Tree:")
print(confusion_matrix(y_test, y_pred_tree))

# ---------- STEP 9: Try predicting on ONE new sample (demo for presentation) ----------
sample = X_test.iloc[[0]]                 # take the first test row as an example
sample_scaled = scaler.transform(sample)  # scale it the same way as training data

pred_log_single = log_reg.predict(sample_scaled)[0]
pred_tree_single = tree.predict(sample)[0]
actual_label = y_test.iloc[0]

print("\nSTEP 9: Single Sample Prediction Demo")
print("Actual label       :", data.target_names[actual_label])
print("Logistic Regression predicted:", data.target_names[pred_log_single])
print("Decision Tree predicted      :", data.target_names[pred_tree_single])