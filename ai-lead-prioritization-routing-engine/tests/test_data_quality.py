import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import data_quality
import generate_data


def test_data_quality_required_files_and_columns(tmp_path):
    generate_data.main()
    report = data_quality.validate()
    critical = report[report["severity"] == "critical"]
    assert not report.empty
    assert (critical["status"] == "pass").all()
    assert "required_column_exists" in set(report["check_name"])
