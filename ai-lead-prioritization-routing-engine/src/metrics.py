from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "processed"


def load_table(name: str) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def load_case_data() -> dict[str, pd.DataFrame]:
    return {name: load_table(name) for name in [
        "leads", "accounts", "channels", "campaigns", "sdrs", "routing_rules",
        "lead_activity", "sla_events", "lead_scores", "routing_decisions", "conversion_outcomes"
    ]}


def safe_rate(numerator: float, denominator: float) -> float:
    return 0.0 if denominator in (0, None) or pd.isna(denominator) else float(numerator) / float(denominator)


def base_frame(data: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    data = data or load_case_data()
    leads = data["leads"].copy()
    for table in ["lead_scores", "routing_decisions", "sla_events", "conversion_outcomes"]:
        df = data[table].copy()
        if not df.empty and "lead_id" in df.columns:
            suffix = f"_{table}"
            leads = leads.merge(df, on="lead_id", how="left", suffixes=("", suffix))
    if "sdr_id_routing_decisions" in leads.columns and "sdr_id" not in leads.columns:
        leads = leads.rename(columns={"sdr_id_routing_decisions": "sdr_id"})
    return leads


def total_leads(data=None): return int(len((data or load_case_data())["leads"]))
def total_mqls(data=None): return int((data or load_case_data())["conversion_outcomes"].get("is_mql", pd.Series(dtype=int)).sum())
def total_sqls(data=None): return int((data or load_case_data())["conversion_outcomes"].get("is_sql", pd.Series(dtype=int)).sum())
def average_lead_score(data=None): return float((data or load_case_data())["lead_scores"]["lead_score"].mean())
def average_icp_fit_score(data=None): return float((data or load_case_data())["lead_scores"]["icp_fit_score"].mean())
def average_intent_score(data=None): return float((data or load_case_data())["lead_scores"]["intent_score"].mean())


def priority_tier_distribution(data=None):
    return (data or load_case_data())["leads"]["priority_tier"].value_counts(normalize=True).sort_index()


def average_response_time_hours(data=None):
    return float((data or load_case_data())["sla_events"]["response_time_hours"].mean())


def median_response_time_hours(data=None):
    return float((data or load_case_data())["sla_events"]["response_time_hours"].median())


def sla_compliance_rate(data=None):
    sla = (data or load_case_data())["sla_events"]
    return safe_rate((sla["sla_status"] == "met").sum(), len(sla))


def sla_breach_rate(data=None):
    return 1.0 - sla_compliance_rate(data)


def mql_to_sql_conversion(data=None):
    co = (data or load_case_data())["conversion_outcomes"]
    return safe_rate(co["is_sql"].sum(), co["is_mql"].sum())


def sql_to_opportunity_conversion(data=None):
    co = (data or load_case_data())["conversion_outcomes"]
    return safe_rate(co["is_opportunity"].sum(), co["is_sql"].sum())


def conversion_by_score_band(data=None):
    df = base_frame(data)
    return df.groupby("score_band", dropna=False).agg(leads=("lead_id", "count"), sql_rate=("is_sql", "mean"), opportunity_rate=("is_opportunity", "mean")).reset_index()


def routing_load_by_sdr(data=None):
    df = base_frame(data)
    return df.groupby("sdr_id", dropna=False).agg(assigned_leads=("lead_id", "count")).reset_index().sort_values("assigned_leads", ascending=False)


def accepted_leads_by_sdr(data=None):
    df = base_frame(data)
    return df[df["is_mql"] == 1].groupby("sdr_id").size().reset_index(name="accepted_leads")


def disqualified_leads(data=None):
    co = (data or load_case_data())["conversion_outcomes"]
    return int((co["conversion_status"] == "disqualified").sum())


def leads_without_owner(data=None):
    rd = (data or load_case_data())["routing_decisions"]
    return int(rd["sdr_id"].isna().sum())


def high_priority_delayed_leads(data=None):
    df = base_frame(data)
    return int(((df["priority_tier"] == "p1") & (df["response_time_hours"] > df["sla_target_hours"])).sum())


def conversion_by_channel(data=None):
    df = base_frame(data)
    return df.groupby("channel").agg(leads=("lead_id", "count"), sql_rate=("is_sql", "mean"), opportunity_rate=("is_opportunity", "mean")).reset_index()


def conversion_by_sdr(data=None):
    df = base_frame(data)
    return df.groupby("sdr_id", dropna=False).agg(leads=("lead_id", "count"), sql_rate=("is_sql", "mean"), opportunity_rate=("is_opportunity", "mean")).reset_index()


def backlog_by_sdr(data=None):
    df = base_frame(data)
    return df[df["sla_status"] == "breached"].groupby("sdr_id", dropna=False).size().reset_index(name="backlog_risk")


def lead_quality_by_channel(data=None):
    df = base_frame(data)
    return df.groupby("channel").agg(leads=("lead_id", "count"), avg_score=("lead_score", "mean"), avg_fit=("icp_fit_score", "mean"), avg_intent=("intent_score", "mean")).reset_index()


def speed_to_lead_by_priority(data=None):
    df = base_frame(data)
    return df.groupby("priority_tier").agg(avg_response_hours=("response_time_hours", "mean"), sla_compliance=("sla_status", lambda s: (s == "met").mean())).reset_index()


def sla_compliance_by_sdr(data=None):
    df = base_frame(data)
    return df.groupby("sdr_id", dropna=False).agg(sla_compliance=("sla_status", lambda s: (s == "met").mean()), leads=("lead_id", "count")).reset_index()


def sql_rate_by_campaign(data=None):
    df = base_frame(data)
    return df.groupby("campaign_id").agg(leads=("lead_id", "count"), sql_rate=("is_sql", "mean"), avg_score=("lead_score", "mean")).reset_index()


def opportunity_rate_by_channel(data=None):
    return conversion_by_channel(data)[["channel", "opportunity_rate"]]


def priority_lead_waste_rate(data=None):
    df = base_frame(data)
    high = df[(df["priority_tier"].isin(["p1", "p2"])) | (df["lead_score"] >= 80)]
    wasted = high[(high["sla_status"] == "breached") | (high["sdr_id"].isna()) | (high["is_sql"] == 0)]
    return safe_rate(len(wasted), len(high))


def executive_summary_metrics(data=None) -> dict[str, float]:
    data = data or load_case_data()
    return {
        "total_leads": total_leads(data),
        "total_mqls": total_mqls(data),
        "total_sqls": total_sqls(data),
        "average_lead_score": average_lead_score(data),
        "sla_compliance_rate": sla_compliance_rate(data),
        "mql_to_sql_conversion": mql_to_sql_conversion(data),
        "sql_to_opportunity_conversion": sql_to_opportunity_conversion(data),
        "leads_without_owner": leads_without_owner(data),
        "high_priority_delayed_leads": high_priority_delayed_leads(data),
        "priority_lead_waste_rate": priority_lead_waste_rate(data),
    }
