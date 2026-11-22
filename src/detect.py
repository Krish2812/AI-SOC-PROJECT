import pandas as pd
from common import FEATURES

def apply_rules(df: pd.DataFrame) -> pd.DataFrame:
    """Apply transparent, explainable starter detection rules."""
    out = df.copy()
    reasons = []
    severities = []
    for _, row in out.iterrows():
        hits = []
        severity = "Low"
        if row["failed_logins"] >= 8:
            hits.append("Repeated failed logins (>=8)")
            severity = "High"
        elif row["failed_logins"] >= 4:
            hits.append("Several failed logins (>=4)")
            severity = "Medium"
        if row["bytes_out"] >= 5_000_000:
            hits.append("Unusually high outbound data (>=5 MB)")
            severity = "High"
        if row["unique_dst_ports"] >= 20:
            hits.append("High destination-port diversity (>=20)")
            severity = "High"
        elif row["unique_dst_ports"] >= 10 and severity == "Low":
            hits.append("Elevated destination-port diversity (>=10)")
            severity = "Medium"
        if row["process_risk"] >= 8:
            hits.append("High-risk process indicator (score >=8)")
            severity = "High"
        elif row["process_risk"] >= 5 and severity == "Low":
            hits.append("Moderate process-risk indicator (score >=5)")
            severity = "Medium"
        reasons.append("; ".join(hits) if hits else "")
        severities.append(severity if hits else "Informational")
    out["rule_reasons"] = reasons
    out["rule_severity"] = severities
    out["rule_alert"] = out["rule_reasons"].ne("")
    return out

def combine_alerts(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ml = out.get("ml_anomaly", pd.Series(False, index=out.index)).fillna(False).astype(bool)
    rule = out["rule_alert"].astype(bool)
    out["alert"] = rule | ml
    out["alert_source"] = [
        "Rule + ML" if r and m else "Rule" if r else "ML" if m else "None"
        for r, m in zip(rule, ml)
    ]
    def priority(row):
        if row["rule_severity"] == "High":
            return "High"
        if row["rule_severity"] == "Medium":
            return "Medium"
        if row["ml_anomaly"]:
            return "Review"
        return "Informational"
    out["priority"] = out.apply(priority, axis=1)
    out["investigation_note"] = out.apply(
        lambda r: r["rule_reasons"] or (
            "ML model flagged an unusual combination of activity; investigate context."
            if r["ml_anomaly"] else "No detection rule matched."
        ), axis=1
    )
    return out
