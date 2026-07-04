import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import generate_data
import metrics


def test_main_metrics_do_not_error_and_rates_are_valid():
    data = generate_data.build_data()
    assert metrics.total_leads(data) > 0
    assert metrics.total_sqls(data) >= 0
    assert 0 <= metrics.sla_compliance_rate(data) <= 1
    assert 0 <= metrics.mql_to_sql_conversion(data) <= 1
    assert 0 <= metrics.sql_to_opportunity_conversion(data) <= 1
    assert metrics.average_lead_score(data) > 0


def test_required_metric_tables_return_dataframes():
    data = generate_data.build_data()
    assert not metrics.conversion_by_channel(data).empty
    assert not metrics.routing_load_by_sdr(data).empty
    assert not metrics.speed_to_lead_by_priority(data).empty
