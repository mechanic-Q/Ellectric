
---
author: lmr
created_at: 2026-06-07T01:43:10+08:00
---

# Tasks: Phase 3 — Trading Agents + Backtesting

> 任务列表，细节在 plan 阶段展开

| # | 任务 | 文件路径 |
|---|------|----------|
| 1 | 新增依赖 gymnasium, stable-baselines3, shap, tensorboard | `ellectric/requirements.txt` |
| 2 | 实现 ElectricityMarketEnv (gymnasium.Env) | `ellectric/pipeline/trading_env.py` |
| 3 | 实现 RewardRegistry 和 3 种内置奖励函数 | `ellectric/pipeline/trading_env.py` |
| 4 | 实现 RLAgentFactory + BaseRLAgent (PPO/TD3/SAC adapters) | `ellectric/pipeline/rl_trainer.py` |
| 5 | 实现 BacktestRunner + 策略定义 (baseline/oracle) | `ellectric/pipeline/backtester.py` |
| 6 | 实现 SHAP 可解释性封装 | `ellectric/pipeline/shap_explainer.py` |
| 7 | 编写 Notebook 06 — 环境走查 + PPO 单算法训练 | `ellectric/notebooks/06_rl_trading_agent.ipynb` |
| 8 | 编写 Notebook 07 — 三算法对比 + 回测 | `ellectric/notebooks/07_multi_agent_backtest.ipynb` |
| 9 | 编写 Notebook 08 — SHAP 解释 | `ellectric/notebooks/08_model_explainability.ipynb` |
| 10 | 端到端验证：回测逻辑正确性 (oracle ≥ all), import 通过 | — |
