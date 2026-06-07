---
id: task-02
title: 实现 ElectricityMarketEnv (gymnasium.Env) + RewardRegistry + 3 种内置奖励函数
priority: P0
estimated_hours: 4
depends_on: [task-01]
author: lmr
created_at: 2026-06-07T01:48:57+08:00
blocks: [task-04, task-05, task-06, task-07]
allowed_paths:
  - ellectric/pipeline/trading_env.py
---

# task-02: ElectricityMarketEnv

## 修改文件（必填）
- ADD `ellectric/pipeline/trading_env.py` (new file)

## 实现要求
1. 实现 `ElectricityMarketEnv(gym.Env)` 类
2. 观察空间使用 `gym.spaces.Dict`，包含 5 个 key
3. 动作空间使用 `gym.spaces.Box(low=0, high=1, shape=(24,))`
4. 实现 `RewardRegistry` 类：`register(name, fn)` / `get(name)` / `list()` / `register_builtin()`
5. 3 种内置奖励函数：profit_only, risk_adjusted, volume_penalty
6. 出清逻辑：价格接受者，cleared = min(bid_mw, actual_load)
7. 环境使用已存在的 XGBoostForecaster 和 LEARForecaster 的 predict() 方法获取预测
8. 模块 docstring（中英双语），遵循项目约定

## 接口定义（代码类任务必填）

```python
class RewardFunction(Protocol):
    def __call__(self, cleared_volume: np.ndarray, clearing_price: np.ndarray,
                 pnl_hourly: np.ndarray, info: dict) -> float: ...

class RewardRegistry:
    @staticmethod
    def register(name: str, fn: RewardFunction) -> None: ...
    @staticmethod
    def get(name: str) -> RewardFunction: ...
    @staticmethod
    def list() -> list[str]: ...
    @staticmethod
    def register_builtin() -> None: ...

class ElectricityMarketEnv(gym.Env):
    def __init__(self, load_data: pd.DataFrame, price_data: pd.DataFrame,
                 load_forecaster, price_forecaster,
                 initial_cash: float = 0.0, max_capacity: float = 1000.0,
                 reward_fn: str | RewardFunction = "profit_only",
                 feature_engineer=None): ...
    @property
    def observation_space(self) -> gym.spaces.Dict: ...
    @property
    def action_space(self) -> gym.spaces.Box: ...
    def reset(self, *, seed: int | None = None, options: dict | None = None) -> tuple[dict, dict]: ...
    def step(self, action: np.ndarray) -> tuple[dict, float, bool, bool, dict]: ...
    def _get_prediction(self) -> tuple[np.ndarray, np.ndarray]: ...
    def _build_observation(self) -> dict: ...
    def _compute_reward(self, cleared: np.ndarray, price: np.ndarray, pnl: np.ndarray) -> float: ...
```

## 边界处理（必填）
1. 空数据/缺失值：load_data 或 price_data 为空时 __init__ 抛出 ValueError 并说明要求的最小行数
2. 不修改传入参数：__init__ 对传入 DataFrame 做 .copy()，绝不修改 caller 的原始数据
3. 预测器调用失败：_get_prediction 内部捕获预测异常，回退到 zero vector + logger.warning
4. step() 必须在 reset() 之后调用，否则 raise RuntimeError("call reset() first")
5. action 越界：np.clip(action, 0, 1) 强制到合法范围，记录 warning
6. observation_space 和 action_space 必须在 __init__ 中定义，否则 gymnasium 会报错
7. metadata 属性：`metadata = {"render_modes": []}` 必须定义
8. 奖励函数不存在时 reward_fn="nonexistent" → raise KeyError(f"Unknown reward: {reward_fn}")

## 非目标（本任务不做的事）
- 不做真实机组组合出清优化
- 不做 RL 训练（task-04 负责）
- 不做回测（task-05 负责）
- 不做自定义 render 方法

## 参考
- gymnasium.Env API: https://gymnasium.farama.org/api/env/
- stable-baselines3 的 gym.Env 指南
- 现有 forecaster.py 中的 persistence_forecast() 和 calculate_pnl() 可作为 P&L 计算参考

## TDD 步骤
1. 写测试 → 2. 确认失败 → 3. 写代码 → 4. 确认通过 → 5. 回归

## 验收标准
| # | 验证步骤 | 通过标准 |
|---|----------|----------|
| AC-01 | from ellectric.pipeline.trading_env import ElectricityMarketEnv, RewardRegistry | 无 ImportError |
| AC-02 | env = ElectricityMarketEnv(...); obs, info = env.reset() | obs 是 dict 且包含 5 个 key |
| AC-03 | obs, r, term, trunc, info = env.step(np.zeros(24)) | 返回 5 元组，r 是 float |
| AC-04 | RewardRegistry.list() 返回 ["profit_only", "risk_adjusted", "volume_penalty"] | 3 种内置奖励 |
| AC-05 | env.observation_space.contains(obs) | True |
| AC-06 | env.action_space.contains(action) | action=zeros(24) 通过 |
| AC-07 | 连续 step 直到 terminated=True | 累计 P&L 在 info 中返回 |
