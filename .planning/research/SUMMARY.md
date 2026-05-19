# Project Research Summary

**Project:** Ellectric — AI-driven electricity trading learning platform
**Domain:** Energy AI / ML education platform with agent-based market simulation
**Researched:** 2026-05-20
**Confidence:** HIGH

## Executive Summary

Ellectric is a **layered learning platform** that teaches electricity trading through progressive AI techniques — from simple XGBoost load forecasting to deep reinforcement learning agents competing in realistic market simulations. Experts in this domain build such systems as **strictly separated pipelines** (data → forecast → simulate → trade), not monolithic notebooks, with each layer communicating through well-defined data contracts (Parquet files with standardized schemas).

The recommended approach is a **four-phase build** that mirrors the learning journey: Phase 1 establishes a working end-to-end pipeline using simple tools (pandas + XGBoost + a trivial naive forecaster plugged into a minimal simulation), proving integration works on Day 1. Phase 2 introduces domain-specific frameworks (OpenSTEF for automated forecasting, ASSUME for market simulation) once fundamentals are solid. Phase 3 adds the "cool AI" — RL trading agents, custom reward functions, and historical backtesting. Phase 4 wraps everything in a Natural Language interface via LangChain + Ollama and a FastAPI backend. Every phase builds on the previous; none can be skipped or reordered.

