"""
GOAL: Predict `sales` (OUTPUT / target / y) using `TV` and `radio`
      advertising spend (INPUT / features / X).
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

os.chdir(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv("advertising.csv", index_col=0)

print("First 5 rows of the dataset:")
print(df.head())
print("\nDataset shape (rows, columns):", df.shape)

X = df[["TV", "radio"]]
y = df["sales"]

print("\nInput features (X) preview:")
print(X.head())
print("\nOutput/target (y) preview:")
print(y.head())

# test_size=0.2  - 20% of rows are held back for testing, 80% for training
# random_state=42 - makes the split reproducible (same split every run)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\nTraining rows: {X_train.shape[0]}")
print(f"Testing rows:  {X_test.shape[0]}")


model = LinearRegression()
model.fit(X_train, y_train)


print("\nLearned relationship:")
print(f"  sales = {model.coef_[0]:.4f} * TV + {model.coef_[1]:.4f} * radio + {model.intercept_:.4f}")

y_pred = model.predict(X_test)

print("\nSample predictions vs actual values:")
comparison = pd.DataFrame({"Actual Sales": y_test.values, "Predicted Sales": y_pred.round(2)})
print(comparison.head(10))

mae = mean_absolute_error(y_test, y_pred)          # avg absolute error, in same units as sales
rmse = np.sqrt(mean_squared_error(y_test, y_pred))  # penalizes big errors more
r2 = r2_score(y_test, y_pred)                       # 0 to 1, how much variance is explained

print("\nModel performance on TEST data:")
print(f"  MAE  (avg error):        {mae:.3f}")
print(f"  RMSE (penalized error):  {rmse:.3f}")
print(f"  R^2  (fit quality 0-1):  {r2:.4f}")

plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred, color="steelblue", edgecolor="k", alpha=0.7)
min_val, max_val = min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())
plt.plot([min_val, max_val], [min_val, max_val], color="red", linestyle="--", label="Perfect prediction")
plt.xlabel("Actual Sales")
plt.ylabel("Predicted Sales")
plt.title("Actual vs Predicted Sales (Linear Regression)")
plt.legend()
plt.tight_layout()
plt.savefig("actual_vs_predicted_sales.png")
plt.close()

print("\nProgram executed")