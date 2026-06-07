---
id: task-06
title: 编写 Notebook 06 — 环境走查 + PPO 单算法训练
priority: P0
estimated_hours: 3
depends_on: [task-01, task-02, task-04]
author: lmr
created_at: 2026-06-07T01:48:57+08:00
blocks: [task-09]
allowed_paths:
  - ellectric/notebooks/06_rl_trading_agent.ipynb
---

# task-06: Notebook 06 — 环境走查 + PPO 训练

## 修改文件（必填）
- ADD `ellectric/notebooks/06_rl_trading_agent.ipynb` (new file)

## 实现要求
1. 创建 Jupyter notebook，遵循现有 01-05 的样式规范
2. 包含以下 sections（Markdown + Code cells）：
   - **Markdown**: 本节目标和预期（中英双语）
   - **Markdown + Code**: 导入库（import gymnasium, sb3, etc.）
   - **Markdown + Code**: 数据加载（复用 data_loader.py loader）
   - **Markdown + Code**: 环境初始化（ElectricityMarketEnv）
   - **Markdown + Code**: 随机策略 100 episodes 走查（show reward distribution）
   - **Markdown + Code**: PPO 训练 50K steps（TensorBoard 日志）
   - **Markdown + Code**: 训练曲线（episode reward, mean reward）
   - **Markdown + Code**: 评估（5 episodes 回放，actual vs bid overlay）
   - **Markdown + Code**: 动作分布直方图（bid volumes per hour）
   - **Markdown + 思考题**: 3-5 道 reflection questions

3. Markdown 内容使用中文，技术术语保留英文
4. 所有代码 cell 可执行（not 伪代码）
5. 使用 plotly 可视化
6. 与 Phase 1 notebooks 风格一致

## 接口定义（代码类任务必填）
This is a notebook — no public API. But it must import from:
- `ellectric.pipeline.data_loader` (create_loader)
- `ellectric.pipeline.cleaner` (clean_data)
- `ellectric.pipeline.forecaster` (XGBoostForecaster)
- `ellectric.pipeline.price_forecaster` (LEARForecaster)
- `ellectric.pipeline.trading_env` (ElectricityMarketEnv)
- `ellectric.pipeline.rl_trainer` (RLAgentFactory)

## 边界处理（必填）
1. 所有 import 需放在单独 cell，失败时显示清晰错误
2. 数据文件不存在时显示可读性错误 + 提示从 Phase 1/2 notebook 生成
3. notebook 执行时无 GPU 也无警告（CPU 可运行）
4. 训练参数硬编码默认值（50000 timesteps），但 cell 中可修改
5. TensorBoard 日志路径使用相对于 notebook 的相对路径：`../../tb_logs`
6. 模型保存到 `models/ppo_trader.zip`（相对于项目根目录）

## 非目标（本任务不做的事）
- 不做 TD3/SAC 训练（Notebook 07 负责）
- 不做回测（Notebook 07 负责）
- 不做 SHAP 解释（Notebook 08 负责）

## 参考
- Phase 1 notebooks: 01_data_ingestion.ipynb ~ 05_end_to_end_baseline.ipynb
- 每个 notebook 末尾的 `## 思考题` 格式
- phase 2 notebook 风格（如有）

## TDD 步骤
1. 写 notebook → 2. jupyter nbconvert --to script 验证可执行 → 3. 手动执行检查

## 验收标准
| # | 验证步骤 | 通过标准 |
|---|----------|----------|
| AC-01 | jupyter nbconvert 06_rl_trading_agent.ipynb --to script | 转换成功无 error |
| AC-02 | notebook 在 Jupyter 中打开 | 无损坏 |
| AC-03 | 包含至少 6 个 Markdown sections | 每个 section 有标题 |
| AC-04 | 包含至少 5 个 思考题 | reflection questions 存在 |
| AC-05 | import 路径正确 | from ellectric.pipeline... 等 import 可用 |
