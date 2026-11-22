# AI-SOC: Intelligent Threat Detection and Network Security Monitoring

A beginner-friendly defensive SOC lab starter project for Windows + VirtualBox.

## What this starter kit does
- Reads normalized endpoint/network security events from CSV.
- Detects repeated failed logins, unusual outbound data, high destination-port counts, and suspicious process activity.
- Trains an Isolation Forest model on baseline/benign activity.
- Combines rule-based and ML signals into prioritized alerts.
- Displays events and alerts in a Streamlit dashboard.
- Includes synthetic sample data so the pipeline works before Wazuh/Sysmon/Suricata are installed.

> Safety: run attack simulations only in your own isolated VirtualBox lab. Do not scan or test systems you do not own or have written permission to assess. The included dataset is synthetic and does not contain real credentials or malware.

## 1. Requirements
- Windows 10/11 host
- VirtualBox
- Python 3.10 or 3.11
- VS Code (recommended)
- At least 8 GB RAM recommended; 16 GB is more comfortable for multiple VMs.

## 2. Install on Windows
Open PowerShell in this folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Run the starter pipeline
```powershell
python src\train_model.py
python src\run_detection.py
streamlit run src\dashboard.py
```
Open the local URL printed by Streamlit (usually http://localhost:8501).

## 4. Normalized event schema
`data/sample_events.csv` uses these fields:

| Field | Meaning |
|---|---|
| timestamp | ISO-8601 event time |
| host | Host that generated the event |
| source_ip | Source IP observed in the lab |
| event_type | login, network, process |
| failed_logins | Failed login count in the time window |
| bytes_out | Outbound bytes in the time window |
| unique_dst_ports | Number of distinct destination ports |
| process_risk | Simple process-risk score from 0 to 10 |
| label | Synthetic ground-truth label: benign or suspicious |

The `label` field is for evaluating the synthetic example only. Do not use it as an input feature when training the model.

## 5. Architecture and integration phases

### Phase A — working prototype (start here)
Synthetic CSV -> Python feature processing -> rules + Isolation Forest -> alerts CSV -> Streamlit dashboard.

### Phase B — endpoint telemetry
1. Install Sysmon on a Windows VM.
2. Collect Windows event logs in the VM.
3. Configure Wazuh agent on the Windows VM and Wazuh manager in an Ubuntu VM (or use the official all-in-one quickstart on a suitably resourced Ubuntu VM).
4. Export Wazuh alerts as JSON.
5. Map relevant fields into the normalized schema.

### Phase C — network telemetry
1. Put Ubuntu sensor and test VM on a VirtualBox Host-only or Internal Network.
2. Install Suricata on the Ubuntu sensor.
3. Enable EVE JSON output.
4. Parse `eve.json` into the normalized event schema.
5. Re-run detection and review correlated alerts.

Do not expose management interfaces to the public internet. Use host-only/internal networking for lab traffic.

## 6. Suggested VirtualBox layout
- Ubuntu SOC VM: 4 vCPU, 4–6 GB RAM, 40 GB disk (more if running Wazuh all-in-one).
- Windows test VM: 2 vCPU, 4 GB RAM, 40 GB disk.
- Optional second Ubuntu VM: 2 vCPU, 2 GB RAM.
- Network: Host-only or Internal Network for isolated testing. Use NAT only when downloading updates, then disconnect if not needed.

Wazuh all-in-one can be resource-heavy. If your laptop has only 8 GB RAM, first run the Python prototype and add VMs one at a time.

## 7. Testing
```powershell
python -m unittest discover -s tests -v
```

Test the included sample:
- `suspicious` rows should trigger one or more rules and/or ML anomaly flags.
- Benign rows should generally have fewer alerts.
- Review false positives; a high anomaly score is not proof of compromise.

## 8. Research evaluation
Compare:
1. Rule-only detection
2. ML-only anomaly detection
3. Hybrid rule + ML detection

Report:
- Precision, recall, F1-score
- False-positive rate
- Detection latency
- CPU/RAM use
- Confusion matrix

Use a labelled, documented dataset such as CIC-IDS2017 or UNSW-NB15 for offline experiments. Check each dataset's licence and citation requirements. Keep training/test splits separate and avoid data leakage.

## 9. GitHub checklist
- Add architecture diagram and screenshots.
- Explain your lab topology and VM network mode.
- Include dataset source and citation.
- Include setup commands and reproducibility steps.
- Document at least three controlled lab scenarios.
- Never upload passwords, API keys, private IP details you want to keep private, or raw sensitive logs.

## Disclaimer
This is an educational prototype, not a production SIEM or automated response system. Validate alerts manually before taking action.

## Day 2 – Security Detection Modules

### 1. Security Event Analysis
Analyzes security events using Python and Pandas.

### 2. Suspicious IP Detection
Groups events by source IP and calculates:
- Total failed login attempts
- Maximum failed logins in one event
- Total number of events

### 3. Brute-Force Detection
Uses timestamp-based rolling window analysis.

Detection configuration:
- Time window: 15 minutes
- Threshold: 10 failed logins
- Severity: HIGH

### 4. Generated Reports

| Report | Description |
|---|---|
| alerts.csv | Security detection alerts |
| suspicious_ips.csv | Suspicious IP report |
| bruteforce_alerts.csv | Time-based brute-force alerts |

### 5. Validation Results

- Total brute-force alert records: 20
- Suspicious source IPs: 2
- Alert threshold validation: Passed

### Technologies Used
- Python 3.10
- Pandas
- Scikit-learn
- Streamlit
- CSV
- Machine Learning
