# Phase 1: Data Foundation + Basic Prediction - Context

**Gathered:** 2026-05-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a working Jupyter-based learning environment where users can: (1) install all dependencies in one command, (2) pull and clean PUDL electricity data, (3) train an XGBoost load forecasting model with proper temporal validation, and (4) run an end-to-end baseline pipeline (persistence forecast → simulation → P&L) proving all system layers connect. This is the "prove the skeleton" phase — get a full pipeline running before introducing domain-specific frameworks (OpenSTEF, ASSUME) in Phase 2.
</domain>

<decisions>
## Implementation Decisions

### Data Source Selection
- **D-01:** Use PJM Interconnection data via PUDL as the primary dataset — largest US RTO, most comprehensive data coverage, well-documented PUDL tables (hourly demand, generation mix, plant metadata). Default to full PJM region; individual zones optional.
- **D-02:** Pin data version via Zenodo DOI for reproducibility. PUDL provides versioned data releases — learners must get identical results regardless of when they download.

### Data Storage & Format
- **D-03:** Parquet as primary data format — portable, columnar, pandas-native, fast read/write without database server. No SQLite unless query complexity demands it later.
- **D-04:** Standardized column schema documented inline: `timestamp` (datetime64[ns, UTC]), `load_mw` (float64), `temperature_f` (if weather available), plus metadata columns. All timestamps in UTC with timezone-aware pandas dtypes. Column name `timestamp` used for brevity while preserving full timezone awareness.

### Environment Setup
- **D-05:** pip + venv with `requirements.txt` (pinned versions from STACK.md). One-command setup: `python3.11 -m venv .venv && pip install -r requirements.txt`. Target: <30 minutes on clean machine.
- **D-06:** Docker Compose optional (for TimescaleDB + Grafana) — not required for Phase 1. Download YAML but mark as "Phase 2 dependency."

### Feature Engineering Approach
- **D-07:** Progressive feature design — start with 5 core features (hour, day-of-week, month, is_weekend, lag-24h), validate model works, then add holiday flags, lag-168h, rolling windows. Each feature addition should be its own notebook cell with before/after metric comparison.
- **D-08:** CRITICAL: All scalers (StandardScaler, etc.) fit ONLY on training data using `TimeSeriesSplit`. NEVER call `fit()` on full dataset. This is the #1 pitfall identified in research and must be enforced by the notebook structure itself.

### Notebook Architecture
- **D-09:** Modular structure: thin Jupyter notebooks import from reusable `.py` modules (`pipeline/data_loader.py`, `pipeline/cleaner.py`, `pipeline/features.py`, `pipeline/forecaster.py`). Notebooks are for exploration and visualization; `.py` modules are for production logic. This prevents the monolithic-notebook anti-pattern.
- **D-10:** Notebook naming convention: `01_data_ingestion.ipynb`, `02_data_cleaning.ipynb`, `03_feature_engineering.ipynb`, `04_load_forecasting.ipynb`, `05_end_to_end_baseline.ipynb`. Sequential, self-documenting.

### End-to-End Baseline
- **D-11:** Baseline uses persistence forecast (yesterday's load = today's prediction) plus a minimal P&L calculation (assume flat price, buy at forecast, settle at actual). No ASSUME dependency — pure Python. Purpose: prove data → predict → trade pipeline works in <50 lines.
- **D-12:** Baseline P&L chart verifies: (a) predictions flow into trading logic, (b) cumulative profit graph renders, (c) pipeline layers are connected. Numerical P&L need not be positive — the point is integration, not profitability.

### Model Evaluation
- **D-13:** Default metrics: MAE, RMSE, MAPE on temporal test split (last 20% of data). Add R² as supplementary. Report all metrics in a single comparison table.
- **D-14:** Visualization minimum: (a) load-vs-prediction overlay plot for test period, (b) error distribution histogram, (c) residuals-over-time plot. Use matplotlib (pyplot) — no plotly dependency yet.

### Claude's Discretion
- Exact XGBoost hyperparameters (n_estimators, max_depth, learning_rate) — start with defaults, tune later
- Error message wording for missing data or failed downloads
- Color scheme and figure sizes for matplotlib plots
- `requirements.txt` exact structure (flat vs grouped with comments)
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Definition
- `.planning/PROJECT.md` — Core value, constraints, out-of-scope boundaries
- `.planning/REQUIREMENTS.md` — All 24 v1 requirements; Phase 1 covers ENV-01..03, DATA-01..04, PRED-01, VIZ-01

### Technology Stack
- `.planning/research/STACK.md` — Version-pinned stack: Python 3.11, pandas 3.0.3, scikit-learn 1.8.0, XGBoost 3.2.0, enda 1.0.5, matplotlib 3.10.9

### Pitfalls (CRITICAL reads)
- `.planning/research/PITFALLS.md` — **Look-ahead bias** (scaler on full data, random splits), **spike-as-noise** (log-transforming prices destroys signal), and **no end-to-end early** trap. Phase 1 must actively prevent the first and third.

### Architecture
- `.planning/research/ARCHITECTURE.md` — Layered pipeline: Data Layer → Prediction Layer → Market Layer → Agent Layer. Phase 1 delivers Data Layer + manual Prediction Layer connector.

### Features
- `.planning/research/FEATURES.md` — Table stakes feature list, dependency chain: Data → Forecasting → Simulation → RL → LLM. Phase 1 covers the first two nodes.

### Roadmap
- `.planning/ROADMAP.md` § Phase 1 — 9 requirements, 5 success criteria, MVP mode
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet — greenfield project. All code in Phase 1 will be new.

### Established Patterns
- `pipeline/` directory for `.py` modules (established in this phase as project convention)
- `notebooks/` directory for Jupyter exploration (established in this phase)
- `requirements.txt` with pinned versions (established in this phase)

### Integration Points
- Phase 1 `DataLoader` class will be consumed by Phase 2 (OpenSTEF + ASSUME input)
- Phase 1 `cleaned_load.parquet` output schema will be the contract for downstream phases
- Phase 1 `Forecaster.predict()` interface will be replaced by OpenSTEF in Phase 2 — design it as an abstraction
</code_context>

<specifics>
## Specific Ideas

- "I want to be able to find data and make a prediction within 30 minutes of setup" — from the learning roadmap
- Notebooks should feel like a guided tutorial, not a code dump — markdown explanations before each code block, reflection questions after each visualization
- The end-to-end baseline should produce a cumulative profit chart even if the numbers are negative — the visual proof of integration is the goal
- Follow the Beijing Tuji (GeekBidder) inspired pattern: data robot → prediction → trade — our open-source equivalent
</specifics>

<deferred>
## Deferred Ideas

- Chinese electricity data (国家能源局, 菏泽市, EPS) — custom scraping, no ready-made Python package. Deferred to v2 (EXT-01). Focus Phase 1 on PUDL.
- Weather data integration for prediction features — deferred to Phase 2 when OpenSTEF brings weather feature engineering
- HAMLET local market simulation — research couldn't locate the repo (possible 404). ASSUME covers wholesale market needs.
- Real-time data feeds and live trading — explicitly out of scope per PROJECT.md
</deferred>

---
*Phase: 01-data-foundation-basic-prediction*
*Context gathered: 2026-05-20*
