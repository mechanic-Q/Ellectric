# Feature Research

**Domain:** AI-driven electricity trading learning platform
**Researched:** 2026-05-20
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = the learning platform feels broken — you can't teach electricity trading without them.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Public Data Ingestion Pipeline** | Every ML/energy project starts with data. Without clean data, nothing else works. | MEDIUM | Use PUDL (US EIA data, SQLite/Parquet outputs) as primary source; supplement with IEA Real-Time Electricity Tracker. Build Python scripts that: (a) download PUDL data via Zenodo DOI or Kaggle, (b) load into local SQLite, (c) provide a `DataLoader` class abstracting access. Include data version pinning for reproducibility. |
| **Data Cleaning & Preprocessing** | Raw energy data has gaps, outliers, timezone issues. Learners must see realistic data wrangling. | MEDIUM | Leverage `enda` for time-series gap detection, resampling, contract-to-timeseries conversion. Build reusable cleaning pipelines: missing value imputation, outlier detection (IQR), timestamp normalization to UTC. Expose via Jupyter notebooks with before/after visuals. |
| **Load Forecasting (ML Pipeline)** | Core skill: predict electricity demand from weather, calendar, historical patterns. | HIGH | Two-tier approach: (a) **Manual model**: XGBoost with feature engineering (hour-of-day, day-of-week, holiday flags, lag features) for pedagogical clarity; (b) **Automated pipeline**: OpenSTEF for comparison. Must include training/test split, backtesting, model persistence. Evaluation metrics: MAE, RMSE, MAPE. |
| **Price Forecasting** | Electricity price forecasting is the other half of the prediction problem — without it, you can't make trading decisions. | MEDIUM | Use `epftoolbox` for benchmark models (LEAR, DNN) on day-ahead markets. Include 5 reference datasets (EPEX-BE/FR/DE, NordPool, PJM). Must provide comparison against naive baselines (persistence, weekly-average). |
| **Market Simulation Environment** | Trading happens in markets. Learners need a sandbox to safely experiment with market dynamics. | HIGH | Use ASSUME framework as the core simulation engine. Runs agent-based electricity market simulations with configurable: generation mix (coal, gas, wind, solar, storage), demand profiles, market clearing mechanism (pay-as-clear, pay-as-bid), grid topology. Include Grafana dashboards via Docker Compose for result visualization. |
| **Results Visualization** | Learners need to SEE what happened — bids, clears, profits, forecast accuracy. | LOW-MEDIUM | Time-series charts (matplotlib/plotly): load vs forecast overlay, price heatmaps, agent P&L over time. Must work in Jupyter notebooks. Include pre-built plotting utilities that take standard data shapes. |
| **Jupyter Notebook as Primary Interface** | The default interface for data science education. Notebooks are the "lab bench" for this platform. | LOW | Provide a set of well-documented notebooks organized by learning stage. Each notebook: markdown explanation → code cell → output visualization → reflection questions. Support both local Jupyter and Google Colab. |
| **Environment Setup Tooling** | Beginners can't learn if they spend 3 days installing dependencies. | LOW | `requirements.txt` or `environment.yml` with pinned versions. Docker Compose for database + Grafana. One-command setup: `make install` or `docker compose up`. Include CUDA-free path for CPU-only machines. |

### Differentiators (What Makes It Educational)

