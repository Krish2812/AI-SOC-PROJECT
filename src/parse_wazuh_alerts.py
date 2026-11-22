"""Starter adapter: convert exported Wazuh alert JSON lines into normalized CSV.

Wazuh alert exports are JSON Lines (one JSON object per line). Field availability
depends on the rules and integrations configured in your lab. Review mappings.
"""
import json
import sys
import pandas as pd
from pathlib import Path

def main(input_path, output_path):
    rows = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            a = json.loads(line)
            data = a.get("data", {})
            agent = a.get("agent", {})
            rows.append({
                "timestamp": a.get("timestamp", ""),
                "host": agent.get("name", "unknown"),
                "source_ip": data.get("srcip", "unknown"),
                "event_type": a.get("rule", {}).get("description", "wazuh_event"),
                "failed_logins": 0,
                "bytes_out": 0,
                "unique_dst_ports": 0,
                "process_risk": 0,
                "label": "unknown"
            })
    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"Wrote {len(rows)} normalized rows to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python src/parse_wazuh_alerts.py input.json output.csv")
    main(sys.argv[1], sys.argv[2])
