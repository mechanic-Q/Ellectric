
---
author: lmr
created_at: 2026-06-07T12:40:00+08:00
---

# Module Impact: Phase 3 — Trading Agents + Backtesting

## Triple Cross-Validation

| 来源 | 文件数 | 备注 |
|------|--------|------|
| design.md 声明范围 | 10 (4 模块 + 3 notebooks + 1 script + 1 deps + 1 数据) | 含 price_data.parquet(not created) |
| plan.md 任务文件 | 9 | task-01~09 |
| git diff (committed + untracked) | 12 | 实际变更 |

**结论**: 新增 4 pipeline 模块 + 3 notebooks + 1 script + modified requirements.txt。design.md 中的 `price_data.parquet` 未创建（notebook 中按需加载），属于合理偏差。

## 模块影响矩阵

| 模块 | 影响类型 | 相关文件 | 更新内容摘要 | needs_review |
|------|----------|----------|-------------|-------------|
| **(新) trading_env** | 新增 | `ellectric/pipeline/trading_env.py` | 自建 gymnasium.Env (ElectricityMarketEnv) + RewardRegistry + 3 奖励函数 | false |
| **(新) rl_trainer** | 新增 | `ellectric/pipeline/rl_trainer.py` | RLAgentFactory (PPO/TD3/SAC) + BaseRLAgent 抽象基类 | false |
| **(新) backtester** | 新增 | `ellectric/pipeline/backtester.py` | BacktestRunner + 3 策略 (persistence/mean/oracle) | false |
| **(新) shap_explainer** | 新增 | `ellectric/pipeline/shap_explainer.py` | XGBoost TreeExplainer + LEAR LinearExplainer + 特征排名 | false |
| notebooks | 新增 | `06_rl_trading_agent.ipynb` | 环境走查 + PPO 单算法训练 | false |
| notebooks | 新增 | `07_multi_agent_backtest.ipynb` | 三算法对比 + 回测 + 策略排名 | false |
| notebooks | 新增 | `08_model_explainability.ipynb` | SHAP 模型解释 | false |
| forecaster | 调用关系变更 | (未修改) | trading_env 调用 XGBoostForecaster.predict() 获取负荷预测 | true |
| price-forecaster | 调用关系变更 | (未修改) | trading_env 调用 LEARForecaster.predict() 获取电价预测 | true |
| data-loader | 调用关系变更 | (未修改) | notebooks 调用 create_loader() | false |
| cleaner | 调用关系变更 | (未修改) | notebooks 调用 clean_data() | false |
| — | 配置变更 | `ellectric/requirements.txt` | 新增 gymnasium, stable-baselines3, shap, tensorboard | false |

## 未匹配文件

| 文件 | 说明 |
|------|------|
| `ellectric/scripts/verify_phase3.sh` | 验证脚本，不属于任何 pipeline 模块。可新增模块文档。 |

## 依赖关系

```
trading_env ──call──> forecaster (XGBoostForecaster)
trading_env ──call──> price-forecaster (LEARForecaster)
rl_trainer   ──import─> stable-baselines3 (外部)
backtester   ──import─> trading_env (ElectricityMarketEnv)
backtester   ──import─> rl_trainer (BaseRLAgent)
backtester   ──import─> forecaster (calculate_pnl) [implied]
notebooks    ──import─> 全部 4 个新模块 + data-loader + cleaner + forecaster + price-forecaster
```

## 模块文档更新建议

1. **新增 4 个模块卡片**: trading_env, rl_trainer, backtester, shap_explainer
2. **更新 forecaster 模块卡片**: 新增调用者 trading_env
3. **更新 price-forecaster 模块卡片**: 新增调用者 trading_env
4. **更新 notebooks 模块卡片**: 新增 3 个 Phase 3 notebook
