from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_business_recommendations(
    funnel: dict[str, float],
    hourly_counts: pd.DataFrame,
    category_summary: pd.DataFrame,
    user_features: pd.DataFrame,
) -> list[dict[str, str]]:
    hourly_pivot = hourly_counts.pivot_table(
        index="hour", columns="behavior_type", values="count", aggfunc="sum", fill_value=0
    )
    for column in ("pv", "buy", "cart"):
        if column not in hourly_pivot:
            hourly_pivot[column] = 0
    hourly_pivot["buy_rate"] = hourly_pivot["buy"] / hourly_pivot["pv"].clip(lower=1)
    low_conversion_hour = int(hourly_pivot.sort_values(["pv", "buy_rate"], ascending=[False, True]).index[0])
    best_conversion_hour = int(hourly_pivot.sort_values("buy_rate", ascending=False).index[0])

    weak_category = category_summary.sort_values(["pv", "pv_to_buy_rate"], ascending=[False, True]).iloc[0]
    segment_share = user_features["segment"].value_counts(normalize=True)
    high_active_low_conversion_share = float(segment_share.get("高活跃低转化", 0.0))

    return [
        {
            "priority": "高影响低难度",
            "issue": "高流量时段存在明显转化损失",
            "evidence": f"{low_conversion_hour}:00 流量高但购买转化较弱，建议对比 {best_conversion_hour}:00 的承接策略。",
            "action": "在低转化高流量时段增加限时促单、购物车提醒与推荐位优化。",
            "impact": "优先提升浏览到购买的短链路转化效率。",
        },
        {
            "priority": "高影响中难度",
            "issue": "高活跃低转化用户占比偏高",
            "evidence": f"高活跃低转化用户占比约 {high_active_low_conversion_share:.1%}，属于重点召回人群。",
            "action": "对高活跃低转化用户定向发券、加购召回，并优化详情页信息密度。",
            "impact": "有助于把已有流量转化为订单，提高运营 ROI。",
        },
        {
            "priority": "中影响中难度",
            "issue": "部分高曝光类目存在高浏览低成交",
            "evidence": (
                f"类目 {int(weak_category['category_id'])} 曝光高，但浏览转购买率仅 "
                f"{weak_category['pv_to_buy_rate']:.2%}。"
            ),
            "action": "针对弱转化类目优化价格展示、评价露出和关联推荐策略。",
            "impact": "改善重点类目的流量承接质量，减少无效曝光。",
        },
        {
            "priority": "中影响低难度",
            "issue": "加购后未购买仍是关键损失环节",
            "evidence": f"整体加购转购买率为 {funnel['cart_to_buy_rate']:.2%}，存在后链路流失。",
            "action": "增加购物车提醒、限时优惠和支付前补贴策略。",
            "impact": "提升高意向用户的最终成交概率。",
        },
    ]


def build_summary_payload(
    overview: dict[str, float],
    funnel: dict[str, float],
    recommendations: list[dict[str, str]],
    figure_paths: dict[str, str],
    category_summary: pd.DataFrame,
) -> dict[str, object]:
    top_categories = category_summary.head(5).to_dict(orient="records")
    return {
        "overview": overview,
        "funnel": funnel,
        "recommendations": recommendations,
        "figures": figure_paths,
        "top_categories": top_categories,
    }


def render_markdown_report(summary: dict[str, object]) -> str:
    overview = summary["overview"]
    funnel = summary["funnel"]
    recommendations = summary["recommendations"]
    top_categories = summary["top_categories"]

    recommendation_lines = "\n".join(
        [
            (
                f"### {item['priority']} | {item['issue']}\n"
                f"- 数据证据：{item['evidence']}\n"
                f"- 建议动作：{item['action']}\n"
                f"- 预期影响：{item['impact']}"
            )
            for item in recommendations
        ]
    )
    category_lines = "\n".join(
        [
            f"| {int(row['category_id'])} | {int(row['pv'])} | {int(row['buy'])} | {row['pv_to_buy_rate']:.2%} |"
            for row in top_categories
        ]
    )

    return f"""# 电商用户行为转化诊断分析报告

## 1. 背景与目标
- 数据集：阿里云天池 `UserBehavior`
- 目标：识别淘宝用户从浏览到购买的核心转化损失环节，并找到优先运营的用户群。
- 项目定位：面向数据分析实习的业务诊断型项目，强调问题拆解、指标分析与策略建议。

## 2. 数据说明与清洗
- 原始行为字段：`user_id`、`item_id`、`category_id`、`behavior_type`、`timestamp`
- 清洗动作：去重、过滤无效行为、时间戳转北京时间，并衍生 `date/hour/weekday/is_weekend`
- 处理规模：共处理 {overview['processed_rows']:,} 条行为记录，抽样落盘 {overview['sample_rows']:,} 条供 Notebook 复现

## 3. 行为概览
- 样本总行为数：{overview['total_events']:,}
- 样本独立用户数：{overview['unique_users']:,}
- 样本购买用户数：{overview['buy_users']:,}
- 人均行为次数：{overview['avg_events_per_user']:.2f}

## 4. 转化漏斗诊断
- 浏览用户数：{funnel['pv_users']:,}
- 收藏用户数：{funnel['fav_users']:,}
- 加购用户数：{funnel['cart_users']:,}
- 购买用户数：{funnel['buy_users']:,}
- 浏览转收藏率：{funnel['pv_to_fav_rate']:.2%}
- 浏览转加购率：{funnel['pv_to_cart_rate']:.2%}
- 浏览转购买率：{funnel['pv_to_buy_rate']:.2%}
- 加购转购买率：{funnel['cart_to_buy_rate']:.2%}
- 收藏转购买率：{funnel['fav_to_buy_rate']:.2%}

## 5. 重点类目观察
| 类目ID | 浏览量 | 购买量 | 浏览转购买率 |
| --- | ---: | ---: | ---: |
{category_lines}

## 6. 用户分层与业务建议
- 用户分层结构：{overview['user_segments']}

{recommendation_lines}

## 7. 项目亮点
- 采用分块计算处理大体量用户行为日志，避免一次性读入内存
- 基于用户级漏斗口径识别转化损失，而不是只做行为次数统计
- 结合类目与用户分层输出可执行策略，形成“问题-证据-动作”闭环
"""


def relative_figure_path(path: str | Path) -> str:
    return Path(path).as_posix()
