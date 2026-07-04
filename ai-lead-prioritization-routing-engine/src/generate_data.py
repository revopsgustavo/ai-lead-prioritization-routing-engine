from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "processed"
DB_PATH = ROOT_DIR / "data" / "database" / "lead_routing_case.sqlite"


def band(value: float) -> str:
    if value >= 80:
        return "high"
    if value >= 60:
        return "medium"
    return "low"


def priority(score: float, intent: float, segment: str) -> str:
    if score >= 82 or (intent >= 85 and segment in {"enterprise", "mid_market"}):
        return "p1"
    if score >= 68:
        return "p2"
    if score >= 50:
        return "p3"
    return "p4"


def build_data(seed: int = 42) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    end_date = date(2026, 7, 3)
    days = [end_date - timedelta(days=i) for i in range(89, -1, -1)]

    channel_cfg = pd.DataFrame(
        [
            ("paid_search", "Paid Search", 0.39, 58, 63, 0.13, 42000),
            ("referral", "Referral", 0.13, 80, 74, 0.34, 61000),
            ("outbound", "Outbound", 0.19, 66, 58, 0.18, 52000),
            ("partner", "Partner", 0.08, 77, 70, 0.27, 89000),
            ("organic", "Organic", 0.12, 68, 65, 0.20, 47000),
            ("webinar", "Webinar", 0.09, 71, 79, 0.23, 56000),
        ],
        columns=["channel_id", "channel", "volume_weight", "fit_mean", "intent_mean", "base_sql_rate", "avg_potential_arr"],
    )
    channels = channel_cfg.drop(columns=["volume_weight", "fit_mean", "intent_mean", "base_sql_rate", "avg_potential_arr"])
    channels["description"] = [
        "Alto volume, fit medio inferior e maior variabilidade de intencao.",
        "Menor volume, melhor conversao e forte sinal de confianca.",
        "Volume controlado, performance dependente da execucao por SDR.",
        "Baixo volume, maior potencial de ticket e ciclo mais consultivo.",
        "Volume organico estavel com qualidade intermediaria.",
        "Sinal de intencao alto, dependente de cadencia pos-evento.",
    ]

    sdrs = pd.DataFrame(
        [
            ("sdr_01", "Ana Martins", "mid_market", 22, 0.24, "active"),
            ("sdr_02", "Bruno Costa", "smb", 20, 0.12, "active"),
            ("sdr_03", "Carla Nunes", "enterprise", 16, 0.27, "active"),
            ("sdr_04", "Diego Lima", "smb", 18, 0.19, "active"),
            ("sdr_05", "Elisa Rocha", "strategic", 14, 0.31, "active"),
        ],
        columns=["sdr_id", "sdr_name", "territory", "daily_capacity", "expected_sql_rate", "status"],
    )

    campaigns = pd.DataFrame(
        [
            ("camp_01", "Search Always On", "paid_search", "acquisition", "high_volume_low_fit"),
            ("camp_02", "Brand Competitor Capture", "paid_search", "acquisition", "high_intent_mixed_fit"),
            ("camp_03", "Customer Referral Q3", "referral", "referral", "low_volume_high_quality"),
            ("camp_04", "Outbound Named Accounts", "outbound", "sales", "sdr_variance"),
            ("camp_05", "Partner Marketplace", "partner", "partner", "low_volume_high_arr"),
            ("camp_06", "Operations Webinar", "webinar", "demand", "good_intent_sla_sensitive"),
            ("camp_07", "SEO RevOps Templates", "organic", "demand", "mid_quality"),
            ("camp_08", "Generic SaaS Keywords", "paid_search", "acquisition", "high_volume_low_sql"),
        ],
        columns=["campaign_id", "campaign_name", "channel", "motion", "scenario"],
    )

    routing_rules = pd.DataFrame(
        [
            ("rule_01", "Enterprise and Partner to strategic SDR", "segment = enterprise or channel = partner", "sdr_05", "p1", "active"),
            ("rule_02", "Paid Search round robin SMB", "channel = paid_search and segment = smb", "sdr_02", "p3", "active"),
            ("rule_03", "Webinar and organic to mid market", "channel in webinar, organic", "sdr_01", "p2", "active"),
            ("rule_04", "Outbound named accounts", "channel = outbound", "sdr_03", "p2", "active"),
            ("rule_05", "Fallback manual queue", "no rule matched", None, "p4", "active"),
        ],
        columns=["rule_id", "rule_name", "condition", "default_sdr_id", "default_priority_tier", "status"],
    )

    lead_rows, account_rows = [], []
    segments = ["smb", "mid_market", "enterprise"]
    industries = ["software", "financial_services", "retail", "manufacturing", "healthcare", "education"]
    company_sizes = {"smb": (30, 180), "mid_market": (181, 900), "enterprise": (901, 4500)}
    lead_id = 1
    for day_index, created in enumerate(days):
        base = 18 + int(day_index > 68) * 8 + rng.poisson(5)
        for _ in range(base):
            ch = channel_cfg.sample(1, weights=channel_cfg["volume_weight"], random_state=int(rng.integers(1, 1_000_000))).iloc[0]
            campaign_pool = campaigns[campaigns["channel"] == ch["channel_id"]]
            campaign_id = campaign_pool.sample(1, random_state=int(rng.integers(1, 1_000_000))).iloc[0]["campaign_id"]
            segment = rng.choice(segments, p=[0.47, 0.36, 0.17])
            if ch["channel_id"] == "partner":
                segment = rng.choice(["mid_market", "enterprise"], p=[0.45, 0.55])
            fit = float(np.clip(rng.normal(ch["fit_mean"], 14), 10, 100))
            intent = float(np.clip(rng.normal(ch["intent_mean"], 18), 5, 100))
            potential_arr = float(np.clip(rng.normal(ch["avg_potential_arr"], 18000), 8000, 160000))
            score = float(np.clip(0.48 * fit + 0.42 * intent + 0.10 * min(potential_arr / 1600, 100) + rng.normal(0, 6), 0, 100))
            tier = priority(score, intent, segment)
            lead_key = f"lead_{lead_id:05d}"
            account_id = f"acct_{lead_id:05d}"
            account_rows.append(
                (account_id, f"Conta {lead_id:05d}", segment, rng.choice(industries), int(rng.integers(*company_sizes[segment])), round(potential_arr, 2))
            )
            lead_rows.append(
                (lead_key, account_id, created.isoformat(), ch["channel_id"], campaign_id, segment, round(potential_arr, 2), tier, "new")
            )
            lead_id += 1

    leads = pd.DataFrame(
        lead_rows,
        columns=["lead_id", "account_id", "created_date", "channel", "campaign_id", "segment", "potential_arr", "priority_tier", "lead_status"],
    )
    accounts = pd.DataFrame(account_rows, columns=["account_id", "account_name", "segment", "industry", "employee_count", "potential_arr"])

    score_rows = []
    for lead in leads.itertuples(index=False):
        cfg = channel_cfg[channel_cfg["channel_id"] == lead.channel].iloc[0]
        fit = float(np.clip(rng.normal(cfg.fit_mean, 14), 10, 100))
        intent = float(np.clip(rng.normal(cfg.intent_mean, 18), 5, 100))
        score = float(np.clip(0.48 * fit + 0.42 * intent + 0.10 * min(lead.potential_arr / 1600, 100) + rng.normal(0, 6), 0, 100))
        score_rows.append((lead.lead_id, round(fit, 1), round(intent, 1), round(score, 1), band(score), priority(score, intent, lead.segment)))
    lead_scores = pd.DataFrame(score_rows, columns=["lead_id", "icp_fit_score", "intent_score", "lead_score", "score_band", "priority_tier_scored"])
    leads = leads.drop(columns=["priority_tier"]).merge(lead_scores[["lead_id", "priority_tier_scored"]], on="lead_id").rename(columns={"priority_tier_scored": "priority_tier"})

    route_rows, sla_rows, activity_rows, outcome_rows = [], [], [], []
    workload = {sid: 0 for sid in sdrs["sdr_id"]}
    for lead in leads.merge(lead_scores, on="lead_id").itertuples(index=False):
        created_dt = pd.Timestamp(lead.created_date)
        rule_id, sdr_id = "rule_05", None
        if lead.channel == "partner" or lead.segment == "enterprise":
            rule_id, sdr_id = "rule_01", "sdr_05"
        elif lead.channel == "paid_search" and lead.segment == "smb":
            rule_id, sdr_id = "rule_02", "sdr_02"
        elif lead.channel in {"webinar", "organic"}:
            rule_id, sdr_id = "rule_03", "sdr_01"
        elif lead.channel == "outbound":
            rule_id, sdr_id = "rule_04", rng.choice(["sdr_03", "sdr_02", "sdr_04"], p=[0.56, 0.30, 0.14])
        else:
            sdr_id = rng.choice(["sdr_01", "sdr_04"], p=[0.70, 0.30])
            rule_id = "rule_03"
        if lead.icp_fit_score >= 78 and rng.random() < 0.035:
            sdr_id = None
        if sdr_id:
            workload[sdr_id] += 1
        overload = 1.45 if sdr_id == "sdr_02" else 1.0
        end_period_penalty = 1.8 if created_dt >= pd.Timestamp(days[-18]) else 1.0
        priority_factor = {"p1": 0.70, "p2": 0.95, "p3": 1.25, "p4": 1.55}[lead.priority_tier]
        response_hours = float(np.clip(rng.gamma(2.2, 5.0) * overload * end_period_penalty * priority_factor, 0.2, 120))
        if lead.priority_tier == "p1" and rng.random() < 0.18:
            response_hours += float(rng.uniform(20, 55))
        contacted_at = created_dt + pd.Timedelta(hours=response_hours) if sdr_id else pd.NaT
        sla_target = {"p1": 4, "p2": 12, "p3": 24, "p4": 48}[lead.priority_tier]
        sla_status = "breached" if pd.isna(contacted_at) or response_hours > sla_target else "met"
        route_rows.append((lead.lead_id, rule_id, sdr_id, lead.priority_tier, "rule_based", round(response_hours, 2) if sdr_id else np.nan, created_dt.isoformat()))
        sla_rows.append((lead.lead_id, sdr_id, sla_target, round(response_hours, 2) if sdr_id else np.nan, sla_status, contacted_at.isoformat() if sdr_id else ""))
        activity_rows.append((lead.lead_id, "first_touch", contacted_at.isoformat() if sdr_id else "", "completed" if sdr_id else "not_assigned"))
        cfg = channel_cfg[channel_cfg["channel_id"] == lead.channel].iloc[0]
        sdr_rate = float(sdrs[sdrs["sdr_id"] == sdr_id]["expected_sql_rate"].iloc[0]) if sdr_id else 0.03
        quality_factor = (lead.lead_score / 100) * 0.60 + (lead.icp_fit_score / 100) * 0.40
        sla_factor = 0.72 if sla_status == "breached" else 1.06
        channel_factor = {"paid_search": 0.78, "referral": 1.35, "outbound": 0.95, "partner": 1.22, "organic": 1.00, "webinar": 1.08}[lead.channel]
        sql_prob = float(np.clip((cfg.base_sql_rate * 0.55 + sdr_rate * 0.45) * quality_factor * sla_factor * channel_factor, 0.02, 0.62))
        is_sql = rng.random() < sql_prob
        opp_prob = 0.47 if lead.channel in {"referral", "partner"} else 0.31
        is_opp = is_sql and rng.random() < opp_prob * (0.70 + quality_factor)
        status = "opportunity" if is_opp else "sql" if is_sql else rng.choice(["mql", "disqualified", "nurture"], p=[0.50, 0.25, 0.25])
        outcome_rows.append((lead.lead_id, sdr_id, status, int(status in {"mql", "sql", "opportunity"}), int(is_sql), int(is_opp), round(sql_prob, 4)))

    routing_decisions = pd.DataFrame(route_rows, columns=["lead_id", "rule_id", "sdr_id", "priority_tier", "routing_method", "response_time_hours", "routed_at"])
    sla_events = pd.DataFrame(sla_rows, columns=["lead_id", "sdr_id", "sla_target_hours", "response_time_hours", "sla_status", "first_contact_at"])
    lead_activity = pd.DataFrame(activity_rows, columns=["lead_id", "activity_type", "activity_at", "activity_status"])
    conversion_outcomes = pd.DataFrame(outcome_rows, columns=["lead_id", "sdr_id", "conversion_status", "is_mql", "is_sql", "is_opportunity", "expected_sql_probability"])
    return {
        "leads": leads,
        "accounts": accounts,
        "channels": channels,
        "campaigns": campaigns,
        "sdrs": sdrs,
        "routing_rules": routing_rules,
        "lead_activity": lead_activity,
        "sla_events": sla_events,
        "lead_scores": lead_scores,
        "routing_decisions": routing_decisions,
        "conversion_outcomes": conversion_outcomes,
    }


def main():
    tables = build_data()
    for name, df in tables.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
    with sqlite3.connect(DB_PATH) as conn:
        for name, df in tables.items():
            df.to_sql(name, conn, if_exists="replace", index=False)
    print(f"Generated {len(tables['leads'])} leads and SQLite at {DB_PATH}")


if __name__ == "__main__":
    main()
