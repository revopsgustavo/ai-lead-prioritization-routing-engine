from __future__ import annotations

from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "processed"
DB_DIR = ROOT_DIR / "data" / "database"
DOCS_DIR = ROOT_DIR / "docs"


def format_currency_br(value):
    if value is None:
        return "-"
    text = f"R$ {float(value):,.2f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_number_br(value):
    if value is None:
        return "-"
    text = f"{float(value):,.1f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_integer_br(value):
    if value is None:
        return "-"
    text = f"{int(round(float(value))):,}"
    return text.replace(",", ".")


def format_percent_br(value):
    if value is None:
        return "-"
    return f"{float(value) * 100:.1f}%".replace(".", ",")


def format_points_br(value):
    if value is None:
        return "-"
    return f"{float(value):+.1f} pts".replace(".", ",")


def format_date_br(value):
    if value is None:
        return "-"
    try:
        return datetime.fromisoformat(str(value)[:10]).strftime("%d/%m/%Y")
    except ValueError:
        return str(value)


def select_existing(df, columns):
    return [column for column in columns if column in df.columns]


def has_columns(df, columns):
    return all(column in df.columns for column in columns)


def read_markdown(path: Path) -> str:
    if not path.exists():
        return "Arquivo ainda nao gerado."
    return path.read_text(encoding="utf-8")
