---
id: task-05
title: 实现 BacktestRunner + 策略定义 (baseline_persistence, baseline_mean, oracle)
priority: P0
estimated_hours: 4
depends_on: [task-01, task-02, task-04]
author: lmr
created_at: 2026-06-07T01:48:57+08:00
blocks: [task-07, task-09]
allowed_paths:
  - ellectric/pipeline/backtester.py
---

# task-05: BacktestRunner

## 修改文件（必填）
- ADD `ellectric/pipeline/backtester.py` (new file)

## 实现要求
1. 实现 `BacktestRunner` 类
2. 实现 `replay()` 方法：逐小时回放历史数据，调用策略产生投标 → 环境出清 → 记录结果
3. 实现 `compare()` 方法：多策略对比，计算总收益/夏普比率/胜率/最大回撤
4. 3 种策略类型：baseline_persistence (t-24h), baseline_mean (168h rolling mean), oracle (actual load)
5. 输出 trades_df 列：timestamp, bid_mw, cleared_mw, clearing_price, actual_load, pnl_hourly, pnl_cumulative, strategy
6. 模块 docstring（中英双语），遵循项目约定

## 接口定义（代码类任务必填）

```python
class BacktestRunner:
    def __init__(self, env_factory: Callable[[], ElectricityMarketEnv],
                 initial_cash: float = 0.0): ...

    def replay(self, model: BaseRLAgent | str | None,
               load_data: pd.DataFrame, price_data: pd.DataFrame,
               start: str, end: str,
               strategy_name: str = "rl") -> pd.DataFrame:
        """回放历史数据
        - model: BaseRLAgent 实例 (RL策略) / "baseline_persistence" / "baseline_mean" / "oracle"
          / None 表示使用策略名字符串
        - start, end: 时间范围 "YYYY-MM-DD"
        - strategy_name: 策略名称（用于结果标记）
        - returns: trades DataFrame
        """

    def compare(self, results: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """多策略对比
        - results: {strategy_name: trades_df}
        - returns: DataFrame[策略, 总收益, 夏普比率, 胜率, 最大回撤, 交易次数]
        """

    @staticmethod
    def plot_comparison(comparison_df: pd.DataFrame,
                        title: str = "策略对比") -> go.Figure:
        """多策略累计 P&L 叠加图"""
```

## 边界处理（必填）
1. start/end 格式校验：非 "YYYY-MM-DD" 格式时 raise ValueError
2. 时间范围无数据：raise ValueError(f"数据范围 {start}~{end} 无数据")
3. load_data 和 price_data 无重叠时间范围：raise ValueError("数据无重叠")
4. oracle 策略 P&L ≥ 所有其他策略（逻辑校验，replay 完成后内部 assert — 不阻断，但记录 warning）
5. model 参数类型不合法：raise TypeError
6. 不修改传入的 load_data 和 price_data（内部做 copy）
7. 缺失值处理：bfill + ffill（与 cleaner.py 一致）
8. 文件名中不允许出现路径分隔符

## 非目标（本任务不做的事）
- 不做 RL 训练（task-04 负责）
- 不做 Gym 环境实现（task-02 负责）
- 不做超参数调优
- 不做实时回放（按小时步进逐需回放）

## 参考
- forecaster.py 的 calculate_pnl(): `-(|forecast - actual|) * price / 1000` 和 plot_pnl()
- cleaner.py 的缺失值填充：ffill + bfill
- 现有 persistence_forecast() 的 t-24h 逻辑

## TDD 步骤
1. 写测试 → 2. 确认失败 → 3. 写代码 → 4. 确认通过 → 5. 回归

## 验收标准
| # | 验证步骤 | 通过标准 |
|---|----------|----------|
| AC-01 | from ellectric.pipeline.backtester import BacktestRunner | 无 ImportError |
| AC-02 | runner = BacktestRunner(env_factory); df = runner.replay("oracle", load, price, "2022-01-01", "2022-01-07") | 返回 DataFrame 含所有列 |
| AC-03 | df 列包含: timestamp, bid_mw, cleared_mw, clearing_price, actual_load, pnl_hourly, pnl_cumulative, strategy | 列齐全 |
| AC-04 | runner.compare({"oracle": df, "baseline": df2}) | 返回 DataFrame 含收益/夏普/胜率/最大回撤 |
| AC-05 | oracle 策略总收益 ≥ baseline 策略 | 断言通过 |
| AC-06 | start > end 时 raise | ValueError |