The key risks are **look-ahead bias in time-series preprocessing** (treating temporal energy data as i.i.d. — the #1 failure mode), **mistaking price spikes for noise** (clipping outliers destroys the trading signal that matters), and **optimizing models for academic metrics rather than trading P&L** (RMSE doesn't pay bills). All three are prevented by running end-to-end with a naive model in Week 1, using temporal (not random) splits for all preprocessing, and evaluating every model upgrade against trading profit, not just forecast accuracy.

## Key Findings

### Recommended Stack

The stack spans five dimensions, introduced progressively across phases. **Python 3.11 is the floor** (OpenSTEF requires ≥3.11, and ASSUME 0.6.0 + OpenSTEF 3.4.93 both support it, making 3.11 the common denominator). Phase 1 starts lean: pandas 3.0.3 (Arrow-backed, fast) + scikit-learn 1.8.0 + XGBoost 3.2.0 + Jupyter notebooks. Phase 2 adds domain tools: OpenSTEF 3.4.93 (automated ML pipeline for energy forecasting), ASSUME 0.6.0 (agent-based market simulation with built-in DRL agents), and epftoolbox (price forecasting benchmarks — **datasets only**, not installed in same env due to TensorFlow/PyTorch conflict). Phase 4 adds FastAPI 0.136.1, LangChain 1.3.1, Ollama 0.6.2 with Qwen2.5-7B (Chinese+English bilingual, runs on 16GB RAM), and chromadb for RAG.

**Core technologies:**
- **pandas 3.0.3 + enda 1.0.5 + PUDL 2026.5.0**: Energy data pipeline — PUDL provides analysis-ready US electricity data (EIA 860/861/923/930), enda handles domain-specific timeseries operations (gap detection, contract conversion), pandas 3.0's Arrow backend handles performance
- **scikit-learn 1.8.0 + XGBoost 3.2.0**: Phase 1-2 ML — XGBoost consistently tops energy forecasting benchmarks, scikit-learn provides preprocessing and evaluation. Both CPU-optimized for dev hardware
- **OpenSTEF 3.4.93 + epftoolbox**: Energy forecasting frameworks — OpenSTEF (LF Energy, MPL-2.0) provides production-style AutoML pipeline for load forecasting; epftoolbox provides benchmark LEAR/DNN models and 5 reference market datasets for price forecasting
- **ASSUME 0.6.0 + stable-baselines3 2.8.0**: Market simulation + RL — ASSUME (AGPL-3.0, published in SoftwareX 2025) handles multi-agent electricity market simulation with pluggable DRL agents (PPO, SAC, TD3), market clearing (pay-as-clear, pay-as-bid, nodal), and Grafana dashboards
- **FastAPI 0.136.1 + LangChain 1.3.1 + Ollama 0.6.2**: Interface layer (Phase 4) — FastAPI for REST API, LangChain for LLM agent orchestration with tool-calling, Ollama for local LLM serving (Qwen2.5-7B-Instruct)

### Expected Features

**Must have (table stakes — P1):**
- **Public Data Ingestion Pipeline** — PUDL + IEA data, one-command download, version-pinned for reproducibility. Without clean data, nothing else works
- **Data Cleaning & Preprocessing** — Gap detection (enda), outlier handling (IQR, not clipping), timezone normalization to UTC, train/test temporal split
- **Load Forecasting (Manual XGBoost)** — Feature engineering (hour-of-day, day-of-week, holidays, lags), train on historical period, evaluate with MAE/RMSE/MAPE, model persistence. This is the first "I built something" moment
- **Results Visualization** — Load-vs-prediction overlay plots, error distribution histograms, feature importance charts. Must work in Jupyter notebooks
- **Jupyter Notebook Environment** — Well-documented notebooks with markdown explanations → code cells → output visualization → reflection questions. Setup must work on a clean machine in <30 minutes
- **Guided Learning Path (Stage 1)** — Structured notebooks for the warm-up phase with clear success criteria

**Should have (differentiators — P2):**
- **Load Forecasting (OpenSTEF)** — Automated pipeline comparison. The "manual vs automated ML" comparison is highly educational
- **Price Forecasting (epftoolbox)** — Day-ahead price forecasting with LEAR/DNN benchmarks across 5 reference markets (EPEX-BE/FR/DE, NordPool, PJM)
- **Market Simulation (ASSUME)** — Agent-based sandbox with configurable generation mix, demand profiles, market mechanisms. Grafana dashboards for visualization
- **Multi-Model Comparison Dashboard** — Side-by-side plotly dashboard comparing XGBoost vs OpenSTEF vs LSTM (load) and LEAR vs DNN vs naive (price). Error-by-hour heatmaps showing where each model fails
- **Scenario Builder** — Modify generation mix and demand via ASSUME YAML configs. Pre-built scenarios: "High Wind Day", "Summer Peak", "Storage Arbitrage"

**Defer (v2+ — P3):**
- **RL Agent Sandbox** — Modify reward functions, observe emergent bidding strategies, TensorBoard monitoring. Requires market simulation to exist first
- **End-to-End Trading Backtest** — The capstone: forecast → bid → market clear → P&L calculation. Requires all three pillars (forecasting, price prediction, simulation) working individually
- **Model Explainability Tools** — SHAP values, partial dependence plots. More impactful once learners have built multiple models
- **LLM-Powered Trading Assistant** — Natural language interface wrapping all platform capabilities. Highest "wow factor" but requires everything else to work first

**Explicitly anti-features (never build):** Real-time market data feeds, automated real-money trading execution, proprietary data scraping, full SaaS web application, carbon/emissions trading, large model training (GPT-scale), graphical drag-and-drop bidding, multi-user collaboration.

### Architecture Approach

The system follows a **5-layer pipeline architecture** with clean data-contract boundaries between layers. Each layer is independently learnable, testable, and replaceable — matching the four-stage learning roadmap. Data flows strictly downward: raw data → cleaned DataFrames → forecast DataFrames → simulation results → agent decisions → user interface. Layers communicate through Parquet files with well-defined column schemas, never through direct function calls. Key patterns: Strategy Pattern for pluggable bidding (rule-based → prediction-based → RL), Pipeline with Checkpoints for faster iteration (each stage caches intermediate results), and Config-Driven Simulation (ASSUME YAML/CSV configs, no code changes to test different markets).

**Major components:**
1. **Data Layer** (`src/data_pipeline/`) — Ingestion (PUDL, IEA), cleaning (enda, pandas), feature engineering (calendar, weather, lags), and storage (Parquet). Produces `cleaned_load.parquet`, `cleaned_price.parquet`, `weather_features.parquet`
2. **Prediction Layer** (`src/prediction/`) — Load forecasting (XGBoost → OpenSTEF), price forecasting (LEAR/DNN via epftoolbox), renewable generation forecasting (weather→power). All forecasters share `predict(horizon) → pd.DataFrame` interface. Produces `forecast_24h.parquet`
3. **Market Simulation Layer** (`src/simulation/`) — ASSUME wrapper with YAML/CSV configs and pre-built learning scenarios. World orchestration, market operations (day-ahead clearing, balancing), unit operators managing generation portfolios. Produces `results.csv` with cleared prices, dispatch, and profit per unit
4. **Agent/Trading Layer** (`src/agents/`) — Pluggable bidding strategies (marginal cost → markup → prediction-based → RL), Gym-compatible RL environments, historical backtesting engine with stress-test scenarios. RL agents use stable-baselines3 (TD3/SAC/PPO) via ASSUME's learning interface
5. **Interface Layer** (`src/interface/`) — FastAPI REST API (Phase 4), Typer/Click CLI (all phases), LangChain chatbot with tool-calling (Phase 4). All three access modes call the same underlying service functions

### Critical Pitfalls

1. **Look-Ahead Bias in Time-Series Preprocessing** — Using `StandardScaler` or computing rolling statistics on the full dataset before temporal splitting leaks future information into training. Prevention: fit scalers only on training period, use `TimeSeriesSplit` (not `train_test_split`), audit every preprocessing step for temporal leakage. Recovery cost: HIGH (requires re-doing all feature engineering and retraining)

2. **Treating Price Spikes as Noise** — Electricity prices exhibit negative values, 10-100x spikes above mean, and multi-modal distributions. Clipping outliers or log-transforming destroys the very signal that matters for trading profit. Prevention: use sMAPE, spike MAE, spike recall alongside RMSE; never clip prices; evaluate models on spike detection, not just aggregate error

3. **RL Reward Function That Optimizes the Wrong Thing** — Pure profit maximization leads to degenerate strategies (bid max price, zero volume 95% of time, huge reward on spikes). ASSUME docs explicitly warn: "A larger total reward does NOT imply that the learned behavior is better." Prevention: always validate behavior (bid curves, acceptance rate) not just reward magnitude; start with naive/heuristic baselines before adding RL; use ASSUME's `early_stopping` with large episodes

4. **Not Running End-to-End Early** — Spending weeks perfecting a prediction model before ever connecting it to simulation or trading. Prevention: run full pipeline (data → naive forecast → simulation → P&L) in Week 1 with a trivial model (next hour = last hour). This validates integration, data formats, and establishes a baseline to beat

5. **Unrealistic Market Assumptions** — Simulating markets without transmission constraints, market power, renewable intermittency, or dual settlement. Strategies that work in simplified markets fail in reality. Prevention: start with ASSUME's built-in example scenarios (which include realistic German market configurations), add realism features progressively (congestion → zonal pricing → multiple markets → ancillary services)

## Implications for Roadmap

Based on combined research from all four files, the architecture, features, and pitfalls all converge on a four-phase build order with strict dependencies:

### Phase 1: Data Foundation + Basic Prediction (Warm-Up)

**Rationale:** Everything downstream depends on clean data and a working prediction pipeline. This phase establishes the "skeleton" — all five layers exist in minimal form, proving integration works before any sophistication is added. The research is unanimous: run end-to-end with a naive model on Day 1.

**Delivers:**
- PUDL data ingestion pipeline → cleaned Parquet files
- Data cleaning with temporal splitting (TimeSeriesSplit, no look-ahead bias)
- Manual XGBoost load forecasting model with feature engineering (calendar, lags)
- Basic visualization (load vs prediction overlay, error distribution)
- Structured Jupyter notebooks with markdown explanations and reflection questions
- **Naive end-to-end run**: persistence forecast → minimal simulation → P&L calculation (validates the full pipeline exists)

**Addresses features:** Public Data Ingestion Pipeline, Data Cleaning & Preprocessing, Load Forecasting (Manual XGBoost), Basic Results Visualization, Jupyter Notebook Environment, Guided Learning Path (Stage 1)

**Must avoid:** Pitfall 1 (look-ahead bias — use `TimeSeriesSplit`, fit scalers only on training data), Pitfall 2 (clipping price spikes — evaluate with spike-aware metrics from the start), Pitfall 5 (no end-to-end — run full loop in Week 1)

**Stack:** pandas 3.0.3 + scikit-learn 1.8.0 + XGBoost 3.2.0 + enda 1.0.5 + Jupyter + matplotlib. PUDL for data. Purely CPU — no GPU needed.

### Phase 2: Deep Prediction + Market Simulation

**Rationale:** Phase 1 proved the pipeline works. Phase 2 introduces domain-specific tools (OpenSTEF for automated forecasting, ASSUME for market simulation) that are the platform's core value. Predictions feed simulation, so forecasting must mature before simulation scenarios become meaningful. ASSUME is the platform for all later trading agent work.

**Delivers:**
- OpenSTEF automated forecasting pipeline (compare against manual XGBoost from Phase 1)
- Price forecasting with epftoolbox (LEAR model + benchmark datasets, 5 reference markets)
- ASSUME installation, first 7-day simulation with default naive agents
- Multi-model comparison dashboard (plotly): XGBoost vs OpenSTEF, LEAR vs naive price baselines
- Basic scenario builder (modify generation mix, demand profiles via ASSUME YAML)
- Merit order visualization (Grafana dashboards via ASSUME's Docker Compose)
- Expanded notebooks for Stage 2 learning

**Addresses features:** Load Forecasting (OpenSTEF), Price Forecasting (epftoolbox), Market Simulation (ASSUME), Multi-Model Comparison Dashboard, Scenario Builder (basic), Guided Learning Path (Stage 2)

**Must avoid:** Pitfall 4 (unrealistic market — start with ASSUME's example_01a, verify simulated prices correlate with real data r > 0.6), Pitfall 6 (dual settlement gap — introduce concept even if not fully implemented yet), Pitfall 9 (merit order ignorance — verify merit order steps appear in Grafana)

**Stack adds:** OpenSTEF 3.4.93, epftoolbox (datasets only — do NOT install full package in same env due to TF/PyTorch conflict), ASSUME 0.6.0, plotly 6.7.0

### Phase 3: Trading Agents + Backtesting

**Rationale:** Trading strategies are meaningless without a market to test in. ASSUME must already be running with naive strategies (Phase 2) before RL agents can be added, compared, and validated. This phase introduces the "cool AI" — RL agents learning to trade — but the architecture research emphasizes that RL is strictly additive, not foundational.

**Delivers:**
- Custom rule-based bidding strategies (marginal cost, markup, prediction-based)
- RL agent training via ASSUME's learning capabilities (TD3/SAC/PPO)
- Reward function variants (profit-only, risk-adjusted, multi-component)
- TensorBoard integration for training monitoring
- Historical backtesting engine with stress-test periods (2022 energy crisis, 2021 winter storm, COVID demand shock)
- End-to-end trading backtest: forecast → bid strategy → market clearing → P&L → strategy comparison
- Agent behavior validation suite (bid curves, acceptance rate, strategy Sharpe ratio)

**Addresses features:** RL Agent Sandbox, End-to-End Trading Backtest, Model Explainability Tools (SHAP for XGBoost, feature importance)

**Must avoid:** Pitfall 3 (RL reward collapse — validate behavior not just reward, use ASSUME's `early_stopping` with large episodes, compare P&L vs naive baseline), Pitfall 8 (survivorship bias — backtest on crisis periods, not just stable markets), Pitfall 10 (pipeline coupling — use ForecastProvider interface so models are swappable)

**Stack adds:** stable-baselines3 2.8.0 (direct usage beyond ASSUME defaults), optuna 4.8.0 (hyperparameter tuning), optionally PyTorch if training custom RL models outside ASSUME

### Phase 4: Integration + LLM Interface

**Rationale:** The interface layer wraps all previous layers. The architecture research is explicit: every function tool backing the LLM chatbot MUST be a working CLI command first. Building the chatbot before the pipelines are stable causes hallucination, cascading errors, and loss of learner trust. This is the LAST layer, and all architecture anti-patterns agree.

**Delivers:**
- FastAPI REST API with endpoints: `/predict`, `/simulate`, `/results`, `/backtest`
- CLI with subcommands mirroring pipeline stages: `ellectric predict`, `ellectric simulate`, `ellectric backtest`
- LangChain + Ollama chatbot with tool-calling:
  - Natural language query: "What is tomorrow's peak load forecast?"
  - Trading command parsing: "Bid 50MW at $35/MWh for hours 8-16"
  - Scenario explanation: "Why did prices spike yesterday afternoon?"
  - Model comparison: "Compare my XGBoost against OpenSTEF for last week"
- ChromaDB vector store for RAG over trading docs and historical scenarios
- MLflow experiment tracking dashboard (retroactively applied to all previous phase experiments)

**Addresses features:** LLM-Powered Trading Assistant, all interface access modes (API, CLI, Chatbot)

**Must avoid:** Architecture Anti-Pattern 4 (premature LLM integration — every tool must be a working CLI command first), Pitfall 10 (pipeline coupling — interface calls functions, doesn't embed logic)

**Stack adds:** FastAPI 0.136.1 + uvicorn 0.47.0, LangChain 1.3.1 + langchain-community 0.4.1, Ollama 0.6.2 + Qwen2.5-7B-Instruct, chromadb 1.5.9, MLflow 3.12.0

### Phase Ordering Rationale

- **Phase 1 must come first** because: (a) all layers need clean data, (b) running end-to-end with naive models prevents Pitfall 5 (the "perfect model, no integration" trap), (c) establishes the correct temporal preprocessing discipline before any sophistication is added
- **Phase 2 must come second** because: (a) ASSUME is the platform for all trading work — "Strategies are meaningless without a market to test in. SIMULATION MUST EXIST FIRST" (ARCHITECTURE.md), (b) OpenSTEF comparison only makes sense once learners have built their own model in Phase 1
- **Phase 3 must come third** because: (a) RL agents are compared against rule-based baselines that need ASSUME (Phase 2), (b) backtesting requires both prediction (Phase 1-2) and simulation (Phase 2) to exist, (c) reward function design is guided by behavior observed in Phase 2 simulations
- **Phase 4 must come last** because: all architecture anti-patterns and pitfalls agree — the interface layer wraps everything underneath. Every LLM tool must be a proven CLI command first

### Research Flags

**Phases likely needing deeper research during planning (`/gsd-plan-phase --research-phase`):**

- **Phase 2 (Deep Prediction + Market Simulation):** ASSUME configuration has documented gotchas (seed=null for RL, train_freq alignment, complex clearing corner cases). epftoolbox TensorFlow conflict requires a concrete LEAR reimplementation plan with scikit-learn. PUDL data model understanding (EIA generator IDs, fuel types, timezone handling) is non-trivial. OpenSTEF CPU-only install path needs verification on target hardware.

- **Phase 3 (Trading Agents):** RL reward function design for electricity markets is under-documented beyond ASSUME's warnings. Action space design (continuous vs discrete bidding) impacts algorithm choice. Multi-agent RL dynamics (centralized critic, gradient step timing per agent) are documented in ASSUME release notes but require careful study. Backtesting stress scenarios need historical price data selection.

- **Phase 4 (Integration + LLM):** LangChain v1.x tool-calling patterns for domain-specific data pipelines have fewer examples than generic chatbot use cases. ChromaDB embedding strategy for electricity trading documents (which chunk size, which embedding model) needs experimentation. Ollama Qwen2.5-7B quantization settings for 16GB RAM need benchmarking.

**Phases with standard patterns (skip research-phase, proceed directly to plan):**

- **Phase 1 (Data Foundation):** pandas + scikit-learn + XGBoost data pipeline is the most well-documented pattern in data science. PUDL has extensive tutorials. TimeSeriesSplit and temporal preprocessing are thoroughly covered in sklearn docs and energy forecasting papers. Standard pattern — plan directly.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | All version numbers verified against PyPI on 2026-05-20. Library compatibility matrix documented. ASSUME, OpenSTEF, enda, PUDL repos directly inspected. Published papers (SoftwareX 2025, Applied Energy 2021) validate tool quality. |
| Features | **HIGH** | Feature priority derived from PROJECT.md 4-stage roadmap. All table-stake features map to specific libraries. Differentiator features map to ASSUME/LangChain capabilities verified in official docs. Anti-features aligned with explicit PROJECT.md constraints. |
| Architecture | **HIGH** | Layer design mirrors ASSUME's own architecture (docs at assume.readthedocs.io). Data contract schemas defined. Project structure follows standard Python data-science layout. Build order verified against layer dependency requirements. |
| Pitfalls | **HIGH** | Top 10 pitfalls sourced directly from ASSUME official docs (readthedocs), release notes v0.1.0–v0.6.1 (11 releases of bug-fix history), and peer-reviewed papers. Prevention strategies include working code examples and ASSUME-specific config guidance. Recovery strategies provided for each critical pitfall. |

**Overall confidence: HIGH** — Research is unusually thorough for this domain. ASSUME is well-documented with published academic validation, all libraries have active maintenance and accessible source code, and PROJECT.md provides clear constraints that bound the research scope.

### Gaps to Address

These areas couldn't be fully resolved in research and need attention during planning or implementation:

- **Chinese electricity data pipeline:** No Python package exists for Chinese energy data (PUDL is US-only). The STACK.md notes manual ingestion from 国家能源局 and 菏泽市公共数据开放网, but actual data availability, format, and update frequency need validation during Phase 1 planning. Mitigation: start with PUDL/IEA data to prove the pipeline; add Chinese data as a Phase 1 extension task.

- **epftoolbox LEAR model reimplementation:** The TensorFlow/PyTorch conflict means epftoolbox can't be installed in the same environment as ASSUME. Reimplementing the LEAR model (essentially LASSO regression with engineered features) with scikit-learn should be straightforward, but needs a concrete implementation plan in Phase 2. This is low-risk but requires a task.

- **ASSUME Chinese electricity market configuration:** ASSUME's built-in scenarios model German (EPEX) market rules. Chinese electricity markets (provincial vs inter-provincial, different bidding timelines, different renewable integration policies) may require custom market configuration. Research during Phase 2 planning should assess how much customization is needed vs using European markets as the primary learning environment.

- **Qwen2.5-7B quantization performance:** The STACK.md recommends Qwen2.5-7B-Instruct with 4-bit quantization for 16GB RAM, but performance (inference speed, quality degradation, electricity-domain knowledge) hasn't been benchmarked for this specific use case. This is a Phase 4 spike task — try it and validate before committing to the full chatbot implementation.

## Sources

### Primary (HIGH confidence)
- **ASSUME Framework** — `https://assume.readthedocs.io/en/latest/` — Architecture, bidding strategies, market mechanisms, reinforcement learning docs, release notes v0.1.0–v0.6.1. GitHub: `github.com/assume-framework/assume` (v0.6.0, AGPL-3.0, 90★)
- **OpenSTEF** — `https://github.com/OpenSTEF/openstef` — v3.4.93 (MPL-2.0, 143★, LF Energy project). Automated ML pipeline for short-term energy forecasting
- **epftoolbox** — `https://github.com/jeslago/epftoolbox` (Apache-2.0, 352★). Electricity price forecasting benchmark with 5 EU/US markets. Published in Applied Energy (2021)
- **PUDL** — `https://github.com/catalyst-cooperative/pudl` (v2026.5.0, MIT, 586★, 11K commits). CC-BY-4.0 licensed US energy data pipeline
- **enda** — `https://github.com/enercoop/enda` (v1.0.5, MIT, 16★). Energy timeseries data manipulation
- **HAMLET** — `https://github.com/tum-ens/HAMLET` (v1.0.1, MIT, 24★). Published in SoftwareX (2025)
- **Harder et al. (2025)** — "ASSUME: An agent-based simulation framework for exploring electricity market dynamics with reinforcement learning," *SoftwareX*, Vol. 30, Article 102176
- **Harder, Qussous & Weidlich (2023)** — "Fit for purpose: Modeling wholesale electricity markets realistically with multi-agent deep reinforcement learning," *Energy and AI*, Vol. 14, 100295
- **Lago et al. (2021)** — "Forecasting day-ahead electricity prices: A review of state-of-the-art algorithms, best practices and an open-access benchmark," *Applied Energy*, Vol. 293, 116983
- **PROJECT.md** — Ellectric project definition with 4-stage learning roadmap, constraints, and out-of-scope decisions

### Secondary (MEDIUM confidence)
- PyPI package index — All version numbers verified via `pip index versions` on 2026-05-20
- scikit-learn, XGBoost, FastAPI, LangChain official documentation — Well-established libraries, used per standard patterns
- LangChain → LlamaIndex comparison — Based on v1.x API surface evaluation; both could coexist (LlamaIndex for retrieval, LangChain for agent orchestration)

### Tertiary (LOW confidence)
- Chinese electricity data availability from public sources (国家能源局, 菏泽市公共数据开放网) — Not yet validated. Needs Phase 1 spike
- Qwen2.5-7B quantization performance for electricity-domain QA — Not benchmarked. Needs Phase 4 spike

---
*Research completed: 2026-05-20*
*Ready for roadmap: yes*
