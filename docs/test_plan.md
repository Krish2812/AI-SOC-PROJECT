# Test plan

Run only inside your own isolated VirtualBox lab.

| Scenario | Safe simulation | Expected observation |
|---|---|---|
| Repeated login failures | Use a deliberately incorrect password against a test VM account a few times | Windows/Linux authentication failure events; rule should flag high counts |
| Port discovery | Run a limited scan against your own host-only test VM | Suricata/connection events; review destination-port count |
| Large outbound transfer | Copy a harmless test file between two lab VMs | Flow bytes increase; adjust threshold to your baseline |
| Suspicious process indicator | Use a harmless local script/process and create a test event record | Process event appears; analyst reviews context |

For reproducibility, document date/time, VM IPs (private lab only), command, logs observed, alert generated, and whether it was a true/false positive. Avoid destructive payloads and real malware.
