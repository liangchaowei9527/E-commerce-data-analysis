# 淘宝用户行为转化漏斗诊断与用户分层分析

基于阿里云天池 `UserBehavior` 数据集，围绕用户从 `pv -> fav/cart -> buy` 的行为路径，完成一次面向数据分析实习的业务诊断型项目。项目重点不是“画几张图”，而是回答两个问题：

1. 用户转化损失主要发生在哪些环节？
2. 哪些用户群最值得优先运营，应该采取什么动作提升购买转化？

## 项目亮点
- 使用 **分块处理** 分析大体量行为日志，避免一次性加载 3GB+ 原始 CSV。
- 采用 **用户级转化漏斗**，而不是只做行为次数统计。
- 结合 **时间维度、类目维度、用户分层**，形成更接近真实业务专项分析的故事线。
- 同时输出 **Python 分析、SQL 校验、分析报告、PPT**，适合实习简历展示与面试讲解。

## 技术栈
- `Python`
- `Pandas`
- `NumPy`
- `Matplotlib`
- `Seaborn`
- `SQL (SQLite)`
- `Jupyter Notebook`
- `python-pptx`（用于生成汇报型 PPT）

## 项目结构
```text
data/
  raw/
  processed/
figures/
notebooks/
reports/
sql/
src/taobao_analysis/
tests/
run_analysis.py
README.md
requirements.txt
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

## 分析目标
1. 建立整体行为结构与时间节律视角。
2. 构建用户级转化漏斗，识别核心流失环节。
3. 识别高曝光低成交类目与高活跃低转化用户群。
4. 输出可执行业务建议，形成“问题-证据-动作”闭环。

## 核心分析模块
1. 数据清洗
2. 行为概览
3. 转化漏斗诊断
4. 用户分层分析
5. 业务建议整理

## 运行方式
### 1. 准备数据
将 `UserBehavior.csv` 放在以下任一位置：
- 项目根目录
- `data/raw/UserBehavior.csv`

### 2. 运行测试
```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
```

### 3. 运行主分析
```powershell
python run_analysis.py
```

### 4. 生成 Notebook
```powershell
python tools/generate_notebooks.py
```

### 5. 生成 PPT
如果当前 Python 环境没有 `python-pptx`，可使用 Codex 工作区自带运行时：
```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" tools\generate_ppt.py
```

## 输出结果
- `data/processed/user_behavior_sample.csv`：Notebook 复用样本
- `data/processed/user_features.csv`：用户分层结果
- `data/processed/analysis_mart.db`：SQL 分析用 SQLite 数据库
- `data/processed/analysis_summary.json`：汇总结果
- `reports/电商用户行为转化诊断分析报告.md`
- `reports/电商用户行为转化诊断汇报PPT.pptx`
- `figures/*.png`

## SQL 校验
SQL 文件位于 `sql/`：
- `funnel_metrics.sql`
- `time_analysis.sql`
- `user_segmentation.sql`

这些 SQL 直接基于 `data/processed/analysis_mart.db` 中的表运行。

## 面试表达建议
- 先讲业务问题，而不是先讲代码。
- 强调你做的是 **转化漏斗诊断 + 用户分层 + 策略建议**。
- 面试时优先展示：
  - 关键漏斗指标
  - 高流量低转化时段
  - 高活跃低转化用户群
  - 对应运营动作

## 简历描述示例
- 使用 `Python、Pandas、SQL、Seaborn` 对淘宝用户行为日志进行分块清洗与分析，构建 `浏览-收藏/加购-购买` 用户级转化漏斗，识别关键流失环节与高流量低转化场景。
- 从时间、类目、用户活跃度等维度拆解转化差异，结合近似 `RFM` 思路完成用户分层，识别高活跃低转化等重点运营人群。
- 输出结构化业务建议、图表报告与汇报型 PPT，形成从数据洞察到策略建议的完整项目闭环。
