---
id: task-03
title: 实现 SHAP 可解释性封装（XGBoost TreeExplainer + LEAR LinearExplainer）
priority: P1
estimated_hours: 2
depends_on: [task-01]
author: lmr
created_at: 2026-06-07T01:48:57+08:00
blocks: [task-08]
allowed_paths:
  - ellectric/pipeline/shap_explainer.py
---

# task-03: SHAP 可解释性

## 修改文件（必填）
- ADD `ellectric/pipeline/shap_explainer.py` (new file)

## 实现要求
1. 实现 `explain_xgboost_sample()` — 使用 shap.TreeExplainer，返回 plotly waterfall
2. 实现 `explain_lear_sample()` — 使用 shap.LinearExplainer，返回 plotly waterfall
3. 实现 `feature_importance_ranking()` — 跨模型特征重要性 DataFrame
4. 所有函数返回 plotly Figure 或 pandas DataFrame（与现有代码风格一致）
5. 模块 docstring（中英双语）

## 接口定义（代码类任务必填）

```python
def explain_xgboost_sample(
    model: "XGBoostForecaster",
    X: pd.DataFrame,
    sample_idx: int = 0,
    max_display: int = 15,
) -> go.Figure:
    """XGBoost 单样本 SHAP waterfall 图
    - model: XGBoostForecaster 实例（_model 属性为 XGBRegressor）
    - X: 特征 DataFrame（含 _feature_cols）
    - sample_idx: 解释哪一行
    - returns: plotly Figure (waterfall)
    """

def explain_lear_sample(
    model: "LEARForecaster",
    X: pd.DataFrame,
    sample_idx: int = 0,
    max_display: int = 15,
) -> go.Figure:
    """LEAR 单样本 SHAP waterfall 图
    - model: LEARForecaster 实例（_model 属性为 Lasso）
    - X: 特征 DataFrame（含 _feature_cols）
    - sample_idx: 解释哪一行
    - returns: plotly Figure (waterfall)
    """

def feature_importance_ranking(
    models: dict[str, Any],
    feature_names: list[str],
) -> pd.DataFrame:
    """跨模型特征重要性排名
    - models: {"XGBoost": xgb_model, "LEAR": lear_model}
    - feature_names: 所有特征名列表
    - returns: DataFrame[model, feature, importance]
    """
```

## 边界处理（必填）
1. shap 包未安装时在模块顶部 try/except ImportError 捕获，raise RuntimeError("shap 未安装") — 与项目 optional dep 模式一致
2. sample_idx 越界：超出 X 行数时 raise IndexError(f"sample_idx {sample_idx} > {len(X)}")
3. X 为空 DataFrame 时 raise ValueError("X is empty")
4. model._model 未训练（None）：raise RuntimeError("模型未训练")
5. 不修改传入的 model 或 X：不做任何 inplace 操作
6. max_display 小于 1 时使用默认值 10
7. 特征名不匹配时记录 warning
8. shap 计算失败时捕获异常并转为 logger.error + 重抛 RuntimeError

## 非目标（本任务不做的事）
- 不做 force_plot 或 beeswarm plot（只在 notebook 08 中用 waterfall + summary bar）
- 不保存 SHAP 计算结果到文件
- 不修改 XGBoostForecaster 或 LEARForecaster 已有代码

## 参考
- shap.Explainer, shap.TreeExplainer, shap.LinearExplainer
- plotly.graph_objects.Figure 和 Bar trace
- 现有 forecaster.py 中 plot_forecast() 的 plotly 风格
- 现有 features.py 中 try/except ImportError 模式

## TDD 步骤
1. 写测试 → 2. 确认失败 → 3. 写代码 → 4. 确认通过 → 5. 回归

## 验收标准
| # | 验证步骤 | 通过标准 |
|---|----------|----------|
| AC-01 | from ellectric.pipeline.shap_explainer import explain_xgboost_sample, explain_lear_sample | 无 ImportError |
| AC-02 | 用训练好的 XGBoostForecaster 和样本数据调用 explain_xgboost_sample() | 返回 go.Figure |
| AC-03 | 用训练好的 LEARForecaster 和样本数据调用 explain_lear_sample() | 返回 go.Figure |
| AC-04 | feature_importance_ranking({"XGB": xgb, "LEAR": lear}, ["feat1", "feat2"]) | 返回 DataFrame[model, feature, importance] |
| AC-05 | 未训练的模型 raise | RuntimeError |
| AC-06 | sample_idx 越界 raise | IndexError |
