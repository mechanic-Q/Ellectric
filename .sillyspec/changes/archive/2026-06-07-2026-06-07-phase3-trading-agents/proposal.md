
---
author: lmr
created_at: 2026-06-07T01:43:10+08:00
---

# Proposal: Phase 3 — Trading Agents + Backtesting

## 动机

Phase 1 有了负荷预测（XGBoost），Phase 2 有了电价预测（LEAR）和市场仿真（ASSUME）。但这些预测目前只是"看"——学习者还没有把预测转化为交易决策。Phase 3 解决这个最后一公里的问题：**用预测指导电力市场的投标行为，用强化学习优化投标策略，用历史回测验证策略效果**。

核心动机不是"做一个生产级交易系统"，而是让学习者亲手体验：
- 预测如何接入交易决策
- RL 智能体如何在市场环境中学习策略
- 不同奖励函数如何塑造不同的投标行为
- 回测如何评估策略在压力场景下的表现
- ML 模型为什么做出某个预测（SHAP 可解释性）

## 关键问题

1. **预测与决策脱节**：Phase 1/2 的 XGBoost 和 LEAR 产出了预测值，但没有机制将这些预测输入到交易策略中。学习者无法回答"有了好的预测，怎么赚钱？"

2. **无策略对比框架**：没有统一的方式比较"持续法投标"vs"RL 投标"vs"完美先知投标"，无法量化策略改进的幅度。

3. **ML 黑盒问题**：XGBoost 和 LEAR 是黑盒模型，学习者不知道模型为什么预测某个值——这降低了学习深度和信任度。

## 变更范围

1. **自建电力市场交易环境** (`trading_env.py`)：gymnasium.Env，不依赖 ASSUME，最大透明度
2. **RL 智能体训练框架** (`rl_trainer.py`)：PPO/TD3/SAC 三种算法统一接口
3. **回测引擎** (`backtester.py`)：真实历史数据回放，RL vs baseline vs oracle 策略对比
4. **SHAP 可解释性** (`shap_explainer.py`)：XGBoost 和 LEAR 模型决策解释
5. **3 个新 Jupyter Notebook** (06/07/08)：完整培训路径

## 不在范围内（显式清单）

- 不做 ASSUME 框架集成（自建 gymnasium 环境）
- 不做 CLI 接口（Phase 4）
- 不做 FastAPI 端点（Phase 4）
- 不做 Grafana 仪表板（Phase 2 已完成）
- 不做多智能体博弈环境
- 不做在线学习 / 实时数据流
- 不做真实市场交易下单

## 成功标准（可验证）

1. 打开 `06_rl_trading_agent.ipynb`，运行 PPO 训练，TensorBoard 显示 reward 收敛上升
2. 打开 `07_multi_agent_backtest.ipynb`，运行回测，输出策略对比表：oracle P&L ≥ RL ≥ baseline（在某些指标上）
3. 切换奖励函数（profit_only → risk_adjusted → volume_penalty），观察投标曲线形态变化
4. 打开 `08_model_explainability.ipynb`，SHAP waterfall 图正确显示特征贡献方向和大小
5. `python -c "from ellectric.pipeline.trading_env import ElectricityMarketEnv; from ellectric.pipeline.rl_trainer import RLAgentFactory; print('imports OK')"` — 无报错
