from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from taobao_analysis.config import FIGURES_DIR

sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def _save_current_figure(filename: str) -> str:
    path = FIGURES_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return str(path)


def create_all_figures(
    behavior_counts: pd.DataFrame,
    hourly_counts: pd.DataFrame,
    weekday_counts: pd.DataFrame,
    category_summary: pd.DataFrame,
    funnel: dict[str, float],
    user_features: pd.DataFrame,
) -> dict[str, str]:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    figures: dict[str, str] = {}

    plt.figure(figsize=(8, 5))
    sns.barplot(data=behavior_counts, x="behavior_type", y="count", color="#4C72B0")
    plt.title("行为类型分布")
    plt.xlabel("行为类型")
    plt.ylabel("行为次数")
    figures["behavior_distribution"] = _save_current_figure("behavior_distribution.png")

    hourly_pivot = hourly_counts.pivot_table(
        index="hour", columns="behavior_type", values="count", aggfunc="sum", fill_value=0
    ).reset_index()
    for column in ("pv", "buy"):
        if column not in hourly_pivot:
            hourly_pivot[column] = 0
    plt.figure(figsize=(10, 5))
    plt.plot(hourly_pivot["hour"], hourly_pivot["pv"], marker="o", label="pv")
    plt.plot(hourly_pivot["hour"], hourly_pivot["buy"], marker="o", label="buy")
    plt.title("分时段浏览与购买趋势")
    plt.xlabel("小时")
    plt.ylabel("行为次数")
    plt.legend()
    figures["hourly_trend"] = _save_current_figure("hourly_trend.png")

    weekday_pivot = weekday_counts.pivot_table(
        index="weekday", columns="behavior_type", values="count", aggfunc="sum", fill_value=0
    )
    for column in ("pv", "buy", "cart", "fav"):
        if column not in weekday_pivot:
            weekday_pivot[column] = 0
    weekday_rate = pd.DataFrame(
        {
            "weekday": weekday_pivot.index,
            "pv_to_buy_rate": weekday_pivot["buy"] / weekday_pivot["pv"].clip(lower=1),
            "cart_to_buy_rate": weekday_pivot["buy"] / weekday_pivot["cart"].clip(lower=1),
        }
    )
    plt.figure(figsize=(9, 5))
    sns.heatmap(weekday_rate.set_index("weekday"), annot=True, fmt=".2%", cmap="YlGnBu")
    plt.title("按星期的关键转化率热力图")
    figures["weekday_heatmap"] = _save_current_figure("weekday_heatmap.png")

    top_categories = category_summary.head(10).copy()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_categories, x="pv_to_buy_rate", y="category_id", color="#55A868")
    plt.title("Top类目浏览转购买率")
    plt.xlabel("浏览转购买率")
    plt.ylabel("类目ID")
    figures["category_conversion"] = _save_current_figure("category_conversion.png")

    funnel_df = pd.DataFrame(
        {
            "stage": ["pv_users", "fav_users", "cart_users", "buy_users"],
            "users": [funnel["pv_users"], funnel["fav_users"], funnel["cart_users"], funnel["buy_users"]],
        }
    )
    plt.figure(figsize=(8, 5))
    sns.barplot(data=funnel_df, x="stage", y="users", color="#8172B3")
    plt.title("用户级转化漏斗")
    plt.xlabel("漏斗阶段")
    plt.ylabel("用户数")
    figures["funnel"] = _save_current_figure("funnel.png")

    segment_counts = user_features["segment"].value_counts().reset_index()
    segment_counts.columns = ["segment", "count"]
    plt.figure(figsize=(8, 5))
    sns.barplot(data=segment_counts, x="segment", y="count", color="#C44E52")
    plt.title("用户分层分布")
    plt.xlabel("用户分层")
    plt.ylabel("用户数")
    figures["segment_distribution"] = _save_current_figure("segment_distribution.png")

    return figures
