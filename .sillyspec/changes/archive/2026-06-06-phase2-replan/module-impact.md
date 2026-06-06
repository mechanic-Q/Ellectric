---
author: lmr
created_at: 2026-06-06T21:00:00+08:00
---

# 模块影响分析

## 变更摘要

本次变更为 Phase 2 计划修正，5 份 `.planning/` 文档修改。epftoolbox 降级为基准数据源 + sklearn.Lasso 替代 LEAR 实现 + 中国电价数据接入 + ASSUME 中国省间现货规则。

## 模块影响矩阵

无代码模块受影响 — 5 个变更文件均为项目计划文档，不在模块映射范围内。

| 模块 | 影响类型 | 相关文件 | 更新内容摘要 | needs_review |
|------|----------|----------|-------------|--------------|
| — | — | — | — | — |

## 未匹配文件

| 文件路径 | 说明 | 归类原因 |
|----------|------|----------|
| `.planning/REQUIREMENTS.md` | 新增 DATA-05 + 重写 PRED-03 + 修正 SIM-02 | 项目计划文档，非代码模块 |
| `.planning/ROADMAP.md` | Phase 2 标题/目标/成功标准中国化 | 项目计划文档，非代码模块 |
| `.planning/research/STACK.md` | epftoolbox 降级 + sklearn.Lasso 新增 | 技术调研文档，非代码模块 |
| `.planning/research/SUMMARY.md` | 关闭 epftoolbox gap + ASSUME 中国配置 | 调研总结文档，非代码模块 |
| `.planning/phases/01-data-foundation-basic-prediction/01-RESEARCH.md` | 新增 Section 9 LEAR gap 已解决 | Phase 1 调研文档，非代码模块 |

## 间接影响

- **Phase 2 执行阶段**将受本次计划修正指导：LEAR 实现用 sklearn.Lasso 替代 epftoolbox TF 版本，电价数据使用 ZionLuo 中国数据集，ASSUME 仿真配置中国省间现货规则
- **Phase 1 源码**无影响 — 未修改任何 Python 文件
- **模块文档**无影响 — 所有 pipeline 模块（data-loader/cleaner/feature-engineer/forecaster）和 notebooks 模块未变更
