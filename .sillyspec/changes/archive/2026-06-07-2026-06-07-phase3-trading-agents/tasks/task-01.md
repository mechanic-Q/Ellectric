---
id: task-01
title: 新增依赖 gymnasium, stable-baselines3, shap, tensorboard 到 requirements.txt
priority: P0
estimated_hours: 0.5
depends_on: []
author: lmr
created_at: 2026-06-07T01:48:57+08:00
blocks: [task-02, task-03, task-04, task-05]
allowed_paths:
  - ellectric/requirements.txt
---

# task-01: 新增依赖到 requirements.txt

## 修改文件（必填）
- `ellectric/requirements.txt`

## 实现要求
1. 在 `# ── 机器学习` 部分追加 gymnasium, stable-baselines3
2. 在 `# ── 可视化` 部分追加 shap
3. 在 `# ── 开发环境` 部分追加 tensorboard
4. 使用版本 pin: gymnasium==1.3.0, stable-baselines3==2.8.0, shap==0.46.0, tensorboard==2.18.0
5. 添加注释说明用途，与现有风格一致（`# ──` 分隔线）

## 接口定义（代码类任务必填）
无（纯依赖管理，无代码 API）

## 边界处理（必填）
1. 保持已有依赖不变（版本号不修改）
2. 新增依赖版本与 Python 3.11 兼容
3. 新增依赖不与其他已有依赖冲突
4. 添加后运行 `pip install -r requirements.txt` 无错误
5. 国内镜像注释保持不变

## 非目标（本任务不做的事）
- 不修改已有依赖的版本
- 不删除已有依赖
- 不修改 setup.sh 或其他安装脚本

## 参考
- 现有 requirements.txt 格式
- design.md 中 section 9 的兼容策略

## TDD 步骤
1. 编辑 requirements.txt
2. 运行 `pip install -r ellectric/requirements.txt` 验证安装成功
3. 运行 `python -c "import gymnasium; import stable_baselines3; import shap; import tensorboard; print('OK')"` 验证导入

## 验收标准
| # | 验证步骤 | 通过标准 |
|---|----------|----------|
| AC-01 | pip install -r requirements.txt | 无报错 |
| AC-02 | python -c "import gymnasium; print(gymnasium.__version__)" | 输出版本号 >=1.0 |
| AC-03 | python -c "import stable_baselines3; print(stable_baselines3.__version__)" | 输出版本号 >=2.8.0 |
| AC-04 | python -c "import shap; import tensorboard" | 无报错 |
| AC-05 | requirements.txt 中已有依赖版本不变 | diff 只新增 4 行 |
| AC-06 | 国内镜像注释（第3行）未被修改 | 注释保留 |
