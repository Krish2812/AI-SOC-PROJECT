import joblib
from sklearn.ensemble import IsolationForest
from common import load_events, FEATURES, MODELS, ensure_dirs

def main():
    ensure_dirs()
    df = load_events()
    # Train only on baseline/benign events. Never include the label as a feature.
    baseline = df[df["label"].astype(str).str.lower() == "benign"]
    if len(baseline) < 20:
        raise ValueError("Need at least 20 benign baseline rows to train the demo model.")
    model = IsolationForest(
        n_estimators=150,
        contamination=0.01,
        random_state=42
    )
    model.fit(baseline[FEATURES])
    path = MODELS / "isolation_forest.joblib"
    joblib.dump(model, path)
    print(f"Saved model: {path}")
    print(f"Training baseline rows: {len(baseline)}")

if __name__ == "__main__":
    main()
