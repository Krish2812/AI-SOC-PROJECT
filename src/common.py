from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
MODELS = ROOT / "models"
FEATURES = ["failed_logins", "bytes_out", "unique_dst_ports", "process_risk"]

def ensure_dirs():
    OUTPUTS.mkdir(exist_ok=True)
    MODELS.mkdir(exist_ok=True)

def load_events(path=None):
    path = path or DATA / "sample_events.csv"
    df = pd.read_csv(path)
    required = ["timestamp", "host", "source_ip", "event_type", *FEATURES]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    return df
