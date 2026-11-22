"""Starter adapter for Suricata EVE JSON lines."""
import json
import sys
import pandas as pd

def main(input_path, output_path):
    rows = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get("event_type") not in ("alert", "flow", "dns", "http"):
                continue
            alert = e.get("alert", {})
            rows.append({
                "timestamp": e.get("timestamp", ""),
                "host": e.get("in_iface", "suricata-sensor"),
                "source_ip": e.get("src_ip", "unknown"),
                "event_type": e.get("event_type", "network"),
                "failed_logins": 0,
                "bytes_out": e.get("flow", {}).get("bytes_toserver", 0),
                "unique_dst_ports": 1 if e.get("dest_port") else 0,
                "process_risk": 8 if alert else 0,
                "label": "unknown"
            })
    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"Wrote {len(rows)} normalized rows to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python src/parse_suricata_eve.py eve.json output.csv")
    main(sys.argv[1], sys.argv[2])
