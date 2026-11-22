
import pandas as pd
from pathlib import Path
from common import load_events

print("=" * 60)
print("          TIME-BASED BRUTE FORCE DETECTION")
print("=" * 60)

# Load security events
df = load_events()

# Convert timestamps into datetime format
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

# Keep only events with failed login attempts
failed_events = df[df["failed_logins"] > 0].copy()

# Sort events by source IP and timestamp
failed_events = failed_events.sort_values(
    ["source_ip", "timestamp"]
)

# Detection configuration
WINDOW = "15min"
THRESHOLD = 10

alert_list = []

# Analyze each IP separately
for ip, ip_events in failed_events.groupby("source_ip"):

    # Set timestamp as index
    ip_events = ip_events.set_index("timestamp")

    # Calculate failed logins in previous 15 minutes
    ip_events["failed_logins_15m"] = (
        ip_events["failed_logins"].rolling(WINDOW).sum()
    )

    # Identify suspicious activity
    suspicious = ip_events[
        ip_events["failed_logins_15m"] >= THRESHOLD
    ].copy()

    if not suspicious.empty:
        suspicious["source_ip"] = ip
        alert_list.append(suspicious.reset_index())

# Combine alerts
if alert_list:

    alerts = pd.concat(alert_list, ignore_index=True)

    alerts["severity"] = "HIGH"

    print("\nBRUTE FORCE ALERTS:")
    print(alerts.to_string(index=False))

else:

    alerts = pd.DataFrame(
        columns=[
            "timestamp",
            "source_ip",
            "failed_logins",
            "failed_logins_15m",
            "severity"
        ]
    )

    print("\nNo brute-force alerts detected.")

# Save results
Path("outputs").mkdir(exist_ok=True)

alerts.to_csv(
    "outputs/bruteforce_alerts.csv",
    index=False
)

print("\nTotal alerts:", len(alerts))
print("Report saved: outputs/bruteforce_alerts.csv")
print("\nDETECTION COMPLETED")