Features that set this learning platform apart from just reading docs. These create the "aha moments" that make a learning project valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **RL Trading Agent Sandbox** | Learners modify reward functions, observe emergent bidding strategies, understand the RL→trading connection. This is the core "cool factor" of the platform. | HIGH | Leverage ASSUME's built-in DRL capabilities (PPO, TD3, SAC agents). Provide pre-built notebook templates where learners: (a) change the reward function (profit-only vs risk-adjusted), (b) observe agent behavior change via TensorBoard, (c) compare RL agent vs rule-based baselines. Expose hyperparameters as notebook variables (learning rate, discount factor, exploration rate). |
| **LLM-Powered Trading Assistant** | Natural language interface to query predictions, explain market conditions, and interpret agent decisions. Makes the system feel "smart" and lowers the barrier for non-coders. | MEDIUM | Build with LangChain + local/open-source LLM API (e.g., Ollama with DeepSeek/Qwen, or OpenAI API as fallback). Capabilities: (a) "What is the predicted load for tomorrow at 6pm?" → queries forecast DB, (b) "Explain why the RL agent bid high at hour 18" → retrieves agent state + feature importance, (c) "Compare my XGBoost model against OpenSTEF" → runs comparison and summarizes. Use structured output (JSON function calling) for reliable data retrieval. |
| **Multi-Model Comparison Dashboard** | Side-by-side comparison of different forecasting approaches teaches model selection skills that raw metrics alone don't convey. | MEDIUM | Interactive plotly dashboard comparing: XGBoost vs OpenSTEF vs LSTM for load; LEAR vs DNN vs naive for price. Show residual distributions, error-by-hour heatmaps, and highlight where each model fails. This is where learning happens — "why did my model fail at peak hours?" |
| **Scenario Builder** | Learners design their own market scenarios: change renewable penetration, add storage, modify demand patterns, and watch market dynamics shift. | HIGH | Use ASSUME's YAML-based scenario configuration as foundation. Build a notebook-based builder that: (a) lets learners specify generation fleet composition, (b) load demand profiles from data, (c) run simulation and compare outcomes. Save/load scenario presets. Pre-built scenarios: "High Wind Day", "Summer Peak", "Storage Arbitrage". |
| **Model Explainability Tools** | Understanding WHY a model predicts something is more educational than the prediction itself. SHAP values, feature importance, partial dependence plots. | MEDIUM | Integrate SHAP for tree models (XGBoost) and permutation importance for black-box models. Every forecasting notebook includes a "Why did the model predict this?" section with SHAP waterfall plots showing top contributing features. |
| **Guided Learning Path with Milestones** | Structured progression keeps learners from getting lost. Each stage has clear success criteria and produces a working artifact. | LOW | Four-stage path matching PROJECT.md: (1) Warm-up: manual XGBoost → pass when MAE < threshold; (2) Deep Dive: OpenSTEF + ASSUME first simulation → pass when you've run a 7-day simulation; (3) Agent Building: RL agent beats rule-based baseline → pass when cumulative profit > baseline; (4) Integration: LLM can query your system → pass when natural language queries return correct data. |
| **End-to-End Trading Backtest** | The "full stack" experience: forecast → bid → market clear → P&L calculation. Learners see the entire trading loop in action. | HIGH | Wire OpenSTEF predictions into ASSUME agent's bidding strategy. Run multi-day backtests. Output: cumulative P&L chart, win/loss heatmap by hour, strategy Sharpe ratio. This is the capstone feature that ties everything together. |

### Anti-Features (Things to Deliberately NOT Build)

