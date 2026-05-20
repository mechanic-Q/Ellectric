"""
预测引擎 — 负荷预测与盈亏计算
==============================

本模块提供两种预测方法:
1. **持续法 (Persistence Forecast)** — 最简单的基线模型
2. **P&L 计算** — 将预测转化为模拟交易的盈亏

为什么先做持续法预测？
~~~~~~~~~~~~~~~~~~~~
在机器学习领域，"基线模型" (Baseline Model) 是用来衡量
后续复杂模型是否真正有效的参照物。

如果 XGBoost 的 MAE 是 500MW，但持续法的 MAE 是 510MW，
说明你花了很多力气，模型比"昨天=今天"就好了一点点——
这时候应该反思特征工程或模型选择是否正确。

持续法 (Persistence Forecast)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
定义: 用昨天的负荷值作为今天的预测值。
     forecast(t) = actual(t - 24h)

为什么是 24 小时？
电力负荷有极强的日周期 (Diurnal Cycle)：
- 早晨↑（人们起床）→ 中午↑（工业/商业高峰）→ 傍晚↑（回家）
- 凌晨↓（大多数人睡觉）→ 循环往复
昨天的同一时刻是今天的最好近似。

这是时序预测的最简单基线，但它出奇地有效——
在电力负荷预测中，持续法通常能做到 MAPE 3%-5%。
如果你的 XGBoost 做不到比这更好，说明还没学到日周期模式。

P&L 计算 (Profit & Loss)
~~~~~~~~~~~~~~~~~~~~~~~~
模拟交易的盈亏：假设你按照预测来"买电"，实际交付时按真实负荷"结算"。
这只是学习用的简化模型，不是真实的电力交易结算逻辑。

简化假设:
- 统一电价 $50/MWh（美国日前市场均价参考）
- 买入量 = 预测负荷
- 结算价 = 实际负荷 × 固定电价
- P&L = 实际收入 - 买入成本
"""

import pandas as pd
import numpy as np
import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


def persistence_forecast(df: pd.DataFrame) -> pd.Series:
    """
    持续法预测：用 24 小时前的负荷作为预测。

    算法: forecast[t] = actual[t - 24]

    为什么是 24？
    电力负荷有日周期——昨天下午 3 点的负荷
    是预测今天下午 3 点负荷的最好起点。

    Args:
        df: 包含 timestamp, load_mw 列的 DataFrame

    Returns:
        预测值 Series，索引与 df 相同。
        前 24 小时用后向填充补齐。
    """
    forecast = df["load_mw"].shift(24)

    # 前 24 个值没有"昨天数据"，用后向填充
    # 即用第 25 小时的值回填第 1-24 小时
    forecast = forecast.bfill()

    logger.info(f"持续法预测: 使用 24h 滞后, 共 {len(forecast)} 个预测值")
    return forecast


def calculate_pnl(
    actual: pd.Series,
    forecast: pd.Series,
    price_per_mwh: float = 50.0,
) -> pd.Series:
    """
    计算模拟交易的累计盈亏 (Cumulative P&L)。

    交易模型:
    ~~~~~~~~
    你在每个时间点"买入"预测量的电力，
    实际交付时按真实负荷"结算"。

    P&L = (实际负荷 - 预测负荷) × 电价

    解释:
    - 如果预测偏低 (actual > forecast) → 你少买了 → 需要高价补够 → 亏
    - 如果预测偏高 (actual < forecast) → 你买多了 → 浪费 → 亏
    - 预测完美 → P&L = 0
    - 但这是简化模型，真实市场有更复杂的结算规则

    为什么这里 P&L 永远是负数？
    因为简化假设下，任何偏差都会产生"惩罚"。
    真实市场中，偏差在容忍范围内是不罚的。

    Args:
        actual:   实际负荷 Series
        forecast: 预测负荷 Series
        price_per_mwh: 电价 ($/MWh)，默认 50

    Returns:
        逐小时的累计 P&L Series
    """
    # 偏差 = forecast - actual
    # 负值 = 赔了（预测不准的代价）
    # 取负数让"更准的预测"显示为"更高的 P&L"
    hourly_pnl = -(forecast - actual).abs() * (price_per_mwh / 1000.0)
    # 除以 1000 是为了让数值好看（MW 级别偏差的代价）

    cumulative = hourly_pnl.cumsum()
    logger.info(f"P&L 计算完成: 累计 {cumulative.iloc[-1]:.2f}")
    return cumulative


def plot_pnl(
    df: pd.DataFrame,
    forecast: pd.Series,
    cumulative_pnl: pd.Series,
    title: str = "端到端基线 — 持续法预测 vs 实际",
) -> go.Figure:
    """
    绘制端到端管道结果图。

    包含两个子图:
    1. 上: 负荷预测 vs 实际（时间序列叠加图）
    2. 下: 累计 P&L（盈亏曲线）

    为什么用 Plotly 而不是 matplotlib？
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Plotly 是**交互式**的——你可以：
    - 悬停查看精确数值
    - 框选放大某个时间段
    - 双击重置视图
    这对学习过程中的数据探索非常有价值。

    Args:
        df:             原始数据（含 timestamp, load_mw）
        forecast:       预测值
        cumulative_pnl: 累计盈亏
        title:          图表标题

    Returns:
        plotly Figure 对象（在 Jupyter 中自动渲染）
    """
    # 创建两个子图，共享 X 轴
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("负荷预测 vs 实际", "累计模拟盈亏"),
        row_heights=[0.6, 0.4],
    )

    # ── 子图 1: 负荷预测 vs 实际 ─────────────────
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["load_mw"],
            mode="lines",
            name="实际负荷",
            line=dict(color="#1f77b4", width=2),
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=forecast,
            mode="lines",
            name="持续法预测 (t-24h)",
            line=dict(color="#ff7f0e", width=1.5, dash="dash"),
        ),
        row=1, col=1,
    )

    # ── 子图 2: 累计 P&L ─────────────────────────
    color = "#2ca02c" if cumulative_pnl.iloc[-1] >= cumulative_pnl.iloc[0] else "#d62728"
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=cumulative_pnl,
            mode="lines",
            name="累计 P&L",
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=f"rgba({','.join(map(str, [44, 160, 44, 0.2]) if color == '#2ca02c' else [214, 39, 40, 0.2])})",
        ),
        row=2, col=1,
    )

    # ── 布局设置 ─────────────────────────────────
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        height=700,
        hovermode="x unified",  # 悬停时显示同一时间点的所有值
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title_text="时间", row=2, col=1)
    fig.update_yaxes(title_text="负荷 (MW)", row=1, col=1)
    fig.update_yaxes(title_text="盈亏 ($)", row=2, col=1)

    return fig
