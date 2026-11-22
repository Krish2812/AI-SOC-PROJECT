
import joblib
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

from common import load_events, FEATURES, MODELS, OUTPUTS, ensure_dirs
from detect import apply_rules


def evaluate(name, actual, predicted):
    print(f"\n===== {name} =====")
    print(f"Accuracy:  {accuracy_score(actual, predicted):.4f}")
    print(f"Precision: {precision_score(actual, predicted, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(actual, predicted, zero_division=0):.4f}")
    print(f"F1 Score:  {f1_score(actual, predicted, zero_division=0):.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(actual, predicted))
    print(classification_report(
        actual,
        predicted,
        target_names=["Benign", "Suspicious"],
        zero_division=0
    ))


def main():
    ensure_dirs()

    df = load_events()
    df["actual"] = (
        df["label"].astype(str).str.lower() == "suspicious"
    ).astype(int)

    # Keep training and test events separate.
    train_df, test_df = train_test_split(
        df,
        test_size=0.30,
        random_state=2026,
        stratify=df["actual"]
    )

    # Train Isolation Forest only on benign training events.
    benign_train = train_df[
        train_df["actual"] == 0
    ]

    model = IsolationForest(
        n_estimators=150,
        contamination=0.01,
        random_state=42
    )

    model.fit(benign_train[FEATURES])

    # Evaluate only on unseen test events.
    test = test_df.copy()

    test["ml_anomaly"] = (
        model.predict(test[FEATURES]) == -1
    )

    test["anomaly_score"] = model.decision_function(
        test[FEATURES]
    )

    # Apply the existing fixed detection rules.
    test = apply_rules(test)

    test["ml_prediction"] = test["ml_anomaly"].astype(int)
    test["rule_prediction"] = test["rule_alert"].astype(int)

    test["hybrid_prediction"] = (
        test["ml_anomaly"] | test["rule_alert"]
    ).astype(int)

    actual = test["actual"]

    evaluate("ISOLATION FOREST", actual, test["ml_prediction"])
    evaluate("RULE-BASED DETECTION", actual, test["rule_prediction"])
    evaluate("HYBRID DETECTION", actual, test["hybrid_prediction"])

    # Save predictions for inspection.
    output_columns = [
        "timestamp",
        "host",
        "source_ip",
        "label",
        "actual",
        "ml_anomaly",
        "anomaly_score",
        "rule_alert",
        "rule_reasons",
        "ml_prediction",
        "rule_prediction",
        "hybrid_prediction"
    ]

    output_path = OUTPUTS / "independent_test_results.csv"

    test[output_columns].to_csv(output_path, index=False)

    print("\n===== DATA SPLIT =====")
    print(f"Total events: {len(df)}")
    print(f"Training events: {len(train_df)}")
    print(f"Testing events: {len(test_df)}")
    print(f"Benign training events: {len(benign_train)}")
    print(f"Suspicious test events: {(test['actual'] == 1).sum()}")
    print(f"Benign test events: {(test['actual'] == 0).sum()}")

    print(f"\nIndependent test results saved to: {output_path}")


if __name__ == "__main__":
    main()
