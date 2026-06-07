
---
author: lmr
created_at: 2026-06-07T01:43:10+08:00
---

# Requirements: Phase 3 — Trading Agents + Backtesting

## 角色

| 角色 | 说明 |
|------|------|
| 学习者 | 通过 Jupyter notebooks 学习 RL 交易策略，运行训练、对比、回测和解释 |

## 功能需求

### FR-01: 电力市场交易环境

**Given** 学习者已加载历史负荷数据和电价数据（DataFrame，含 timestamp/load_mw/price_da 列）
**When** 创建 `ElectricityMarketEnv` 实例并调用 `reset()`
**Then** 返回初始观察值（包含负荷预测、电价预测、时间特征、历史出清价、账户状态）

**Given** 环境处于某个 step
**When** 调用 `step(action)` 传入 24 维投标量数组
**Then** 返回 (next_obs, reward, terminated, truncated, info)，reward 由已注册的奖励函数计算

**Given** 环境到达最后一步
**When** 调用 `step(action)`
**Then** `terminated=True`，`info` 包含累计 P&L 和交易汇总

**Given** 学习者想自定义奖励函数
**When** 传入 `reward_fn=my_custom_fn` 参数或使用 `RewardRegistry.register("my_reward", my_fn)`
**Then** 环境使用自定义函数计算每步 reward

### FR-02: RL 智能体训练 (PPO/TD3/SAC)

**Given** 已创建 `ElectricityMarketEnv`
**When** 调用 `RLAgentFactory.create("ppo", env, tensorboard_log="./tb_logs")`
**Then** 返回已初始化的 PPO 智能体实例

**Given** 已创建智能体实例
**When** 调用 `agent.train(total_timesteps=50000)`
**Then** 开始训练，TensorBoard 日志自动写入 `tensorboard_log` 目录，reward 曲线随时间步上升

**Given** 训练好的模型
**When** 调用 `agent.save("models/ppo_trader.zip")`
**Then** 模型持久化到磁盘，可通过 `RLAgentFactory.load("ppo", path)` 恢复

**Given** 三种算法各训练一个模型
**When** 调用 `agent.evaluate(env, episodes=100)`
**Then** 返回 `{"mean_reward": ..., "std_reward": ..., "episode_rewards": [...]}`

### FR-03: 历史回测

**Given** 训练好的 RL 模型和历史数据（指定时间范围）
**When** 调用 `BacktestRunner.replay(model, load_data, price_data, start, end)`
**Then** 返回 trades DataFrame（每行一个时间步，含 bid/cleared/price/pnl 列）

**Given** 多种策略的回测结果（rl_ppo, rl_td3, rl_sac, baseline_persistence, baseline_mean, oracle）
**When** 调用 `BacktestRunner.compare(results)`
**Then** 返回策略对比 DataFrame（总收益、夏普比率、胜率、最大回撤），oracle P&L ≥ 所有其他策略

**Given** 回测使用了真实历史数据
**When** 查看累计 P&L 曲线
**Then** 曲线应反映策略在所选时间段内的实际市场表现，无 look-ahead bias

### FR-04: TensorBoard 训练监控

**Given** 训练中的 RL 智能体（tb_log 已配置）
**When** 在另一个终端运行 `tensorboard --logdir ./tb_logs`
**Then** 浏览器显示 reward、loss、action distribution 等指标曲线

**Given** 多组训练实验（不同算法 / 不同奖励函数）
**When** 在 TensorBoard 中切换 run
**Then** 可以并排对比不同实验的训练曲线

### FR-05: SHAP 模型可解释性

**Given** 训练好的 XGBoostForecaster 模型和样本特征
**When** 调用 `explain_xgboost_sample(model, X, sample_idx)`
**Then** 返回 plotly Figure 显示 SHAP waterfall 图（特征贡献从基线到预测值）

**Given** 训练好的 LEARForecaster 模型
**When** 调用 `explain_lear_sample(model, X, sample_idx)`
**Then** 返回 plotly Figure 显示 SHAP 贡献分解

**Given** 多个训练好的模型
**When** 调用 `feature_importance_ranking(models, feature_names)`
**Then** 返回 DataFrame 排名表（按模型+特征的重要性排序）

### FR-06: Notebook 学习路径

**Given** 学习者打开 `06_rl_trading_agent.ipynb`
**When** 顺序执行所有 cell
**Then** 输出包含：环境走查（100 episodes 随机策略）、PPO 训练过程、奖励曲线、动作分布可视化

**Given** 学习者打开 `07_multi_agent_backtest.ipynb`
**When** 顺序执行所有 cell
**Then** 输出包含：PPO/TD3/SAC 训练对比（TensorBoard）、3 种奖励函数对比、历史回测结果（RL vs baseline vs oracle 的累计 P&L 叠加图 + 策略排名表）

**Given** 学习者打开 `08_model_explainability.ipynb`
**When** 顺序执行所有 cell
**Then** 输出包含：XGBoost SHAP waterfall 单样本解释、LEAR 系数分析、跨模型特征重要性对比

## 非功能需求

- **兼容性**: 不修改已有 6 个 pipeline 模块（data_loader/cleaner/features/forecaster/price_loader/price_forecaster/statistical_tests），新增依赖追加到 requirements.txt
- **可回退**: 删除新增的 4 个 .py 文件和 3 个 .ipynb 文件即可回退 Phase 3，不影响 Phase 1/2 功能
- **可测试**: 每个模块可独立导入；oracle 策略 P&L ≥ 所有策略作为逻辑正确性检查
- **性能**: 默认 50K timesteps PPO 训练在普通开发机（CPU）30 分钟内完成
- **依赖**: gymnasium ≥1.0, stable-baselines3 ≥2.0, shap ≥0.46, tensorboard ≥2.0, 全部兼容 Python 3.11+
