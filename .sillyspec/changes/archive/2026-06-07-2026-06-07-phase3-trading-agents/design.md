
<!-- author: lmr -->
<!-- created_at: 2026-06-07T01:30:00+08:00 -->

# Phase 3 Design — Trading Agents + Backtesting

## 1. 背景

Phase 1 完成了负荷预测（XGBoost + 持续法基准），Phase 2 完成了电价预测（LEAR + epftoolbox 基准对比）和市场仿真（ASSUME）。Phase 3 将这些预测能力转化为交易决策：**用预测指导投标，用强化学习优化策略，用回测验证效果**。

核心问题：如何让机器学会"在电力市场中赚钱"——不是简单的边际成本投标，而是基于对未来价格和负荷的预测，在日前市场提交最优投标量。

## 2. 设计目标

1. 自建轻量 gymnasium 电力交易环境，学习者可透明理解 RL 训练闭环
2. 覆盖 PPO / TD3 / SAC 三种主流 RL 算法，统一训练和评估接口
3. 回测引擎支持真实历史数据回放，对比 RL vs 基准策略 vs 先知策略
4. SHAP 可解释性：解释 XGBoost 负荷预测和 LEAR 电价预测的决策依据
5. 全部在 Jupyter notebooks 中完成，零 CLI/API 依赖

## 3. 非目标

- 不用 ASSUME 内部 RL 框架（自建环境，最大化学习透明度）
- 不做 CLI 接口（Phase 4 才引入 `ellectric backtest run` 等命令）
- 不做 FastAPI 端点（Phase 4）
- 不做 Grafana 仪表板（Phase 2 已完成）
- 不做真实交易（学习项目，无真实资金）
- 不做多智能体博弈（Phase 3 聚焦单智能体在固定市场环境中的策略学习）
- 不做在线学习 / 实时数据流

## 4. 拆分判断

| 条件 | 本变更 | 结论 |
|------|--------|------|
| 3+ 可独立交付模块 | trading_env, rl_trainer, backtester, shap_explainer — 4 个模块但紧密耦合 | 否 |
| 3+ 角色/权限 | 单一学习者角色 | 否 |
| 跨页面状态流转 | 无，全部 Notebook | 否 |
| 模块间低耦合 | 强耦合：环境 → 训练 → 回测 → 评估 | 合并不拆 |

**结论：无需拆分。** 4 个模块的依赖链是线性的（env 供 trainer 和 backtester 使用，shap_explainer 独立），拆分反而增加上下文切换成本。

## 5. 总体方案

### 5.1 架构（5 层）

```
┌──────────────────────────────────────────────┐
│  Layer 5: 评估与可视化 (notebooks)            │
│  P&L 曲线 · SHAP 瀑布图 · TensorBoard         │
├──────────────────────────────────────────────┤
│  Layer 4: 回测引擎 (backtester.py)             │
│  历史数据回放 → 策略执行 → 出清 → P&L 计算     │
├──────────────────────────────────────────────┤
│  Layer 3: RL 训练层 (rl_trainer.py)            │
│  PPO / TD3 / SAC 统一接口 · 奖励注册表          │
├──────────────────────────────────────────────┤
│  Layer 2: 交易环境 (trading_env.py)             │
│  gymnasium.Env · 观察空间 · 动作空间 · 出清逻辑  │
├──────────────────────────────────────────────┤
│  Layer 1: 预测层（复用 Phase 1 + 2）            │
│  XGBoost 负荷预测 + LEAR 电价预测 → 特征向量    │
└──────────────────────────────────────────────┘
```

### 5.2 Layer 2: ElectricityMarketEnv（gymnasium.Env）

**观察空间 (Dict 或 Box)**:
- 负荷预测值 `load_forecast_24h` (24,) — 来自 XGBoostForecaster.predict()
- 电价预测值 `price_forecast_24h` (24,) — 来自 LEARForecaster.predict()
- 时间特征 `time_features` (4,) — [hour_sin, hour_cos, day_of_week, is_weekend]
- 历史出清价 `price_history_168h` (168,) — 过去一周的每小时实际电价
- 账户状态 `account_state` (2,) — [current_position, cumulative_pnl]

**动作空间**: Box(low=0, high=1, shape=(24,)) — 24 小时归一化投标量 [0, 1]，运行时映射到 [0, max_capacity] MW

**奖励函数（可插拔）**:
```python
class RewardFunction(Protocol):
    def __call__(self, cleared_volume: np.ndarray, clearing_price: np.ndarray,
                 pnl: np.ndarray, info: dict) -> float:
        ...
```

