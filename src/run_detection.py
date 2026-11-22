import joblib
from common import load_events, FEATURES, MODELS, OUTPUTS, ensure_dirs
from detect import apply_rules, combine_alerts

def main():
    ensure_dirs()
    model_path = MODELS / "isolation_forest.joblib"
    if not model_path.exists():
        raise FileNotFoundError("Model not found. Run: python src/train_model.py")
    df = load_events()
    model = joblib.load(model_path)
    # IsolationForest returns -1 for anomaly and +1 for inlier.
    df["ml_anomaly"] = model.predict(df[FEATURES]) == -1
    df["anomaly_score"] = model.decision_function(df[FEATURES])
    df = apply_rules(df)
    df = combine_alerts(df)
    out = OUTPUTS / "alerts.csv"
    df.to_csv(out, index=False)
    print(f"Processed {len(df)} events.")
    print(f"Alerts: {int(df['alert'].sum())}")
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
