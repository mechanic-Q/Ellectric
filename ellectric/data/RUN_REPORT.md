
# Ellectric 全流程运行报告

## 概要

| 指标 | 值 |
|------|-----|
| 数据源 | PJM 电力市场 (2013-01-01 00:00:00 ~ 2018-12-24 23:00:00) |
| 数据量 | 52,416 行小时级数据 |
| 训练/测试 | 41,932 / 10,484 行 |
| XGBoost MAE | 3484 MW |
| LEAR MAE | 5.75 元/MWh |
| PPO 训练步数 | 5,000 |
| PPO 评估奖励 | -153357327 ± 0 |

## 回测结果

```
         策略            总收益        夏普比率   胜率           最大回撤  交易次数
0    oracle      -0.003573 -144.750662  0.0      -0.003534   120
1    rl_ppo -211645.099659 -241.884396  0.0 -210404.301267   120
2  baseline  -56665.181876  -58.022524  0.0  -55424.383484   120
```

## 生成文件

| 文件 | 说明 |
|------|------|
| `data/demo_xgb.joblib` | 训练好的 XGBoost 负荷预测模型 |
| `data/demo_lear.joblib` | 训练好的 LEAR 电价预测模型 |
| `data/demo_ppo.zip` | 训练好的 PPO 交易智能体 |
| `data/demo_backtest.html` | 回测对比交互图 (plotly) |
| `data/demo_shap_xgb.html` | XGBoost SHAP 瀑布图 |
| `data/demo_shap_lear.html` | LEAR SHAP 瀑布图 |
| `data/demo_test_data.parquet` | 测试数据 (notebook 使用) |

## Notebook 学习路径

| Notebook | 内容 | 当前状态 |
|----------|------|----------|
| 01-05 | Phase 1: 数据加载 → 负荷预测 → 基线 | 需要 OWID 年数据 (非小时级) |
| 06_price_forecasting | Phase 2: LEAR 电价预测 | 需要中国电价数据 |
| 09_rl_trading_agent | Phase 3: RL 环境走查 + PPO 训练 | 参考本脚本 |
| 10_multi_agent_backtest | Phase 3: 三算法对比 + 回测 | 参考本脚本 |
| 11_model_explainability | Phase 3: SHAP 解释 | 参考本脚本 |

## 指标词汇表 (Glossary)

| 指标 | 英文 | 含义 | 解读 |
|------|------|------|------|
| MAE | Mean Absolute Error | 平均绝对误差 | 预测值与真实值差距的平均绝对值。越小越好 |
| RMSE | Root Mean Squared Error | 均方根误差 | 对大误差惩罚更重。RMSE > MAE 说明有异常大误差 |
| P&L | Profit & Loss | 盈亏 | 模拟交易的累计盈利/亏损。正=赚,负=亏 |
| 总收益 | Total Return | 回测期间总盈亏 | oracle≈0 说明完美投标无偏差，RL 和 baseline 为负说明偏离实际负荷 |
| 夏普比率 | Sharpe Ratio | 风险调整后收益 | =(平均收益-无风险利率)/波动率。越大越好(>1良,>2优) |
| 胜率 | Win Rate | 盈利小时占比 | 盈利小时数/总小时数。越高越好 |
| 最大回撤 | Max Drawdown | 从峰值到谷值最大跌幅 | 策略历史最高点以来的最大亏损幅度。越小越好 |