三种内置奖励：
| 名称 | 公式 | 用途 |
|------|------|------|
| `profit_only` | Σ(出清量 × 出清价) | 纯利润最大化 |
| `risk_adjusted` | profit — λ × σ(hourly_returns) | 风险调整（夏普比惩罚） |
| `volume_penalty` | profit — α × count_zero_volume | 惩罚零成交量闲置 |

**出清逻辑（简化）**:
- 不做完整机组组合优化
- 用历史真实出清价 `P_clear[t]`（来自数据）作为市场出清价
- 智能体是价格接受者：投标量按当局真实出清价成交
- `cleared_volume[t] = min(bid_volume[t], demand[t])` — 供给侧上限

### 5.3 Layer 3: RL Trainer

```python
class RLAgentFactory:
    """统一创建 PPO / TD3 / SAC 智能体"""
    @staticmethod
    def create(algo: str, env: gym.Env, **kwargs) -> "BaseRLAgent":
        ...

class BaseRLAgent(ABC):
    def train(self, timesteps: int) -> None: ...
    def predict(self, obs: np.ndarray) -> np.ndarray: ...
    def save(self, path: str) -> None: ...
    def load(self, path: str) -> None: ...
    def evaluate(self, env: gym.Env, episodes: int) -> dict: ...
```

- PPO: `stable_baselines3.PPO` — 在线策略，适用于连续动作空间
- TD3: `stable_baselines3.TD3` — 离线策略，双 Q 网络减少高估偏差
- SAC: `stable_baselines3.SAC` — 熵正则化，自动探索-利用平衡
- 所有模型共享 `BaseRLAgent` 接口（适配器模式包装 sb3）

**TensorBoard 集成**: sb3 原生支持 `tensorboard_log` 参数，自动记录 reward、loss、action distribution

### 5.4 Layer 4: 回测引擎

```python
class BacktestRunner:
    def load_historical(self, start: str, end: str) -> pd.DataFrame: ...
    def replay(self, env: ElectricityMarketEnv, model: BaseRLAgent,
               strategy_name: str) -> pd.DataFrame: ...
    def compare(self, results: dict[str, pd.DataFrame]) -> pd.DataFrame: ...
```

**三种策略类型**:
| 策略 | 描述 | 实现 |
|------|------|------|
| `baseline_persistence` | t-24h 投标量，电力日周期简单重复 | 模块级函数 |
| `baseline_mean` | 过去 7 天平均负荷作为投标量 | 模块级函数 |
| `rl_ppo/td3/sac` | 加载训练好的 RL 模型 | RLAgentFactory |
| `oracle` | 已知真实负荷，完美投标（理论上界） | 模块级函数 |

**回测流程**:
1. `load_historical(start, end)` — 加载真实负荷 + 电价数据（Phase 1/2 已有 loader）
2. 逐小时遍历历史数据：预测 → 投标 → 出清 → 记账 → 推进到下一小时
3. 输出：`trades_df`（timestamp, bid_mw, cleared_mw, price, pnl）, 累计 P&L, Sharpe

### 5.5 Layer 5: SHAP 可解释性

```python
# shap_explainer.py 模块函数
def explain_xgboost(model, X_sample, feature_names) -> go.Figure: ...
def explain_lear(model, X_sample, feature_names) -> go.Figure: ...
def feature_importance_ranking(models: dict) -> pd.DataFrame: ...
```

- 使用 `shap.TreeExplainer` (XGBoost) 和 `shap.LinearExplainer` (Lasso/LEAR)
- 输出 plotly 图表（与现有代码风格一致）
- 单样本 waterfall 图 + 全局 summary bar chart

## 6. 文件变更清单

| 操作 | 文件路径 | 说明 |
|------|----------|------|
| 新增 | `ellectric/pipeline/trading_env.py` | ElectricityMarketEnv (gymnasium.Env) + RewardRegistry |
| 新增 | `ellectric/pipeline/rl_trainer.py` | RLAgentFactory + BaseRLAgent + PPO/TD3/SAC wrappers |
| 新增 | `ellectric/pipeline/backtester.py` | BacktestRunner + 策略定义 (baseline/oracle) |
| 新增 | `ellectric/pipeline/shap_explainer.py` | SHAP 分析封装 (TreeExplainer + LinearExplainer) |
| 新增 | `ellectric/notebooks/06_rl_trading_agent.ipynb` | 环境走查 + PPO 单算法完整训练 |
| 新增 | `ellectric/notebooks/07_multi_agent_backtest.ipynb` | 三算法对比 + 回测 + 策略排名 |
| 新增 | `ellectric/notebooks/08_model_explainability.ipynb` | SHAP 分析 + 特征重要性 |
| 修改 | `ellectric/requirements.txt` | 新增 gymnasium, stable-baselines3, shap, tensorboard |
| 新增 | `ellectric/data/price_data_hourly.parquet` | 真实历史电价数据（用于回测），数据源说明见 notebook |

