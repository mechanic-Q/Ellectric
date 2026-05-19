# Requirements: Ellectric (AI + 电力交易技术学习平台)

**Defined:** 2026-05-20
**Core Value:** 跑通"公开电力数据接入 → 负荷/电价预测 → 电力市场仿真 → 自动交易策略"的端到端技术闭环

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Environment & Setup

- [ ] **ENV-01**: 一键安装脚本，在干净 Python 3.11 环境中 30 分钟内完成所有依赖安装
- [ ] **ENV-02**: Docker Compose 配置文件，启动 TimescaleDB + Grafana（ASSUME 可视化依赖）
- [ ] **ENV-03**: Jupyter Notebook 作为主要交互界面，每个 notebook 包含：说明(Markdown) → 代码(Cell) → 可视化(Output) → 思考题

### Data Pipeline

- [ ] **DATA-01**: 从 PUDL 获取美国电力数据（负荷、发电、电厂元数据），输出为本地 SQLite/Parquet
- [ ] **DATA-02**: 实现 DataLoader 抽象类，统一数据访问接口，支持数据版本锁定
- [ ] **DATA-03**: 数据清洗管道：缺失值填充、异常值检测(IQR)、时区标准化到 UTC
- [ ] **DATA-04**: 时序特征工程：小时/星期/节日标识、滞后特征(lag features)、滚动窗口统计

### Prediction & Forecasting

- [ ] **PRED-01**: 使用 XGBoost 构建手动短期负荷预测模型，包含训练/测试集(TimeSeriesSplit)、模型持久化
- [ ] **PRED-02**: 运行 OpenSTEF 自动化预测管道，与手动 XGBoost 模型对比 MAE/RMSE/MAPE
- [ ] **PRED-03**: 使用 epftoolbox 进行日前电价预测（LEAR/DNN 模型），包含 5 个参考数据集
- [ ] **PRED-04**: 多模型对比仪表板：XGBoost vs OpenSTEF（负荷），LEAR vs DNN vs 基准（电价），交互式 plotly 图表

### Market Simulation

- [ ] **SIM-01**: 安装并运行 ASSUME 电力市场仿真，至少完成一次 7 天仿真（使用默认智能体）
- [ ] **SIM-02**: 通过 YAML 配置修改发电组合（煤/气/风/光/储能）、需求曲线、出清机制
- [ ] **SIM-03**: 场景构建器：预制场景模板（大风日、夏季高峰、储能套利），支持保存/加载
- [ ] **SIM-04**: 通过 Grafana 仪表板可视化市场出清结果（出清价格、调度、利润）

### Trading Agents

- [ ] **AGENT-01**: 将 OpenSTEF/XGBoost 预测结果接入 ASSUME 智能体的投标策略
- [ ] **AGENT-02**: 修改 ASSUME 强化学习智能体（PPO/TD3/SAC）的奖励函数，观测策略变化
- [ ] **AGENT-03**: 端到端交易回测：预测 → 投标 → 出清 → 盈亏，输出累计 P&L 图表
- [ ] **AGENT-04**: TensorBoard 监控 RL 训练过程（奖励曲线、行为曲线），包含基准策略对比

### Integration & Interface

- [ ] **INTG-01**: FastAPI 后端：集成数据查询、预测服务、策略引擎的 REST API
- [ ] **INTG-02**: CLI 命令行工具：`data fetch`、`forecast run`、`simulate start`、`backtest run`
- [ ] **INTG-03**: LangChain + Ollama(或 API) 实现自然语言交易助手：查询预测、解释决策、对比模型

### Visualization & Explainability

- [ ] **VIZ-01**: 基本时序可视化：负荷预测叠加图、误差分布直方图、电价热力图
- [ ] **VIZ-02**: 模型可解释性：XGBoost 特征重要性、SHAP 瀑布图、置换重要性

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Extended Features

- **EXT-01**: 中国电力市场数据接入（国家能源局、菏泽市开放数据、EPS 平台）
- **EXT-02**: 可再生能源发电预测（基于气象数据的风光功率预测）
- **EXT-03**: 碳排放/绿证交易市场扩展模块
- **EXT-04**: Streamlit/Gradio 轻量 Web 界面
- **EXT-05**: 多智能体博弈场景（多个 RL 智能体在同一市场中竞争）
- **EXT-06**: ASSUME 中国省级电力市场适配配置

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| 真实电力市场交易下单 | 学习项目，不涉及真实资金和法律责任 |
| 实时市场数据接入 | 需要付费 API，引入网络依赖，偏离学习目标 |
| 商业级生产系统 | 不考虑高可用、安全合规、SLA |
| 图迹 GeekBidder OS 复现 | 使用开源替代方案，不逆向商业软件 |
| 训练大模型 (GPT-scale) | 违反轻量级约束，需要 GPU 集群 |
| 碳交易市场全维度 | 显式排除，聚焦电力交易 |
| 多用户协作平台 | 单用户 Jupyter 环境，通过 git 分享 |
| 拖拽式图形投标界面 | 前端复杂度高，教育回报低 |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ENV-01 | Phase 1 | Pending |
| ENV-02 | Phase 1 | Pending |
| ENV-03 | Phase 1 | Pending |
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DATA-04 | Phase 1 | Pending |
| PRED-01 | Phase 1 | Pending |
| VIZ-01 | Phase 1 | Pending |
| PRED-02 | Phase 2 | Pending |
| PRED-03 | Phase 2 | Pending |
| PRED-04 | Phase 2 | Pending |
| SIM-01 | Phase 2 | Pending |
| SIM-02 | Phase 2 | Pending |
| SIM-03 | Phase 2 | Pending |
| SIM-04 | Phase 2 | Pending |
| AGENT-01 | Phase 3 | Pending |
| AGENT-02 | Phase 3 | Pending |
| AGENT-03 | Phase 3 | Pending |
| AGENT-04 | Phase 3 | Pending |
| VIZ-02 | Phase 3 | Pending |
| INTG-01 | Phase 4 | Pending |
| INTG-02 | Phase 4 | Pending |
| INTG-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-20*
*Last updated: 2026-05-20 after initial definition*
