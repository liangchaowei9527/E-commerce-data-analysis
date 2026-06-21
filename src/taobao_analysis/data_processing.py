from __future__ import annotations

import pandas as pd

VALID_BEHAVIORS = ("pv", "fav", "cart", "buy")


def clean_behavior_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize schema and add reusable time features."""
    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned[cleaned["behavior_type"].isin(VALID_BEHAVIORS)].copy()
    cleaned["event_time"] = (
        pd.to_datetime(cleaned["timestamp"], unit="s", utc=True)
        .dt.tz_convert("Asia/Shanghai")
        .dt.tz_localize(None)
    )
    cleaned["date"] = cleaned["event_time"].dt.date
    cleaned["hour"] = cleaned["event_time"].dt.hour
    cleaned["weekday"] = cleaned["event_time"].dt.weekday
    cleaned["is_weekend"] = (cleaned["weekday"] >= 5).astype(int)
    cleaned = cleaned.sort_values(["user_id", "event_time"]).reset_index(drop=True)
    return cleaned
