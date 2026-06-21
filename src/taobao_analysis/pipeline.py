from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from taobao_analysis.config import (
    CHUNK_SIZE,
    COLUMN_NAMES,
    FIGURES_DIR,
    PROCESSED_DIR,
    RAW_FILE_CANDIDATES,
    REPORTS_DIR,
    SAMPLE_ROWS,
)
from taobao_analysis.data_processing import clean_behavior_data
from taobao_analysis.metrics import (
    build_user_features_from_aggregate,
    compute_funnel_metrics,
)
from taobao_analysis.reporting import (
    build_business_recommendations,
    build_summary_payload,
    render_markdown_report,
)
from taobao_analysis.visualization import create_all_figures


@dataclass
class AnalysisArtifacts:
    overview: dict[str, float]
    funnel: dict[str, float]
    sample_path: Path
    summary_path: Path
    report_path: Path


def find_raw_file() -> Path:
    for path in RAW_FILE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("未找到 UserBehavior.csv，请放到项目根目录或 data/raw/ 目录下。")


def _append_aggregate(base: pd.DataFrame | None, partial: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if base is None:
        return partial.copy()
    merged = pd.concat([base, partial], ignore_index=True)
    return merged.groupby(keys, as_index=False)["count"].sum()


def _merge_user_partial(base: pd.DataFrame | None, partial: pd.DataFrame) -> pd.DataFrame:
    count_columns = ["pv", "fav", "cart", "buy"]
    if base is None:
        return partial.copy()

    merged = base.merge(partial, on="user_id", how="outer", suffixes=("_base", "_part"))
    result = pd.DataFrame({"user_id": merged["user_id"]})
    for column in count_columns:
        result[column] = merged.get(f"{column}_base", 0).fillna(0) + merged.get(f"{column}_part", 0).fillna(0)
    result["last_active_time"] = pd.concat(
        [merged["last_active_time_base"], merged["last_active_time_part"]], axis=1
    ).max(axis=1)
    return result


def process_raw_data(raw_path: Path, chunk_size: int = CHUNK_SIZE, sample_rows: int = SAMPLE_ROWS) -> dict[str, object]:
    behavior_counts = None
    daily_counts = None
    hourly_counts = None
    weekday_counts = None
    category_counts = None
    user_partials = None
    sampled_chunks: list[pd.DataFrame] = []
    processed_rows = 0
    chunk_counter = 0

    for chunk in pd.read_csv(raw_path, header=None, names=COLUMN_NAMES, chunksize=chunk_size):
        chunk_counter += 1
        cleaned = clean_behavior_data(chunk)
        processed_rows += len(cleaned)

        sample_n = max(1, sample_rows // 20)
        sampled_chunks.append(cleaned.sample(min(sample_n, len(cleaned)), random_state=42))

        partial_behavior = (
            cleaned.groupby("behavior_type", as_index=False).size().rename(columns={"size": "count"})
        )
        behavior_counts = _append_aggregate(behavior_counts, partial_behavior, ["behavior_type"])

        partial_daily = (
            cleaned.groupby(["date", "behavior_type"], as_index=False).size().rename(columns={"size": "count"})
        )
        daily_counts = _append_aggregate(daily_counts, partial_daily, ["date", "behavior_type"])

        partial_hourly = (
            cleaned.groupby(["hour", "behavior_type"], as_index=False).size().rename(columns={"size": "count"})
        )
        hourly_counts = _append_aggregate(hourly_counts, partial_hourly, ["hour", "behavior_type"])

        partial_weekday = (
            cleaned.groupby(["weekday", "behavior_type"], as_index=False).size().rename(columns={"size": "count"})
        )
        weekday_counts = _append_aggregate(weekday_counts, partial_weekday, ["weekday", "behavior_type"])

        partial_category = (
            cleaned.groupby(["category_id", "behavior_type"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )
        category_counts = _append_aggregate(category_counts, partial_category, ["category_id", "behavior_type"])

        partial_user = (
            cleaned.assign(value=1)
            .pivot_table(
                index="user_id",
                columns="behavior_type",
                values="value",
                aggfunc="sum",
                fill_value=0,
            )
            .rename_axis(columns=None)
            .reset_index()
        )
        for column in ("pv", "fav", "cart", "buy"):
            if column not in partial_user:
                partial_user[column] = 0
        partial_last = cleaned.groupby("user_id", as_index=False)["event_time"].max()
        partial_user = partial_user.merge(partial_last, on="user_id", how="left")
        partial_user = partial_user.rename(columns={"event_time": "last_active_time"})
        user_partials = _merge_user_partial(user_partials, partial_user)

        print(f"Processed chunk {chunk_counter}, cumulative rows: {processed_rows}")

    sample_df = pd.concat(sampled_chunks, ignore_index=True).head(sample_rows)
    user_features = build_user_features_from_aggregate(user_partials)
    return {
        "processed_rows": processed_rows,
        "behavior_counts": behavior_counts,
        "daily_counts": daily_counts,
        "hourly_counts": hourly_counts,
        "weekday_counts": weekday_counts,
        "category_counts": category_counts,
        "user_features": user_features,
        "sample_df": sample_df,
    }
def _summarize_category_conversion(category_counts: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    pivot = (
        category_counts.pivot_table(
            index="category_id", columns="behavior_type", values="count", aggfunc="sum", fill_value=0
        )
        .rename_axis(columns=None)
        .reset_index()
    )
    for column in ("pv", "fav", "cart", "buy"):
        if column not in pivot:
            pivot[column] = 0
    pivot["pv_to_buy_rate"] = pivot["buy"] / pivot["pv"].clip(lower=1)
    pivot["cart_to_buy_rate"] = pivot["buy"] / pivot["cart"].clip(lower=1)
    return pivot.sort_values("pv", ascending=False).head(top_n)


def build_outputs(results: dict[str, object]) -> AnalysisArtifacts:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    sample_df = results["sample_df"]
    sample_path = PROCESSED_DIR / "user_behavior_sample.csv"
    sample_df.to_csv(sample_path, index=False, encoding="utf-8-sig")

    user_features = results["user_features"]
    user_features_path = PROCESSED_DIR / "user_features.csv"
    user_features.to_csv(user_features_path, index=False, encoding="utf-8-sig")

    daily_counts = results["daily_counts"]
    hourly_counts = results["hourly_counts"]
    weekday_counts = results["weekday_counts"]
    category_summary = _summarize_category_conversion(results["category_counts"])

    daily_counts.to_csv(PROCESSED_DIR / "daily_behavior_counts.csv", index=False, encoding="utf-8-sig")
    hourly_counts.to_csv(PROCESSED_DIR / "hourly_behavior_counts.csv", index=False, encoding="utf-8-sig")
    weekday_counts.to_csv(PROCESSED_DIR / "weekday_behavior_counts.csv", index=False, encoding="utf-8-sig")
    category_summary.to_csv(PROCESSED_DIR / "category_conversion_summary.csv", index=False, encoding="utf-8-sig")

    sqlite_path = PROCESSED_DIR / "analysis_mart.db"
    with sqlite3.connect(sqlite_path) as conn:
        sample_df.to_sql("sample_behavior", conn, if_exists="replace", index=False)
        user_features.to_sql("user_features", conn, if_exists="replace", index=False)
        hourly_counts.to_sql("hourly_behavior_counts", conn, if_exists="replace", index=False)
        weekday_counts.to_sql("weekday_behavior_counts", conn, if_exists="replace", index=False)
        category_summary.to_sql("category_conversion_summary", conn, if_exists="replace", index=False)

    behavior_counts = results["behavior_counts"].set_index("behavior_type")["count"].to_dict()
    overview = {
        "total_events": int(results["processed_rows"]),
        "unique_users": int(user_features["user_id"].nunique()),
        "buy_users": int((user_features["buy"] > 0).sum()),
        "avg_events_per_user": float(results["processed_rows"] / max(user_features["user_id"].nunique(), 1)),
        "sample_rows": int(len(sample_df)),
        "pv_events": int(behavior_counts.get("pv", 0)),
        "fav_events": int(behavior_counts.get("fav", 0)),
        "cart_events": int(behavior_counts.get("cart", 0)),
        "buy_events": int(behavior_counts.get("buy", 0)),
    }
    overview["processed_rows"] = int(results["processed_rows"])
    overview["user_segments"] = user_features["segment"].value_counts().to_dict()

    funnel = compute_funnel_metrics(user_features)

    recommendations = build_business_recommendations(
        funnel=funnel,
        hourly_counts=hourly_counts,
        category_summary=category_summary,
        user_features=user_features,
    )
    figure_paths = create_all_figures(
        behavior_counts=results["behavior_counts"],
        hourly_counts=hourly_counts,
        weekday_counts=weekday_counts,
        category_summary=category_summary,
        funnel=funnel,
        user_features=user_features,
    )

    summary_payload = build_summary_payload(
        overview=overview,
        funnel=funnel,
        recommendations=recommendations,
        figure_paths=figure_paths,
        category_summary=category_summary,
    )

    summary_path = PROCESSED_DIR / "analysis_summary.json"
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    report_path = REPORTS_DIR / "电商用户行为转化诊断分析报告.md"
    report_path.write_text(render_markdown_report(summary_payload), encoding="utf-8")

    return AnalysisArtifacts(
        overview=overview,
        funnel=funnel,
        sample_path=sample_path,
        summary_path=summary_path,
        report_path=report_path,
    )


def run_pipeline() -> AnalysisArtifacts:
    raw_path = find_raw_file()
    results = process_raw_data(raw_path)
    return build_outputs(results)
