import sys
from pathlib import Path
import unittest
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from detect import apply_rules, combine_alerts

class DetectionTests(unittest.TestCase):
    def test_failed_login_rule(self):
        df = pd.DataFrame([{
            "failed_logins": 9, "bytes_out": 0,
            "unique_dst_ports": 1, "process_risk": 0
        }])
        result = apply_rules(df)
        self.assertTrue(bool(result.loc[0, "rule_alert"]))
        self.assertEqual(result.loc[0, "rule_severity"], "High")

    def test_clean_event_no_rule(self):
        df = pd.DataFrame([{
            "failed_logins": 0, "bytes_out": 1000,
            "unique_dst_ports": 1, "process_risk": 0
        }])
        result = apply_rules(df)
        self.assertFalse(bool(result.loc[0, "rule_alert"]))

if __name__ == "__main__":
    unittest.main()
