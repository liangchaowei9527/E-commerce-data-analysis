from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def markdown_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.splitlines(keepends=True),
    }


def code_cell(code: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": code.splitlines(keepends=True),
    }


def build_notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.10"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_notebook(name: str, cells: list[dict]) -> None:
    path = NOTEBOOKS_DIR / name
    path.write_text(json.dumps(build_notebook(cells), ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    shared_imports = """from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path.cwd().resolve().parent if Path.cwd().name == 'notebooks' else Path.cwd()
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
FIGURES_DIR = PROJECT_ROOT / 'figures'
summary = json.loads((PROCESSED_DIR / 'analysis_summary.json').read_text(encoding='utf-8'))
sns.set_theme(style='whitegrid')
"""

    write_notebook(
        "01_data_cleaning.ipynb",
        [
            markdown_cell("# 01 数据清洗\n\n目标：说明原始字段、清洗步骤和样本结构。"),
            code_cell(shared_imports),
            code_cell(
                """sample_df = pd.read_csv(PROCESSED_DIR / 'user_behavior_sample.csv')
sample_df.head()"""
            ),
            code_cell(
                """sample_df.info()
sample_df[['behavior_type', 'hour', 'weekday']].describe(include='all')"""
            ),
            markdown_cell(
                "## 清洗规则\n- 去重\n- 过滤无效行为\n- 时间戳转换为北京时间\n- 衍生 `date/hour/weekday/is_weekend`"
            ),
        ],
    )

    write_notebook(
        "02_eda_behavior_overview.ipynb",
        [
            markdown_cell("# 02 行为概览\n\n目标：建立流量大盘，观察行为结构与时间节律。"),
            code_cell(shared_imports),
            code_cell(
                """overview = summary['overview']
pd.Series(overview)"""
            ),
            code_cell(
                """daily = pd.read_csv(PROCESSED_DIR / 'daily_behavior_counts.csv')
hourly = pd.read_csv(PROCESSED_DIR / 'hourly_behavior_counts.csv')
daily.head(), hourly.head()"""
            ),
            code_cell(
                """hourly_pivot = hourly.pivot_table(index='hour', columns='behavior_type', values='count', aggfunc='sum', fill_value=0)
hourly_pivot[['pv', 'buy']].plot(figsize=(10,5), marker='o')
plt.title('小时级浏览与购买趋势')
plt.show()"""
            ),
        ],
    )

    write_notebook(
        "03_funnel_analysis.ipynb",
        [
            markdown_cell("# 03 转化漏斗诊断\n\n目标：识别从浏览到购买的关键流失环节。"),
            code_cell(shared_imports),
            code_cell(
                """funnel = pd.Series(summary['funnel'])
funnel"""
            ),
            code_cell(
                """category = pd.read_csv(PROCESSED_DIR / 'category_conversion_summary.csv')
category.head(10)"""
            ),
            code_cell(
                """plt.figure(figsize=(8,5))
sns.barplot(x=['pv','fav','cart','buy'], y=[funnel['pv_users'], funnel['fav_users'], funnel['cart_users'], funnel['buy_users']])
plt.title('用户级漏斗')
plt.show()"""
            ),
        ],
    )

    write_notebook(
        "04_user_segmentation.ipynb",
        [
            markdown_cell("# 04 用户分层分析\n\n目标：识别高活跃低转化等重点运营人群。"),
            code_cell(shared_imports),
            code_cell(
                """user_features = pd.read_csv(PROCESSED_DIR / 'user_features.csv')
user_features.head()"""
            ),
            code_cell(
                """user_features.groupby('segment')[['activity_score', 'buy', 'conversion_rate', 'recency_days']].mean().sort_values('activity_score', ascending=False)"""
            ),
            code_cell(
                """segment_counts = user_features['segment'].value_counts()
segment_counts.plot(kind='bar', figsize=(8,5), color='#C44E52')
plt.title('用户分层分布')
plt.show()"""
            ),
        ],
    )

    write_notebook(
        "05_business_recommendations.ipynb",
        [
            markdown_cell("# 05 业务建议整理\n\n目标：把分析结果转成可执行建议。"),
            code_cell(shared_imports),
            code_cell(
                """recommendations = pd.DataFrame(summary['recommendations'])
recommendations"""
            ),
            markdown_cell(
                "## 使用建议\n- 对高活跃低转化用户做加购召回\n- 对高曝光低成交类目优化详情页与价格策略\n- 在高流量低成交时段加大促购动作"
            ),
        ],
    )


if __name__ == "__main__":
    main()
