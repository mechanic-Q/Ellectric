---
id: task-09
title: 端到端验证：回测逻辑正确性 (oracle ≥ all)、全部 import 通过
priority: P0
estimated_hours: 1
depends_on: [task-06, task-07, task-08]
author: lmr
created_at: 2026-06-07T01:48:57+08:00
blocks: []
allowed_paths:
  - ellectric/
---

# task-09: 端到端验证

## 修改文件（必填）
- No new files. Verification only — create a shell script at `ellectric/scripts/verify_phase3.sh`

## 实现要求
1. 编写验证脚本 `verify_phase3.sh`
2. 验证所有 import 通过
3. 验证 oracle 策略逻辑（确保 oracle 的 bid = actual load）
4. 验证 notebooks 可转换
5. 验证已有模块未被修改（git diff 只包含新增文件和 requirements.txt 修改）

## 接口定义（代码类任务必填）
无（验证脚本）

## 边界处理（必填）
1. 在虚拟环境下运行验证（如果存在 .venv 则激活）
2. import 验证覆盖所有新模块
3. oracle ≥ baseline 是数学恒等式（oracle 知道真实值），如果这个断言失败说明回测逻辑有 bug
4. 验证不通过时输出清晰错误信息
5. 不影响已有模块的运行

## 非目标（本任务不做的事）
- 不生成 model 训练结果（只验证代码正确性）
- 不执行完整 notebook（只做 nbconvert 验证）

## 参考
- Phase 1 已有的 verify_assume.py 脚本风格
- design.md 的验收标准和 R-06

## TDD 步骤
1. 写验证脚本 → 2. 运行脚本 → 3. 修复问题 → 4. 重新验证

## 验收标准
| # | 验证步骤 | 通过标准 |
|---|----------|----------|
| AC-01 | bash scripts/verify_phase3.sh | 全部通过，exit 0 |
| AC-02 | 验证新模块 import | 4 个新模块全部可导入 |
| AC-03 | oracle 策略 bid = actual_load（mock 数据测试） | 断言通过 |
| AC-04 | nbconvert 三个新 notebook | 全部成功无 error |
| AC-05 | 已有 8 个 pipeline 模块未被修改 | git diff 只新增文件 |
