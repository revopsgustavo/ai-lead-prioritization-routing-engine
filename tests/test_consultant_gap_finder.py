import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

import consultant_gap_finder
import generate_data


def test_consultant_gap_log_contract():
    data = generate_data.build_data()
    gaps = consultant_gap_finder.generate_gaps(data)
    assert not gaps.empty
    for column in ["severity", "recommended_action", "missing_evidence", "validation_questions"]:
        assert column in gaps.columns
    forbidden = ["a causa e", "foi comprovado", "garantidamente", "com certeza"]
    text = " ".join(gaps.astype(str).values.ravel()).lower()
    assert not any(term in text for term in forbidden)