Features that seem attractive but would undermine the learning purpose, create maintenance burden, or cross the line into production systems.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Real-Time Market Data Feeds** | Requires paid API subscriptions, introduces network dependency, shifts focus from learning to "keeping the pipeline running." Also enters production territory. | Use static, versioned datasets from PUDL/IEA/epftoolbox. Learners can download once and work offline. Data freshness is not the point — understanding patterns is. |
| **Automated Trading Execution (Real Money)** | Legal liability, financial risk, ethical concerns. This is a learning platform, not a trading bot deployed to production. | All trading is in simulation (ASSUME). Make this explicit in every notebook: "THIS IS A SIMULATION. No real money is involved." |
| **Proprietary Data Scraping or Web Crawling** | Legal risk from scraping commercial data sources. Maintenance burden from fragile scrapers breaking when websites change. | Only use data from sources with explicit open-access terms: PUDL (CC-BY-4.0), IEA open data, epftoolbox datasets. Document data licenses clearly. |
| **Full SaaS Web Application** | Massive scope creep. Web auth, user management, database scaling, deployment — all irrelevant to learning energy AI. Diverts effort from educational content. | Keep it as Jupyter notebooks + FastAPI backend + CLI. If a web UI is needed later, add a lightweight Streamlit/Gradio wrapper, not a full React app. |
| **Carbon Market / Emissions Trading** | PROJECT.md explicitly scopes this out. Carbon markets have different dynamics (cap-and-trade vs energy-only), different data sources, different regulatory frameworks. | Focus single-mindedly on electricity markets. If successful, carbon markets can be a Phase 5 extension. |
| **Training Large Models (GPT-scale)** | Violates the "lightweight model" constraint. Requires GPU clusters, terabytes of data, weeks of training — not achievable on a development laptop. | Use XGBoost, small LSTMs, and RL with modest observation/action spaces (ASSUME's default agents). The educational value is in the architecture and workflow, not model size. |
| **Graphical Bidding Interface (Drag-and-Drop)** | Complex frontend work with minimal educational payoff. The learning is in the code and strategy logic, not in a pretty UI. | Bidding strategies are expressed as Python functions/configs. Use Streamlit for light interactivity if needed. |
| **Multi-User Collaboration Features** | User accounts, sharing, permissions — entire product category unrelated to energy AI learning. | Single-user Jupyter environment. If collaboration is desired, learners share notebooks via git, not a built-in platform. |

## Feature Dependencies

```
Data Ingestion Pipeline
    ├──requires──> Public Data Sources (PUDL, IEA)
    └──feeds──> Data Cleaning Pipeline
                    ├──feeds──> Load Forecasting (XGBoost)
                    ├──feeds──> Load Forecasting (OpenSTEF)
                    ├──feeds──> Price Forecasting (epftoolbox)
                    └──feeds──> Scenario Builder
                                    └──feeds──> Market Simulation (ASSUME)
                                                    ├──feeds──> Results Visualization
                                                    ├──feeds──> RL Agent Sandbox
                                                    │               └──requires──> TensorBoard for learning metrics
                                                    ├──feeds──> End-to-End Trading Backtest
                                                    │               ├──requires──> Load Forecasting
                                                    │               ├──requires──> Price Forecasting
                                                    │               └──requires──> Market Simulation
                                                    └──feeds──> LLM Trading Assistant
                                                                    ├──requires──> End-to-End Backtest (for context)
                                                                    └──enhances──> Model Explainability Tools

Multi-Model Comparison Dashboard
    ├──requires──> Load Forecasting (both XGBoost and OpenSTEF)
    └──requires──> Price Forecasting (multiple models)

Model Explainability Tools ──enhances──> Load Forecasting
Model Explainability Tools ──enhances──> Price Forecasting
Model Explainability Tools ──enhances──> RL Agent Sandbox

Guided Learning Path ──wraps──> all above features in structured sequence
```

### Dependency Notes

- **End-to-End Trading Backtest requires Load Forecasting, Price Forecasting, AND Market Simulation:** This is the integration feature — can only be built after all three pillars are individually working. It's the Phase 3 deliverable in the PROJECT.md roadmap.
- **LLM Trading Assistant requires End-to-End Backtest:** The assistant needs a working system to query. It wraps the existing functionality rather than replacing it. This is Phase 4.
- **RL Agent Sandbox requires Market Simulation:** ASSUME provides the RL infrastructure. The learning platform adds the notebook-based sandbox layer for experimentation.
- **Scenario Builder enhances Market Simulation:** The scenario builder is a UX layer on top of ASSUME's YAML configuration, not an independent feature.
- **Model Explainability enhances all forecasting modules:** Can be added incrementally — start with XGBoost feature importance (built-in), then add SHAP, then permutation importance for black-box models.

## MVP Definition

### Launch With (v1 — Stage 1: Warm-Up & Basic Prediction)

Minimum viable product — what's needed to validate the learning concept.

- [ ] **Public Data Ingestion Pipeline** — Without data, nothing runs. Must pull from PUDL and produce a usable pandas DataFrame.
- [ ] **Data Cleaning Pipeline** — Dirty data breaks models. Must handle missing values, timezone normalization, train/test split.
- [ ] **Load Forecasting (Manual XGBoost)** — The first "I built something" moment. Must produce a prediction and show MAE/RMSE.
- [ ] **Basic Results Visualization** — At minimum: load-vs-prediction overlay plot and error distribution histogram.
- [ ] **Jupyter Notebook Environment** — The "lab bench." Must have setup instructions that work on a clean machine in <30 minutes.
- [ ] **Guided Learning Path (Stage 1 only)** — Notebooks with markdown explanations, code cells, and reflection questions for the warm-up phase.

### Add After Validation (v1.x — Stage 2: Deep Prediction & Market Simulation)

Features to add once the basic prediction pipeline works.

- [ ] **Load Forecasting (OpenSTEF Automated Pipeline)** — Compare against the manual XGBoost model. The "automated ML vs manual" comparison is highly educational.
- [ ] **Price Forecasting (epftoolbox)** — The second pillar of prediction. Day-ahead price forecasting with benchmark models.
- [ ] **Market Simulation (ASSUME first run)** — Run a basic 7-day simulation with default agents. See market clearing in action.
- [ ] **Multi-Model Comparison Dashboard** — Side-by-side forecasting model comparison using plotly.
- [ ] **Scenario Builder (basic)** — Modify generation mix and demand via ASSUME YAML configs.
- [ ] **Guided Learning Path (Stage 2)** — Expanded notebooks for the deep-dive phase.

### Future Consideration (v2+ — Stages 3-4)

Features to defer until the forecasting + simulation foundation is solid.

- [ ] **RL Agent Sandbox** — Modify reward functions, observe emergent strategies. The "cool AI" feature — only valuable once basic simulation is understood.
- [ ] **End-to-End Trading Backtest** — The capstone: forecast → bid → clear → P&L. Ties everything together.
- [ ] **Model Explainability Tools** — SHAP, feature importance. More impactful once learners have built multiple models and can compare.
- [ ] **LLM-Powered Trading Assistant** — Natural language query interface. Highest "wow factor" but lowest priority — requires everything else to work first.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Public Data Ingestion Pipeline | HIGH | MEDIUM | P1 |
| Data Cleaning & Preprocessing | HIGH | MEDIUM | P1 |
| Load Forecasting (Manual XGBoost) | HIGH | MEDIUM | P1 |
| Basic Results Visualization | HIGH | LOW | P1 |
| Jupyter Notebook Environment | HIGH | LOW | P1 |
| Guided Learning Path | MEDIUM | LOW | P1 |
| Load Forecasting (OpenSTEF) | HIGH | MEDIUM | P2 |
| Price Forecasting (epftoolbox) | HIGH | MEDIUM | P2 |
| Market Simulation (ASSUME) | HIGH | HIGH | P2 |
| Multi-Model Comparison Dashboard | MEDIUM | MEDIUM | P2 |
| Scenario Builder | MEDIUM | HIGH | P2 |
| RL Agent Sandbox | HIGH | HIGH | P3 |
| End-to-End Trading Backtest | HIGH | HIGH | P3 |
| Model Explainability Tools | MEDIUM | MEDIUM | P3 |
| LLM-Powered Trading Assistant | MEDIUM | MEDIUM | P3 |

**Priority key:**
- **P1:** Must have for launch. The platform cannot function as a learning tool without these.
- **P2:** Add after core is working. These differentiate the platform from "just reading library docs."
- **P3:** Capstone features. These make the platform exceptional — build once fundamentals are solid.

## Competitor Feature Analysis

Since this is a learning platform inspired by GeekBidder's commercial tech, we compare features through a "what exists" vs "what we build for learning" lens.

| Feature Area | Commercial (GeekBidder-style) | Academic (ASSUME/HAMLET raw) | Our Learning Platform |
|--------------|-------------------------------|------------------------------|----------------------|
| **Data pipeline** | 30TB+ proprietary data, Hadoop/Spark cluster | Requires users to source their own data | Pre-packaged public datasets from PUDL/IEA, one-command download |
| **Load forecasting** | GeekModel (proprietary deep state-space model) | OpenSTEF (AutoML pipeline) | Manual XGBoost → OpenSTEF comparison path — learners build their own, then see automated alternative |
| **Price forecasting** | Integrated in GeekBidder OS | epftoolbox research benchmark | epftoolbox + custom models, side-by-side comparison dashboard |
| **Market simulation** | GeekBidder OS simulation engine | ASSUME CLI + Python API | ASSUME with notebook-based scenario builder and Grafana dashboards |
| **RL trading agents** | "Auto-trading robot" (proprietary) | ASSUME DRL agents (PPO, TD3, SAC) | ASSUME agents + sandbox notebooks for modifying reward functions + TensorBoard monitoring |
| **Natural language interface** | "图小记" conversational agent | None | LangChain + LLM query assistant wrapping all platform capabilities |
| **Learning structure** | Internal training (not public) | Academic papers + README | Guided 4-stage learning path with milestones, reflection questions, and working artifacts at each stage |

## Sources

- **ASSUME Framework** (GitHub: assume-framework/assume) — v0.5.6 (Dec 2025). Agent-based electricity market simulation with DRL. Core simulation engine for this platform. [HIGH confidence — directly inspected repository]
- **OpenSTEF** (GitHub: OpenSTEF/openstef) — v3.4.93 (Mar 2026). Automated ML pipeline for short-term energy forecasting. Under LF Energy. [HIGH confidence — directly inspected repository]
- **epftoolbox** (GitHub: jeslago/epftoolbox) — Electricity price forecasting benchmark with 5 EU/US markets, LEAR + DNN models. Published in Applied Energy 2021. [HIGH confidence — directly inspected repository]
- **PUDL** (GitHub: catalyst-cooperative/pudl) — v2026.5.0 (May 2026). Public Utility Data Liberation Project. CC-BY-4.0 licensed US energy data pipeline outputting SQLite/Parquet. [HIGH confidence — directly inspected repository]
- **enda** (GitHub: enercoop/enda) — v1.0.4 (Jul 2024). Energy timeseries data manipulation, load forecasting, contract handling. MIT licensed. [HIGH confidence — directly inspected repository]
- **HAMLET** (GitHub: tum-ens/HAMLET) — v1.0.1 (Mar 2025). Hierarchical Agent-based Markets for Local Energy Trading. Published in SoftwareX 2025. [HIGH confidence — directly inspected repository]
- **PROJECT.md** — Project definition with 4-stage learning roadmap, constraints, and out-of-scope decisions. [HIGH confidence — primary project document]

---

*Feature research for: AI-driven electricity trading learning platform (Ellectric)*
*Researched: 2026-05-20*
