
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score,precision_score,recall_score,f1_score,confusion_matrix,ConfusionMatrixDisplay)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams["figure.dpi"] = 120

data = load_breast_cancer()
X = pd.DataFrame(data.data, columns=data.feature_names)
y = pd.Series(data.target, name="target")   # 0 = malignant, 1 = benign

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

log_reg = LogisticRegression(max_iter=5000, random_state=42)
log_reg.fit(X_train_scaled, y_train)
y_pred_log = log_reg.predict(X_test_scaled)

tree = DecisionTreeClassifier(random_state=42)
tree.fit(X_train, y_train)
y_pred_tree = tree.predict(X_test)

def evaluate_model(name, y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, pos_label=0)   # precision for "malignant"
    rec = recall_score(y_true, y_pred, pos_label=0)        # recall for "malignant"
    f1 = f1_score(y_true, y_pred, pos_label=0)             # F1 for "malignant"

    print(f"\n{'='*55}")
    print(f"Evaluation Metrics: {name}")
    print(f"{'='*55}")
    print(f"Accuracy  : {acc:.4f}  ({acc*100:.2f}%)")
    print(f"Precision : {prec:.4f}  (of predicted malignant, % actually malignant)")
    print(f"Recall    : {rec:.4f}  (of actual malignant, % correctly caught)")
    print(f"F1 Score  : {f1:.4f}  (balance of precision & recall)")

    return {"model": name, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1}

results_log = evaluate_model("Logistic Regression", y_test, y_pred_log)
results_tree = evaluate_model("Decision Tree", y_test, y_pred_tree)

summary_df = pd.DataFrame([results_log, results_tree])
print(f"\n{'='*55}")
print("SUMMARY TABLE")
print(f"{'='*55}")
print(summary_df.to_string(index=False))

cm_log = confusion_matrix(y_test, y_pred_log)
cm_tree = confusion_matrix(y_test, y_pred_tree)

print(f"\nConfusion Matrix - Logistic Regression:\n{cm_log}")
print(f"\nConfusion Matrix - Decision Tree:\n{cm_tree}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

disp_log = ConfusionMatrixDisplay(confusion_matrix=cm_log, display_labels=data.target_names)
disp_log.plot(ax=axes[0], cmap="Blues", colorbar=False)
axes[0].set_title("Logistic Regression")

disp_tree = ConfusionMatrixDisplay(confusion_matrix=cm_tree, display_labels=data.target_names)
disp_tree.plot(ax=axes[1], cmap="Oranges", colorbar=False)
axes[1].set_title("Decision Tree")

plt.suptitle("Confusion Matrices: Logistic Regression vs Decision Tree")
plt.tight_layout()
plt.savefig("confusion_matrices.png")   # save BEFORE plt.show()
print("\nSaved chart: 'confusion_matrices.png'")
plt.close()

metrics_names = ["accuracy", "precision", "recall", "f1"]
x = range(len(metrics_names))
width = 0.35

plt.figure(figsize=(8, 5))
plt.bar([i - width/2 for i in x], summary_df.loc[0, metrics_names], width, label="Logistic Regression", color="#4C72B0")
plt.bar([i + width/2 for i in x], summary_df.loc[1, metrics_names], width, label="Decision Tree", color="#DD8452")
plt.xticks(list(x), [m.capitalize() for m in metrics_names])
plt.ylim(0, 1.05)
plt.ylabel("Score")
plt.title("All Metrics Comparison (positive class = malignant)")
plt.legend()
plt.tight_layout()
plt.savefig("all_metrics_comparison.png")
print("Saved chart: 'all_metrics_comparison.png'")
plt.close()