# 淘宝用户行为转化漏斗诊断与用户分层分析

基于阿里云天池 `UserBehavior` 数据集，从 `pv -> fav/cart -> buy` 行为路径出发，完成一个偏业务诊断的数据分析项目。核心目标不是只做可视化，而是定位转化流失环节，并给出可执行的用户运营建议。

## 项目目标
1. 识别用户转化损失主要发生在哪些环节。
2. 找出高活跃低转化用户群与高曝光低成交类目。
3. 输出可复用的数据产物、图表、SQL 校验结果、分析报告和 PPT。

## 技术栈
- `Python`
- `Pandas`
- `NumPy`
- `Matplotlib`
- `Seaborn`
- `SQLite`
- `Jupyter Notebook`
- `python-pptx`

## 项目结构图
```text
E-commerce data analysis/
├─ data/
│  ├─ raw/                        # 原始数据目录，可放 UserBehavior.csv
│  └─ processed/                  # 分析中间表与结果产物
│     ├─ analysis_summary.json
│     ├─ category_conversion_summary.csv
│     ├─ daily_behavior_counts.csv
│     ├─ hourly_behavior_counts.csv
│     ├─ user_behavior_sample.csv
│     └─ weekday_behavior_counts.csv
├─ figures/                       # 导出的可视化图表
├─ notebooks/                     # 演示型 Notebook
├─ reports/                       # Markdown 报告与汇报材料
├─ sql/                           # SQL 校验脚本
├─ src/
│  └─ taobao_analysis/
│     ├─ config.py                # 路径、字段、chunk 参数配置
│     ├─ data_processing.py       # 数据清洗
│     ├─ metrics.py               # 指标与漏斗计算
│     ├─ pipeline.py              # 主分析流程
│     ├─ reporting.py             # 报告内容生成
│     └─ visualization.py         # 图表生成
├─ tests/                         # 单元测试
├─ tools/
│  ├─ generate_notebooks.py       # 生成 Notebook
│  └─ generate_ppt.py             # 生成 PPT
├─ run_analysis.py                # 项目主入口
├─ requirements.txt
└─ README.md
```

## 数据集说明
- 数据集：阿里云天池 `UserBehavior`
- 核心字段：
  - `user_id`
  - `item_id`
  - `category_id`
  - `behavior_type`
  - `timestamp`
- 行为类型：
  - `pv`：浏览
  - `fav`：收藏
  - `cart`：加购
  - `buy`：购买

## 运行说明

### 1. 安装依赖
```powershell
python -m pip install -r requirements.txt
```

### 2. 准备原始数据
将 `UserBehavior.csv` 放到以下任一位置：
- 项目根目录：`D:\E-commerce data analysis\UserBehavior.csv`
- 原始数据目录：`D:\E-commerce data analysis\data\raw\UserBehavior.csv`

说明：
- 项目使用分块读取，适合处理大体量 CSV。
- `UserBehavior.csv` 体积较大，不建议提交到 GitHub。

### 3. 运行主分析流程
```powershell
python run_analysis.py
```

执行后会自动完成：
1. 原始数据读取与清洗
2. 行为聚合与漏斗指标计算
3. 用户分层特征构建
4. 图表生成
5. Markdown 报告导出
6. 汇总 JSON 和分析中间表落盘

### 4. 运行测试
当前测试使用 `unittest`：
```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
```

### 5. 生成 Notebook
```powershell
python tools/generate_notebooks.py
```

### 6. 生成 PPT
如果当前环境已安装 `python-pptx`：
```powershell
python tools/generate_ppt.py
```

如果当前 Python 环境没有 `python-pptx`，可使用 Codex 自带运行时：
```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tools\generate_ppt.py
```

## 主要输出
- `data/processed/user_behavior_sample.csv`：Notebook 复用样本
- `data/processed/user_features.csv`：用户分层结果
- `data/processed/analysis_mart.db`：SQLite 分析库
- `data/processed/analysis_summary.json`：核心结果汇总
- `figures/*.png`：分析图表
- `reports/电商用户行为转化诊断分析报告.md`：分析报告

## SQL 校验
`sql/` 目录下包含以下 SQL：
- `funnel_metrics.sql`
- `time_analysis.sql`
- `user_segmentation.sql`

这些 SQL 直接基于 `data/processed/analysis_mart.db` 运行，用于复核关键分析结果。

## 分析亮点
- 使用分块处理避免一次性加载 3GB+ 原始数据。
- 从用户级漏斗而非单纯行为次数视角分析转化。
- 结合时间、类目、用户分层三类维度定位问题。
- 同时输出 Python、SQL、报告、PPT，多场景可复用。

## 面试 / 汇报表达建议
1. 先讲业务问题，再讲实现细节。
2. 用“问题 -> 证据 -> 结论 -> 动作”组织汇报。
3. 优先展示漏斗流失、高流量低转化时段、重点运营用户群。

## 简历描述示例
- 使用 `Python、Pandas、SQL、Seaborn` 对淘宝用户行为日志进行分块清洗与分析，构建用户级转化漏斗，识别关键流失环节与高流量低转化场景。
- 从时间、类目、用户活跃度等维度拆解转化差异，完成用户分层并识别重点运营人群。
- 输出结构化分析报告、图表与汇报型 PPT，形成从数据洞察到策略建议的完整闭环。
