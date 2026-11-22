
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from common import load_events, FEATURES, MODELS
from detect import apply_rules, combine_alerts
import joblib


def evaluate(name, actual, predicted):

    print(f"\n===== {name} =====")

    print(f"Accuracy:  {accuracy_score(actual, predicted):.4f}")
    print(f"Precision: {precision_score(actual, predicted, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(actual, predicted, zero_division=0):.4f}")
    print(f"F1-score:  {f1_score(actual, predicted, zero_division=0):.4f}")

    cm = confusion_matrix(actual, predicted, labels=[0, 1])

    print("\nConfusion Matrix:")
    print(cm)
    print("Rows: Actual [Benign, Suspicious]")
    print("Columns: Predicted [Benign, Suspicious]")


def main():

    print("\n===== AI-SOC HYBRID EVALUATION =====")

    df = load_events()

    df["label"] = df["label"].astype(str).str.strip().str.lower()

    df = df[df["label"].isin(["benign", "suspicious"])].copy()

    y_true = (df["label"] == "suspicious").astype(int)

    # Load the existing trained Isolation Forest model
    model_path = MODELS / "isolation_forest.joblib"
    model = joblib.load(model_path)

    # Generate ML predictions
    df["ml_anomaly"] = model.predict(df[FEATURES]) == -1

    # Generate rule predictions
    df = apply_rules(df)

    # Generate hybrid predictions
    df = combine_alerts(df)

    # Convert predictions to binary values
    ml_pred = df["ml_anomaly"].astype(int)
    rule_pred = df["rule_alert"].astype(int)
    hybrid_pred = df["alert"].astype(int)

    # Evaluate all three systems
    evaluate("ISOLATION FOREST", y_true, ml_pred)
    evaluate("RULE-BASED DETECTION", y_true, rule_pred)
    evaluate("HYBRID DETECTION", y_true, hybrid_pred)

    # Save comparison results
    df.to_csv("outputs/hybrid_evaluation_results.csv", index=False)

    print("\nSaved: outputs/hybrid_evaluation_results.csv")
    print("\n===== EVALUATION COMPLETED =====")


if __name__ == "__main__":
    main()
