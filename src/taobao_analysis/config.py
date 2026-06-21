from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures"
REPORTS_DIR = PROJECT_ROOT / "reports"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SQL_DIR = PROJECT_ROOT / "sql"

RAW_FILE_CANDIDATES = [
    RAW_DIR / "UserBehavior.csv",
    PROJECT_ROOT / "UserBehavior.csv",
]

COLUMN_NAMES = ["user_id", "item_id", "category_id", "behavior_type", "timestamp"]
CHUNK_SIZE = 1_000_000
SAMPLE_ROWS = 200_000
