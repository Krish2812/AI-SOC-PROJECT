
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from common import load_events, FEATURES

def main():

    print("\n===== AI-SOC MODEL EVALUATION =====\n")

    # Load dataset
    df = load_events()

    # Normalize actual labels
    df["label"] = df["label"].astype(str).str.strip().str.lower()

    # Keep only valid labels
    df = df[df["label"].isin(["benign", "suspicious"])].copy()

    if df["label"].nunique() != 2:
        raise ValueError("Dataset must contain benign and suspicious labels.")

    print("Dataset distribution:")
    print(df["label"].value_counts())
    
    # Convert labels: suspicious = 1, benign = 0
    df["actual"] = (df["label"] == "suspicious").astype(int)

    # Split dataset into training and testing
    train_df, test_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["label"]
    )

    # Train only on benign training events
    baseline = train_df[train_df["label"] == "benign"]

    model = IsolationForest(
        n_estimators=150,
        contamination=0.05,
        random_state=42
    )

    model.fit(baseline[FEATURES])

    # Predict anomalies on unseen test data
    predictions = model.predict(test_df[FEATURES])

    # Convert -1 (anomaly) to 1 and +1 (normal) to 0
    y_pred = (predictions == -1).astype(int)
    y_true = test_df["actual"]

    # Calculate metrics
    print("\n===== EVALUATION METRICS =====")

    print(f"Accuracy:  {accuracy_score(y_true, y_pred):.4f}")
    print(f"Precision: {precision_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"F1-score:  {f1_score(y_true, y_pred, zero_division=0):.4f}")

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])

    print("\n===== CONFUSION MATRIX =====")
    print("Rows = Actual, Columns = Predicted")
    print("                 Predicted Benign  Predicted Suspicious")
    print(f"Actual Benign          {cm[0][0]:<10} {cm[0][1]}")
    print(f"Actual Suspicious      {cm[1][0]:<10} {cm[1][1]}")

    print("\n===== CLASSIFICATION REPORT =====")
    print(classification_report(
        y_true,
        y_pred,
        labels=[0, 1],
        target_names=["Benign", "Suspicious"],
        zero_division=0
    ))

    # Save test predictions
    results = test_df.copy()
    results["predicted"] = [
        "Suspicious" if value == 1 else "Benign"
        for value in y_pred
    ]

    output_path = "outputs/model_evaluation_results.csv"
    results.to_csv(output_path, index=False)

    print(f"\nEvaluation results saved to: {output_path}")
    print("\n===== EVALUATION COMPLETED =====")


if __name__ == "__main__":
    main()
