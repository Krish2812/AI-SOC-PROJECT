
from common import load_events

# Load security events
df = load_events()

print("=" * 55)
print("          SUSPICIOUS IP DETECTION")
print("=" * 55)

# Group events by source IP
ip_analysis = df.groupby("source_ip").agg(
    total_events=("source_ip", "count"),
    total_failed_logins=("failed_logins", "sum"),
    maximum_failed_logins=("failed_logins", "max")
)

suspicious_ips = ip_analysis[
    (ip_analysis["total_failed_logins"] >= 100) |
    (ip_analysis["maximum_failed_logins"] >= 8)
]

print("\nCOMPLETE IP ANALYSIS:")
print(ip_analysis.to_string())

print("\nSUSPICIOUS IP ADDRESSES:")
print(suspicious_ips.to_string())

# Save suspicious IP report
suspicious_ips.reset_index().to_csv(
    "outputs/suspicious_ips.csv",
    index=False
)

print("\nSuspicious IP report saved successfully!")

print("\nDETECTION COMPLETED")
