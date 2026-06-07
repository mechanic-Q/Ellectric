---
id: task-08
title: 编写 Notebook 08 — SHAP 解释
priority: P1
estimated_hours: 3
depends_on: [task-01, task-03]
author: lmr
created_at: 2026-06-07T01:48:57+08:00
blocks: [task-09]
allowed_paths:
  - ellectric/notebooks/08_model_explainability.ipynb
---

# task-08: Notebook 08 — SHAP 解释

## 修改文件（必填）
- ADD `ellectric/notebooks/08_model_explainability.ipynb` (new file)

## 实现要求
1. 创建 Jupyter notebook，样式与 Phase 1/3 notebooks 一致
2. 包含以下 sections：
   - 导入库 + 加载数据 + 加载已训练模型（XGBoostForecaster, LEARForecaster）
   - 选择 1 个样本小时，XGBoost SHAP waterfall 图
   - XGBoost SHAP summary bar chart（top 10 features）
   - LEAR 系数柱状图 (model.coef_)
   - 跨模型特征重要性排名表 (feature_importance_ranking())
   - 讨论：为什么两个模型对同一个特征的重要性判断不同
   - 思考题
3. Markdown 中文，技术术语保留英文
4. plotly 可视化

## 接口定义（代码类任务必填）
Imports from:
- `ellectric.pipeline.shap_explainer` (explain_xgboost_sample, explain_lear_sample, feature_importance_ranking)
- `ellectric.pipeline.forecaster` (XGBoostForecaster)
- `ellectric.pipeline.price_forecaster` (LEARForecaster)

## 边界处理（必填）
1. 模型不存在时提示：先运行 Phase 1/2 notebook 生成模型（或加载默认）
2. shap 未安装时 pip install shap == 提示 （不在 notebook 内安装）
3. sample 选择使用 .iloc[0] 作为默认，可修改
4. LEAR 零系数多时 warning （Lasso 可能将大量特征压缩到零）

## 非目标（本任务不做的事）
- 不做 RL 模型的 SHAP 解释（RL 策略不适用）
- 不做 TensorBoard 集成
- 不做 Force plot（只做 waterfall + summary bar）

## 参考
- shap 官方文档: waterfall_plot, summary_plot
- Phase 1 notebook 04 的特征重要性 bar chart 风格
- 现有 plot_price_forecast() 中的系数图

## TDD 步骤
1. 写 notebook → 2. nbconvert 验证 → 3. 手动检查

## 验收标准
| # | 验证步骤 | 通过标准 |
|---|----------|----------|
| AC-01 | nbconvert 成功 | 无 error |
| AC-02 | XGBoost SHAP waterfall cell 可执行 | 生成 plotly Figure |
| AC-03 | LEAR 系数分析 cell 可执行 | 生成 plotly Figure |
| AC-04 | 特征重要性 ranking 表 | DataFrame 输出 |
| AC-05 | 包含思考题 | ≥3 道 |
