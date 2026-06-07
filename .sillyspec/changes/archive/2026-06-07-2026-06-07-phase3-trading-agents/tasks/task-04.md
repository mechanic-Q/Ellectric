---
id: task-04
title: 实现 RLAgentFactory + BaseRLAgent (PPO/TD3/SAC 适配器)
priority: P0
estimated_hours: 4
depends_on: [task-01, task-02]
author: lmr
created_at: 2026-06-07T01:48:57+08:00
blocks: [task-05, task-06, task-07]
allowed_paths:
  - ellectric/pipeline/rl_trainer.py
---

# task-04: RL Agent Training Framework

## 修改文件（必填）
- ADD `ellectric/pipeline/rl_trainer.py` (new file)

## 实现要求
1. 实现 `RLAgentFactory` 类：`create(algo, env, **kwargs) → BaseRLAgent`
2. 实现 `BaseRLAgent(ABC)` 抽象基类：train/predict/save/load/evaluate
3. 实现 `SB3Adapter(BaseRLAgent)` — 内部包装 sb3 模型，对外暴露统一接口
4. 支持 PPO, TD3, SAC 三种算法
5. TensorBoard 日志目录可配置
6. evaluate() 运行多次 episode，返回 mean/std reward

## 接口定义（代码类任务必填）

```python
class BaseRLAgent(ABC):
    @abstractmethod
    def train(self, total_timesteps: int, callback: Callable | None = None) -> dict: ...
    @abstractmethod
    def predict(self, observation: dict | np.ndarray, deterministic: bool = True) -> np.ndarray: ...
    @abstractmethod
    def save(self, path: str) -> None: ...
    @abstractmethod
    def load(self, path: str, env: gym.Env | None = None) -> None: ...
    @abstractmethod
    def evaluate(self, env: gym.Env, n_episodes: int = 100) -> dict: ...

class RLAgentFactory:
    ALGORITHMS = {"ppo": PPO, "td3": TD3, "sac": SAC}

    @classmethod
    def create(cls, algo: str, env: gym.Env, tensorboard_log: str = "./tb_logs",
               policy_kwargs: dict | None = None, verbose: int = 0,
               **kwargs) -> BaseRLAgent: ...
    @classmethod
    def load(cls, algo: str, path: str, env: gym.Env | None = None) -> BaseRLAgent: ...
```

## 边界处理（必填）
1. 不支持的算法名：algo 不在 ["ppo", "td3", "sac"] 时 raise ValueError(f"Unsupported algo: {algo}. Supported: {list(cls.ALGORITHMS.keys())}")
2. create() 必须传入 env，否则 raise TypeError("env is required")
3. train() 前必须已通过 create() (非直接构造)：BaseRLAgent 不由用户直接实例化
4. predict() 在未 train 时 raise RuntimeError("模型未训练，请先调用 train()")
5. evaluate() 中环境无重置/step 错误时抛出清晰异常
6. save() 目标路径不存在时自动创建目录（os.makedirs）
7. 不修改传入的 env（保护 caller 的环境引用）
8. sb3 默认超参数保持不变（不修改默认网络结构）

## 非目标（本任务不做的事）
- 不做超参数自动调优
- 不做模型 ensemble 或多模型并行训练
- 不实现 custom policy network
- 不做奖励函数实现（由 task-02 的 RewardRegistry 提供）

## 参考
- stable-baselines3 文档: PPO, TD3, SAC API
- 现有 forecaster.py 的 XGBoostForecaster 类的 save/load 模式
- stable_baselines3.common.base_class.BaseAlgorithm

## TDD 步骤
1. 写测试 → 2. 确认失败 → 3. 写代码 → 4. 确认通过 → 5. 回归

## 验收标准
| # | 验证步骤 | 通过标准 |
|---|----------|----------|
| AC-01 | from ellectric.pipeline.rl_trainer import RLAgentFactory, BaseRLAgent | 无 ImportError |
| AC-02 | agent = RLAgentFactory.create("ppo", env) | 返回 BaseRLAgent 实例 |
| AC-03 | agent.train(total_timesteps=1000) | 完成无报错 |
| AC-04 | action = agent.predict(obs) | action shape==(24,) |
| AC-05 | agent.save("test_model.zip") + agent.load("test_model.zip") | 文件存在且加载成功 |
| AC-06 | RLAgentFactory.create("invalid") | 抛出 ValueError |
| AC-07 | RLAgentFactory.load("ppo", "nonexistent.zip") | 抛出 FileNotFoundError |
