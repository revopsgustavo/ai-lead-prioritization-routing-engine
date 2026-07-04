from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "processed"

REQUIRED = {
    "leads": ["lead_id", "account_id", "channel", "created_date", "priority_tier"],
    "lead_scores": ["lead_id", "icp_fit_score", "intent_score", "lead_score"],
    "routing_decisions": ["lead_id", "sdr_id", "rule_id", "priority_tier"],
    "conversion_outcomes": ["lead_id", "conversion_status", "is_mql", "is_sql", "is_opportunity"],
    "sdrs": ["sdr_id", "sdr_name", "daily_capacity"],
    "sla_events": ["lead_id", "sla_status", "response_time_hours"],
}


def check(condition: bool, check_name: str, table: str, severity: str, detail: str):
    return {"check_name": check_name, "table": table, "status": "pass" if condition else "fail", "severity": severity, "detail": detail}


def validate() -> pd.DataFrame:
    rows = []
    loaded = {}
    for table, columns in REQUIRED.items():
        path = DATA_DIR / f"{table}.csv"
        exists = path.exists()
        rows.append(check(exists, "file_exists", table, "critical", str(path)))
        if not exists:
            continue
        df = pd.read_csv(path)
        loaded[table] = df
        for column in columns:
            rows.append(check(column in df.columns, "required_column_exists", table, "critical", column))
        if columns[0] in df.columns:
            rows.append(check(df[columns[0]].notna().all(), "primary_id_not_null", table, "critical", columns[0]))
    leads = loaded.get("leads", pd.DataFrame())
    if not leads.empty:
        rows.append(check(leads["lead_id"].notna().all(), "leads_have_lead_id", "leads", "critical", "lead_id"))
        rows.append(check(leads["channel"].notna().all(), "leads_have_channel", "leads", "high", "channel"))
        rows.append(check(pd.to_datetime(leads["created_date"], errors="coerce").notna().all(), "valid_created_date", "leads", "high", "created_date"))
    scores = loaded.get("lead_scores", pd.DataFrame())
    if not scores.empty:
        for column in ["icp_fit_score", "intent_score", "lead_score"]:
            rows.append(check(scores[column].between(0, 100).all(), "scores_between_0_100", "lead_scores", "high", column))
        rows.append(check(set(leads.get("lead_id", [])) <= set(scores["lead_id"]), "leads_without_score", "lead_scores", "high", "all leads should have score"))
    sla = loaded.get("sla_events", pd.DataFrame())
    if not sla.empty:
        rows.append(check(sla["sla_status"].isin(["met", "breached"]).all(), "valid_sla_status", "sla_events", "high", "met/breached"))
    rd = loaded.get("routing_decisions", pd.DataFrame())
    if not rd.empty:
        rows.append(check(rd["sdr_id"].notna().all(), "routing_decisions_without_sdr_id", "routing_decisions", "medium", f"{int(rd['sdr_id'].isna().sum())} null sdr_id"))
    co = loaded.get("conversion_outcomes", pd.DataFrame())
    if not co.empty:
        rows.append(check(co["conversion_status"].notna().all(), "conversion_outcomes_without_status", "conversion_outcomes", "critical", "conversion_status"))
    return pd.DataFrame(rows)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    report = validate()
    report.to_csv(DATA_DIR / "data_quality_report.csv", index=False)
    print(f"Generated data quality report with {len(report)} checks")


if __name__ == "__main__":
    main()
