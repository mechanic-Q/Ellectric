# Walking Skeleton — Ellectric (AI + 电力交易技术学习平台)

**Phase:** 1
**Generated:** 2026-05-20

## Capability Proven End-to-End

A learner can install all dependencies with one shell command, download PJM hourly demand data from PUDL S3, run the data cleaning pipeline producing validated Parquet output, and execute a persistence forecast that flows through a minimal P&L calculation — producing a cumulative profit chart and proving the full data→predict→trade pipeline connects before any ML model is trained.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Language / Runtime** | Python 3.11 (floor) | OpenSTEF (Phase 2) requires ≥3.11. ASSUME supports 3.10-3.14. 3.11 is the common denominator. |
| **Package manager** | pip + venv | Simplest, no additional tooling. requirements.txt with pinned `==` versions. No Poetry/pipenv/conda. |
| **Data format** | Apache Parquet (columnar, compressed, pandas-native) | Portable without database server. Fast read/write. Schema-preserving. Used as the data contract between all pipeline stages. |
| **Data source** | PUDL v2026.5.0 via HTTPS from AWS S3 public bucket | Analysis-ready US electricity data (EIA-930). No `catalystcoop.pudl` Python package needed — download pre-built Parquet directly. Zenodo DOI 10.5281/zenodo.20275549 for reproducibility. |
| **Primary dataset** | PJM hourly demand (`out_eia930__hourly_subregion_demand`, filtered to `balancing_authority_code == "PJM"`) | Largest US RTO (65M+ people). Most comprehensive PUDL data coverage. UTC timestamps, hourly frequency. |
| **Notebook environment** | Jupyter (1.1.1) with `%matplotlib inline` | Primary learning interface. Thin notebooks import from reusable `pipeline/*.py` modules per D-09 — prevents the monolithic-notebook anti-pattern. |
| **Visualization** | matplotlib 3.10.9 + seaborn 0.13.2 | Universal Python plotting. No plotly dependency in Phase 1. |
| **ML framework** | scikit-learn 1.8.0 (preprocessing, metrics, TimeSeriesSplit) + XGBoost 3.2.0 (gradient-boosted trees) | Phase 1 starts with manual XGBoost. OpenSTEF and PyTorch come in Phase 2. No deep learning framework in Phase 1. |
| **Feature engineering** | calendar features (hour, day_of_week, month, is_weekend, is_holiday), lag features (t-24h, t-168h), rolling statistics (24h mean/std) | Progressive design per D-07: start with 5 core features, measure impact, then add complexity. |
| **Temporal validation** | `TimeSeriesSplit(n_splits=5, gap=24)` with scaler-fit-on-train-only | CRITICAL: gap=24 prevents autocorrelation leakage from lag-24h features. Scalers created and fit INSIDE each fold — callers never touch scaler objects (per D-08, Pitfall 1). |
| **Timezone handling** | All timestamps in UTC (timezone-aware `datetime64[ns, UTC]`) | PUDL provides UTC. UTC avoids DST transition issues (23h/25h days). Calendar features computed from UTC. |
| **Outlier strategy** | IQR detection is REPORT-ONLY — outliers are NOT removed | Electricity load outliers are often real extreme events (heat waves, cold snaps). Removing them destroys the signal that matters for trading (per Pitfall 2). |
| **Package exclusions** | NO `catalystcoop.pudl` (package version doesn't exist on PyPI), NO `enda` (H2O JVM dependency conflicts with STACK.md prohibition), NO `TensorFlow/PyTorch` (deferred to Phase 2) | Phase 1 is deliberately minimal — only 9 total packages in requirements.txt. |
| **Directory layout** | `pipeline/` for .py modules, `notebooks/` for Jupyter, `data/raw/` and `data/processed/` for Parquet files, `models/` for saved artifacts | Feature-folder pattern. All production logic in pipeline/ modules (D-09). Data directories gitignored (large binary files). |
| **Deployment / runtime** | Local Python 3.11 environment with `./setup.sh` one-command bootstrap | No Docker required for Phase 1. Docker Compose (TimescaleDB + Grafana) prepared as commented-out skeleton for Phase 2. |

## Stack Touched in Phase 1

- [x] **Project scaffold** — directory tree, requirements.txt (9 pinned packages), setup.sh, .gitignore, README.md
- [x] **Routing / imports** — `pipeline/*.py` modules importable by `notebooks/*.ipynb` via `from pipeline.X import Y`
- [x] **Data read** — real download: PUDL EIA-930 Parquet via HTTPS, filtered to PJM, cached locally
- [x] **Data write** — real output: `cleaned_load.parquet` (UTC timestamps + load_mw + subregion), `features.parquet` (12 columns after feature engineering)
- [x] **Transformation** — cleaning pipeline (missing values, IQR detection, UTC enforcement), feature engineering (calendar + lag + rolling), TimeSeriesSplit with scaler encapsulation
- [x] **Model training** — real XGBoost model with 5-fold temporal CV, evaluation (MAE/RMSE/MAPE/R²), persistence to JSON
- [x] **End-to-end run** — persistence forecast (yesterday = today) → P&L calculation (flat $50/MWh) → cumulative profit chart → proving all layers connect
- [x] **Visualization** — load overlay plot, error histogram, residuals-over-time, correlation heatmaps, cumulative P&L chart, monthly P&L bar chart
- [x] **Documentation** — README with Quick Start, Data Dictionary, Notebook Guide, Next Steps; Zenodo DOI citation

## Out of Scope (Deferred to Later Slices)

- **OpenSTEF automated forecasting pipeline** — Phase 2. Phase 1 uses manual XGBoost only.
- **Electricity price forecasting (epftoolbox)** — Phase 2. Phase 1 assumes flat $50/MWh price.
- **ASSUME market simulation** — Phase 2. Phase 1 baseline uses minimal pure-Python P&L calculation.
- **Docker services (TimescaleDB + Grafana)** — Phase 2. docker-compose.yml skeleton is prepared but commented out.
- **Reinforcement learning agents (PPO/TD3/SAC)** — Phase 3. Phase 1 has no trading agents.
- **SHAP model explainability** — Phase 3. Phase 1 uses XGBoost built-in feature importance only.
- **FastAPI REST API** — Phase 4. Phase 1 is Jupyter-only.
- **CLI tool (ellectric command)** — Phase 4.
- **LLM trading assistant (LangChain + Ollama)** — Phase 4.
- **Chinese electricity data** — Deferred to v2 (EXT-01).
- **Weather data integration for forecasting** — Phase 2 (OpenSTEF brings weather feature engineering).
- **Real-time data feeds / live trading** — Explicitly out of scope per PROJECT.md.
- **Multi-user / web interface** — Deferred. Single-user Jupyter environment.

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its architectural decisions:

- **Phase 2: Deep Prediction + Market Simulation** — Replace manual XGBoost with OpenSTEF automated pipeline, add epftoolbox price forecasting, run ASSUME market simulations with Grafana dashboards. The `pipeline/` module structure, Parquet data contracts, and UTC timezone convention carry forward unchanged.
- **Phase 3: Trading Agents + Backtesting** — Connect Phase 1/2 forecasts to ASSUME agent bidding strategies, train RL agents (PPO/TD3/SAC) with custom reward functions, run historical backtests on stress periods. The DataLoader abstraction and Parquet-as-contract pattern from Phase 1 enable swappable forecast providers.
- **Phase 4: Integration + LLM Interface** — FastAPI REST API wrapping all pipeline stages, CLI toolchain (`ellectric` command), LangChain + Ollama natural language trading assistant. The modular pipeline structure from Phase 1 means every pipeline function is already importable — the API layer is a thin wrapper.