## 7. 接口定义

### 7.1 ElectricityMarketEnv

```python
class ElectricityMarketEnv(gym.Env):
    def __init__(self, load_data: pd.DataFrame, price_data: pd.DataFrame,
                 initial_cash: float = 0.0, max_capacity: float = 1000.0,
                 reward_fn: str | Callable = "profit_only"):
        ...

    @property
    def observation_space(self) -> gym.spaces.Dict: ...
    @property
    def action_space(self) -> gym.spaces.Box: ...

    def reset(self, seed=None, options=None) -> tuple[dict, dict]: ...
    def step(self, action: np.ndarray) -> tuple[dict, float, bool, bool, dict]: ...

    def get_prediction(self, horizon: int = 24) -> tuple[np.ndarray, np.ndarray]:
        """获取未来 horizon 小时的负荷和电价预测"""
        ...
```

### 7.2 RLAgentFactory

```python
class RLAgentFactory:
    ALGORITHMS = {"ppo": PPO, "td3": TD3, "sac": SAC}

    @classmethod
    def create(cls, algo: str, env: gym.Env, tensorboard_log: str = "./tb_logs",
               **kwargs) -> BaseRLAgent: ...
    @classmethod
    def load(cls, algo: str, path: str, env: gym.Env = None) -> BaseRLAgent: ...
```

### 7.3 BacktestRunner

```python
class BacktestRunner:
    def __init__(self, env: ElectricityMarketEnv, initial_cash: float = 0.0): ...

    def replay(self, model: BaseRLAgent, load_data: pd.DataFrame,
               price_data: pd.DataFrame, start: str, end: str,
               strategy_name: str = "rl") -> pd.DataFrame: ...

    def compare(self, results: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """策略对比表：总收益、夏普比率、胜率、最大回撤"""
        ...
```

### 7.4 shap_explainer 模块函数

```python
def explain_xgboost_sample(model: XGBoostForecaster, X: pd.DataFrame,
                           sample_idx: int) -> go.Figure: ...
def explain_lear_sample(model: LEARForecaster, X: pd.DataFrame,
                        sample_idx: int) -> go.Figure: ...
def feature_importance_ranking(models: dict[str, Any],
                               feature_names: list[str]) -> pd.DataFrame: ...
```

### 7.5 预测器接口（复用，不修改）

已有接口作为数据合约：
- `XGBoostForecaster.predict(X) → np.ndarray` (forecaster.py:341)
- `LEARForecaster.predict(X) → np.ndarray` (price_forecaster.py:341)
- `persistence_forecast(df) → pd.Series` (forecaster.py)

## 8. 数据模型

### 8.1 环境状态（内存中）

```python
env_state = {
    "current_timestep": int,      # 当前小时索引
    "total_timesteps": int,       # 总小时数
    "load_history": np.ndarray,   # (168,) 过去一周负荷
    "price_history": np.ndarray,  # (168,) 过去一周电价
    "position": float,            # 当前持仓 (MW)
    "cash": float,                # 累计 P&L
}
```

### 8.2 回测输出 DataFrame 列

| 列名 | 类型 | 说明 |
|------|------|------|
| `timestamp` | datetime64[ns] | 小时时间戳 |
| `bid_mw` | float64 | 投标量 (MW) |
| `cleared_mw` | float64 | 出清量 (MW) |
| `clearing_price` | float64 | 出清价 (元/MWh) |
| `actual_load` | float64 | 实际负荷 (MW) |
| `pnl_hourly` | float64 | 小时 P&L |
| `pnl_cumulative` | float64 | 累计 P&L |
| `strategy` | str | 策略名称 |

## 9. 兼容策略（Brownfield）

- **不修改已有模块**：`data_loader.py`, `cleaner.py`, `features.py`, `forecaster.py`, `price_loader.py`, `price_forecaster.py`, `statistical_tests.py` 保持不变
- **新增依赖**：`gymnasium`, `stable-baselines3`, `shap`, `tensorboard` 追加到 `requirements.txt`
- **Notebook 编号延续**：Phase 1 有 `01-05`，Phase 2 notebook（如有）编号在其后，Phase 3 用 `06/07/08`
- **回退路径**：新增模块全部独立文件，删除 `.py` 文件和对应的 `.ipynb` 即可回退
- **数据合约不变**：新模块消费 `timestamp`, `load_mw`, `price_da` 列，不修改已有列定义

## 10. 风险登记

