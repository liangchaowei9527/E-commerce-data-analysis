from __future__ import annotations

import pandas as pd


def compute_behavior_overview(df: pd.DataFrame) -> dict[str, float]:
    total_events = int(len(df))
    unique_users = int(df["user_id"].nunique())
    buy_users = int(df.loc[df["behavior_type"] == "buy", "user_id"].nunique())
    avg_events_per_user = total_events / unique_users if unique_users else 0.0
    return {
        "total_events": total_events,
        "unique_users": unique_users,
        "buy_users": buy_users,
        "avg_events_per_user": avg_events_per_user,
    }


def build_user_features(df: pd.DataFrame) -> pd.DataFrame:
    pivot = (
        df.assign(value=1)
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
    latest_activity = df.groupby("user_id", as_index=False)["event_time"].max()
    latest_activity = latest_activity.rename(columns={"event_time": "last_active_time"})
    user_features = pivot.merge(latest_activity, on="user_id", how="left")
    return build_user_features_from_aggregate(user_features)


def build_user_features_from_aggregate(user_features: pd.DataFrame) -> pd.DataFrame:
    user_features = user_features.copy()
    for column in ("pv", "fav", "cart", "buy"):
        if column not in user_features:
            user_features[column] = 0

    snapshot_time = user_features["last_active_time"].max()
    user_features["recency_days"] = (
        snapshot_time.normalize() - user_features["last_active_time"].dt.normalize()
    ).dt.days
    user_features["activity_score"] = user_features[["pv", "fav", "cart", "buy"]].sum(axis=1)
    user_features["conversion_rate"] = user_features["buy"] / user_features["activity_score"].clip(lower=1)

    high_activity_threshold = user_features["activity_score"].median()
    high_buy_threshold = user_features["buy"].median()
    low_recency_threshold = user_features["recency_days"].median()

    def classify_user(row: pd.Series) -> str:
        is_high_activity = row["activity_score"] >= high_activity_threshold
        is_high_buy = row["buy"] > high_buy_threshold
        is_recent = row["recency_days"] <= low_recency_threshold

        if is_high_activity and is_high_buy:
            return "高活跃高转化"
        if is_high_activity and not is_high_buy:
            return "高活跃低转化"
        if (not is_high_activity) and is_high_buy and is_recent:
            return "低活跃高价值"
        return "低活跃低转化"

    user_features["segment"] = user_features.apply(classify_user, axis=1)
    return user_features


def compute_funnel_metrics(user_features: pd.DataFrame) -> dict[str, float]:
    has_pv = user_features["pv"] > 0
    has_fav = user_features["fav"] > 0
    has_cart = user_features["cart"] > 0
    has_buy = user_features["buy"] > 0

    pv_users = int(has_pv.sum())
    fav_users = int(has_fav.sum())
    cart_users = int(has_cart.sum())
    buy_users = int(has_buy.sum())
    pv_and_fav_users = int((has_pv & has_fav).sum())
    pv_and_cart_users = int((has_pv & has_cart).sum())
    pv_and_buy_users = int((has_pv & has_buy).sum())
    cart_and_buy_users = int((has_cart & has_buy).sum())
    fav_and_buy_users = int((has_fav & has_buy).sum())

    def safe_divide(numerator: int, denominator: int) -> float:
        return numerator / denominator if denominator else 0.0

    return {
        "pv_users": pv_users,
        "fav_users": fav_users,
        "cart_users": cart_users,
        "buy_users": buy_users,
        "pv_to_fav_rate": safe_divide(pv_and_fav_users, pv_users),
        "pv_to_cart_rate": safe_divide(pv_and_cart_users, pv_users),
        "pv_to_buy_rate": safe_divide(pv_and_buy_users, pv_users),
        "cart_to_buy_rate": safe_divide(cart_and_buy_users, cart_users),
        "fav_to_buy_rate": safe_divide(fav_and_buy_users, fav_users),
    }
