
from common import load_events

# Load security event dataset
df = load_events()

print("=" * 50)
print("       AI-SOC SECURITY EVENT ANALYSIS")
print("=" * 50)

# 1. Total events
print("\nTOTAL SECURITY EVENTS:")
print(len(df))

# 2. Event type analysis
print("\nEVENT TYPE DISTRIBUTION:")
print(df["event_type"].value_counts())

# 3. Failed login analysis
print("\nFAILED LOGIN STATISTICS:")
print(df["failed_logins"].describe())

# 4. Suspicious event analysis
print("\nSUSPICIOUS EVENTS:")
suspicious = df[df["label"] == "suspicious"]

print(suspicious[
    ["timestamp", "host", "source_ip", "failed_logins"]
].to_string(index=False))

# 5. Source IP analysis
print("\nSOURCE IP DISTRIBUTION:")
print(df["source_ip"].value_counts())

print("\nANALYSIS COMPLETED")