| 编号 | 风险 | 等级 | 应对策略 |
|------|------|------|----------|
| R-01 | 真实历史数据质量差（缺失、异常值），导致 RL 训练不稳定 | P1 | 复用 Phase 1 cleaner 的缺失值填充和 IQR 检测；notebook 开头展示数据质量报告 |
| R-02 | sb3 训练速度慢（CPU-only），PPO/TD3/SAC 三种算法 + 回测 run 时间过长 | P1 | 设置默认 `total_timesteps=50_000`（30 分钟内可完成）；notebook 提供参数调优建议 |
| R-03 | gymnasium 动作空间离散化与连续 RL 算法不匹配 | P2 | 使用 `Box(shape=(24,))` 连续空间 + SAC/PPO/TD3 均原生支持连续动作；如需离散投标则在 notebook 讨论 |
| R-04 | SHAP 计算开销大（24 小时 × 多特征），notebook 运行缓慢 | P2 | 限定 SHAP analysis 到单样本 + 全局 summary；用 `shap.sample(X, 100)` 降采样 |
| R-05 | 三种 RL 算法超参数不一致，对比不公平 | P2 | 使用 sb3 默认超参数 + 统一 total_timesteps；notebook 说明"本对比用于学习，非严格 benchmark" |
| R-06 | 回测引擎状态管理 bug（时间步推进错误导致 look-ahead bias） | P0 | reference test：oracle 策略的 P&L 应严格 ≥ 基线策略；写 assert 验证 |
| R-07 | 电价数据单位不一致（中国现货电价单位可能是元/MWh vs 模拟假设） | P1 | 在 backtester 入口做单位标准化；notebook 显式展示数据预览和单位说明 |

## 11. 自审

### 需求覆盖
- [x] AGENT-01: 预测接入交易 — ElectricityMarketEnv 自动加载 XGBoost/LEAR 预测
- [x] AGENT-02: 奖励函数可修改 — RewardFunction Protocol + 3 种内置 + 自定义注入
- [x] AGENT-03: 历史回测 + P&L 对比 — BacktestRunner (RL vs baseline vs oracle)
- [x] AGENT-04: TensorBoard 训练监控 — sb3 原生 tensorboard_log
- [x] VIZ-02: SHAP 可解释性 — shap_explainer.py (waterfall + summary + ranking)

### 约束一致性
- [x] Python 3.11+：gymnasium 1.3.0 / sb3 2.8.0 / shap 均支持 3.11+
- [x] 命名约定：模块 docstring (中英双语), 数据合约 (timestamp/load_mw), logger 标准化
- [x] 工厂模式：RLAgentFactory 类比 create_loader()
- [x] 预测器接口统一：train_evaluate/predict/save/load
- [x] Notebook 延续：编号 06/07/08，含思考题

### 真实性
- [x] 已有类/方法名来自真实代码：XGBoostForecaster (forecaster.py:126), LEARForecaster (price_forecaster.py), TimeSeriesSplit (forecaster.py:275)
- [x] 新模块标注为"新增"：trading_env.py, rl_trainer.py, backtester.py, shap_explainer.py

### YAGNI 检查
- [x] 无多智能体博弈（Phase 3 范围外）
- [x] 无 CLI 接口（Phase 4）
- [x] 无 FastAPI 端点（Phase 4）
- [x] 无 GPU 加速（约束：普通开发机）
- [x] 无 ASSUME 集成（方案 B 明确不依赖）

### 验收标准（具体可测试）
- [x] 打开 06_notebook，运行 PPO 训练 50K steps，TensorBoard 显示 reward 上升曲线
- [x] 打开 07_notebook，运行回测，输出策略对比表（RL > baseline 至少在某些指标上）
- [x] oracle 策略 P&L ≥ 所有其他策略（逻辑正确性）
- [x] 打开 08_notebook，SHAP waterfall 图正确显示特征贡献方向
- [x] all imports pass：gymnasium, stable_baselines3, shap, tensorboard

### 非目标清晰
- [x] 不做 ASSUME 内部 RL 框架使用
- [x] 不做 CLI / API
- [x] 不做多智能体
- [x] 不做实时数据

### 兼容策略
- [x] 不修改已有 6 个 pipeline 模块
- [x] 新依赖追加到 requirements.txt 末尾（不替换已有版本）
- [x] 回退路径明确（删除新文件 + 移除新依赖）

### 风险识别
- [x] P0 (R-06): look-ahead bias — 有明确的回测逻辑纠正 + oracle test 验证
- [x] P1 (R-01/R-02/R-07): 数据质量/训练速度/单位 — 有对应缓解措施
- [x] P2 (R-03/R-04/R-05): 非阻塞风险 — 有 notebook 说明引导

**自审结论：通过。** 11 项检查全部满足，无 ⚠️ 存疑项。
