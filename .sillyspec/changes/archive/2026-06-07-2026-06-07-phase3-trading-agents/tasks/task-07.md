---
id: task-07
title: 编写 Notebook 07 — PPO/TD3/SAC 对比 + 回测
priority: P0
estimated_hours: 4
depends_on: [task-01, task-02, task-04, task-05]
author: lmr
created_at: 2026-06-07T01:48:57+08:00
blocks: [task-09]
allowed_paths:
  - ellectric/notebooks/07_multi_agent_backtest.ipynb
---

# task-07: Notebook 07 — 多算法对比 + 回测

## 修改文件（必填）
- ADD `ellectric/notebooks/07_multi_agent_backtest.ipynb` (new file)

## 实现要求
1. 创建 Jupyter notebook，样式与 01-06 一致
2. 包含以下 sections：
   - 导入 Phase 1/2/3 所有模块
   - 数据加载 + 模型训练（XGBoost, LEAR — 快速训练或加载已保存模型）
   - 创建 ElectricityMarketEnv
   - PPO / TD3 / SAC 三算法训练（各 50K timesteps）
   - 3 种奖励函数对比训练
   - TensorBoard 启动说明（cell with `!tensorboard --logdir ../../tb_logs` 注释掉）
   - BacktestRunner: 压力期回测（`runner.replay("oracle", ...)`, `runner.replay(model, ...)`, `runner.replay("baseline_persistence", ...)`）
   - runner.compare() 输出对比表
   - BacktestRunner.plot_comparison() 输出累积 P&L 叠加图
   - 总结 + 思考题
3. Markdown 中文，技术术语保留英文
4. plotly 可视化
5. BCE: before current epoch — 训练/回测分离

## 接口定义（代码类任务必填）
Imports from:
- `ellectric.pipeline.data_loader`, `cleaner`, `forecaster`, `price_forecaster`
- `ellectric.pipeline.trading_env` (ElectricityMarketEnv)
- `ellectric.pipeline.rl_trainer` (RLAgentFactory)
- `ellectric.pipeline.backtester` (BacktestRunner)

## 边界处理（必填）
1. 数据不存在时给出加载/生成指引（来自 Phase 1/2 notebooks）
2. 训练较长（PPO 50K 步约 5-10 分钟）— 在 Markdown 中预估时间
3. 提供"加载已保存模型"路径（跳过重新训练）
4. TensorBoard 启动命令作为注释 cell（避免非交互运行报错）
5. compare() 中 oracle ≥ all 的断言作为 Assertion cell，失败时显示 warning 而非阻断（notebook 执行中不 raise）

## 非目标（本任务不做的事）
- 不做 SHAP 解释（Notebook 08 负责）
- 不做超参数搜索

## 参考
- 07 notebook 设计来自 design.md section 5.4 (回测引擎) 和 section 5.3 (RL 训练)
- Phase 1 的 05 notebook 中 P&L 图表风格

## TDD 步骤
1. 写 notebook → 2. nbconvert 验证 → 3. 手动检查

## 验收标准
| # | 验证步骤 | 通过标准 |
|---|----------|----------|
| AC-01 | nbconvert 成功 | 无 error |
| AC-02 | 包含 PPO/TD3/SAC 三种算法训练 cell | 三种算法各有独立 cell |
| AC-03 | 包含 BacktestRunner.replay() 和 compare() 调用 | 正确 API |
| AC-04 | 包含累积 P&L 叠加图 | plotly figure cell |
| AC-05 | 策略对比表包含总收益/夏普/胜率/最大回撤列 | 4 个指标 |
| AC-06 | notebook 可从头执行到末尾（假设数据存在） | 无语法/import 错误 |
