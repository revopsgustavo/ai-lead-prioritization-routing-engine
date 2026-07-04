from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_all_dashboard_pages_render_without_errors():
    pages = [
        "Visão Executiva",
        "Lead Scoring",
        "Routing Engine",
        "SLA e Tempo de Resposta",
        "Performance por SDR",
        "Conversão por Score",
        "Consultor de Gaps",
        "IA Consultora",
        "Análise Executiva",
        "Qualidade dos Dados",
        "Production Flow",
    ]
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"))
    app.run(timeout=15)
    for page in pages:
        app.sidebar.radio[0].set_value(page)
        app.run(timeout=15)
        assert not app.exception, f"Dashboard page failed: {page}"
