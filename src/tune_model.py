
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from common import load_events, FEATURES

def main():
    df = load_events()
    df["label"] = df["label"].astype(str).str.lower()

    train_df, test_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["label"]
    )

    baseline = train_df[train_df["label"] == "benign"]
    y_true = (test_df["label"] == "suspicious").astype(int)

    print("\nISOLATION FOREST CONTAMINATION COMPARISON")
    print("-" * 75)
    print(f"{'Contamination':<16}{'Accuracy':<12}{'Precision':<12}{'Recall':<12}{'F1-score'}")

    for contamination in [0.01, 0.02, 0.03, 0.05, 0.08, 0.10]:

        model = IsolationForest(
            n_estimators=150,
            contamination=contamination,
            random_state=42
        )

        model.fit(baseline[FEATURES])

        predictions = model.predict(test_df[FEATURES])
        y_pred = (predictions == -1).astype(int)

        print(
            f"{contamination:<16.2f}"
            f"{accuracy_score(y_true, y_pred):<12.4f}"
            f"{precision_score(y_true, y_pred, zero_division=0):<12.4f}"
            f"{recall_score(y_true, y_pred, zero_division=0):<12.4f}"
            f"{f1_score(y_true, y_pred, zero_division=0):.4f}"
        )

if __name__ == "__main__":
    main()
