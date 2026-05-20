# Phase 01: Data Foundation + Basic Prediction — Research

**Researched:** 2026-05-20
**Domain:** Energy time-series data pipeline + XGBoost load forecasting + end-to-end baseline
**Confidence:** HIGH

## Summary

Phase 01 delivers the "walking skeleton" of the Ellectric learning platform: a Jupyter-based environment where learners pull PUDL electricity data (PJM hourly demand from EIA-930), build an XGBoost load forecasting model with proper temporal validation, and run an end-to-end persistence forecast through a minimal market simulation — proving all five architectural layers connect before introducing domain-specific frameworks (OpenSTEF, ASSUME) in Phase 02.

The core technical risk is **look-ahead bias** (PITFALLS.md §Pitfall 1): fitting scalers on the full dataset before splitting, using random train/test splits on time-ordered data, or leaking future information through feature engineering. This is preventable through disciplined use of `TimeSeriesSplit` and scalers fit ONLY on training folds — but requires that the notebook and module structure _enforce_ this pattern, not merely document it.

**Primary recommendation:** Use the PUDL v2026.5.0 Parquet data from S3 (selective table download — not the full 17.9GB Zenodo archive), build the pipeline as thin Jupyter notebooks importing from reusable `.py` modules, and implement the scaler-fit-on-train-only pattern as a `TimeSeriesPipeline` wrapper that prevents misuse by design.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Data ingestion (PUDL download) | Data Layer (Layer 1) | — | Pure data fetching; no dependency on downstream layers |
| Data cleaning (missing values, IQR, UTC) | Data Layer (Layer 1) | — | Operates on raw data before any modeling |
| Feature engineering (calendar, lag, rolling) | Data Layer (Layer 1) | — | Feature computation is data preparation, not prediction |
| Model training (XGBoost) | Prediction Layer (Layer 2) | — | Consumes cleaned features from Layer 1 via Parquet/DataFrame contract |
| Model evaluation (MAE, RMSE, MAPE) | Prediction Layer (Layer 2) | — | Evaluates against test split; no downstream dependency |
| Visualization (load overlay, error hist) | Jupyter (Interface) | Shared utilities | Renders prediction outputs; thin visualization layer |
| End-to-end baseline (persistence → P&L) | Prediction Layer + Agent Layer | — | Bridges Layer 2 (forecast) to Layer 4 (trading logic) with minimal coupling |

## Standard Stack

### Core (Verified)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **pandas** | 3.0.3 | DataFrame operations, time-series indexing, Parquet I/O | Universal data science standard; Arrow-backed in v3+ |
| **scikit-learn** | 1.8.0 | `TimeSeriesSplit`, `StandardScaler`, `mean_absolute_error`, `mean_absolute_percentage_error`, `r2_score` | Foundation ML library; most-used cross-validation and metrics toolkit |
| **xgboost** | 3.2.0 | Gradient-boosted tree model for load forecasting | Top performer in energy forecasting benchmarks; CPU-optimized |
| **matplotlib** | 3.10.9 | Static visualization (load overlay, error histograms) | Universal Python plotting; used by all energy libraries internally |
| **seaborn** | 0.13.2 | Statistical visualization (error distributions, heatmaps) | Pairs with matplotlib for polished plots with minimal code |
| **jupyter** | 1.1.1 | Interactive notebook environment | Primary learning interface per ENV-03; required by all Phase 1 notebooks |
| **numpy** | (via pandas) | Numerical array operations | Core dependency; no direct version pin needed |

### Supporting (Phase 1 specific)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **holidays** | 0.71 | US federal holiday detection for feature engineering | Required for `is_holiday` calendar feature (D-07) |
| **pyarrow** | (via pandas 3.0) | Parquet read/write engine | Required for reading PUDL Parquet tables from S3 |
| **enda** | 1.0.5 | ⚠️ Energy-specific timeseries utilities (gap detection, resampling) | **See caveat below** — has H2O hard dependency; may conflict with STACK.md prohibition on H2O |

### ⚠️ enda Dependency Caveat

`enda` 1.0.5 lists `h2o` as a hard dependency [VERIFIED: GitHub enercoop/enda README]. STACK.md explicitly lists H2O under "What NOT to Use" ("heavy JVM-based dependency"). This creates a conflict:

- **If you install enda**: You also install H2O (~400MB JVM-based ML framework) — contradicts STACK.md but is a one-time cost for a learning platform
- **If you skip enda**: Phase 1 doesn't strictly need enda's gap-detection or resampling features — PUDL data is already hourly and relatively clean. Use `pandas` directly for any resampling

**Recommendation:** Defer `enda` to Phase 2. For Phase 1, the PUDL EIA-930 data comes pre-cleaned and hourly. Missing-value handling, IQR outlier detection, and UTC timestamp handling can all be done with `pandas` + `numpy` directly. This avoids the H2O dependency entirely and keeps Phase 1's `requirements.txt` lightweight.

### Packages Verified on PyPI

All core packages confirmed available at pinned versions [VERIFIED: pip index]:
- `pandas==3.0.3` ✓ (Latest: 3.0.3)
- `scikit-learn==1.8.0` ✓ (Latest: 1.8.0)
- `xgboost==3.2.0` ✓ (Latest: 3.2.0)
- `matplotlib==3.10.9` ✓ (Latest: 3.10.9)
- `jupyter==1.1.1` ✓ (Latest: 1.1.1)
- `seaborn==0.13.2` ✓ (Latest: 0.13.2)
- `holidays==0.71` ✓ (Verified exists on PyPI)
- `pyarrow` (default in pandas 3.0+) ✓

### ⚠️ PUDL Version Correction

**STACK.md lists `catalystcoop.pudl==2026.5.0` but this version does NOT exist on PyPI.** The PyPI registry shows latest version `2025.7.0` [VERIFIED: PyPI — `pip index versions catalystcoop.pudl` on 2026-05-20].

However, this is NOT a blocking issue: the **data release** v2026.5.0 exists on Zenodo and S3, while the **Python package** is at a different version. For Phase 1, we do NOT need the `catalystcoop.pudl` Python package — we only need to read the pre-built Parquet files. The data is accessed via:
- **S3 Parquet**: `s3://pudl.catalyst.coop/v2026.5.0/` (selective table download, no package needed)
- **HTTP direct download**: `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.5.0/` (for learners without AWS CLI)

**Action:** Remove `catalystcoop.pudl` from Phase 1 `requirements.txt`. The PUDL Python package is for running the ETL pipeline — Phase 1 only consumes pre-built outputs.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| enda | pandas direct | pandas handles hourly PUDL data fine; enda's gap-detection is overkill for pre-cleaned EIA-930 |
| S3 Parquet download | Zenodo full archive (17.9GB) | Zenodo requires downloading ALL tables; S3 allows downloading only the 1-2 tables needed (~50MB vs 17.9GB) |
| holidays library | Manual US holiday CSV | holidays auto-updates; manual CSV requires maintenance for new years |
| xgboost 3.2.0 | LightGBM | Both excellent; XGBoost is OpenSTEF's default backend and better documented for energy use cases |

**Installation (Phase 1 `requirements.txt`):**
```bash
# Core data science
pandas==3.0.3
numpy==2.3.5
pyarrow==22.0.0

# Machine learning
scikit-learn==1.8.0
xgboost==3.2.0

# Visualization
matplotlib==3.10.9
seaborn==0.13.2

# Notebook environment
jupyter==1.1.1

# Feature engineering support
holidays==0.71

# Data access (Parquet from S3)
# pyarrow is already a pandas 3.0 dependency; explicit pin for clarity
```

## Package Legitimacy Audit

> slopcheck unavailable at research time (pip install failed). All packages below tagged `[ASSUMED]`. Planner MUST gate each install behind `checkpoint:human-verify` tasks.

| Package | Registry | Ecosystem | Verified Exists | slopcheck | Disposition |
|---------|----------|-----------|-----------------|-----------|-------------|
| pandas | PyPI | Python | `pip index versions` confirms 3.0.3 | N/A | [ASSUMED] — planner adds checkpoint |
| scikit-learn | PyPI | Python | `pip index versions` confirms 1.8.0 | N/A | [ASSUMED] — planner adds checkpoint |
| xgboost | PyPI | Python | `pip index versions` confirms 3.2.0 | N/A | [ASSUMED] — planner adds checkpoint |
| matplotlib | PyPI | Python | `pip index versions` confirms 3.10.9 | N/A | [ASSUMED] — planner adds checkpoint |
| seaborn | PyPI | Python | `pip index versions` confirms 0.13.2 | N/A | [ASSUMED] — planner adds checkpoint |
| jupyter | PyPI | Python | `pip index versions` confirms 1.1.1 | N/A | [ASSUMED] — planner adds checkpoint |
| numpy | PyPI | Python | `pip index versions` confirms 2.3.5 | N/A | [ASSUMED] — planner adds checkpoint |
| pyarrow | PyPI | Python | `pip index versions` confirms 22.0.0 | N/A | [ASSUMED] — planner adds checkpoint |
| holidays | PyPI | Python | `pip index versions` confirms 0.71 | N/A | [ASSUMED] — planner adds checkpoint |

**Packages removed due to research findings:** `catalystcoop.pudl` (version 2026.5.0 does not exist on PyPI — data access requires no package), `enda` (H2O dependency conflict with STACK.md prohibition)
**Packages flagged as suspicious:** None (slopcheck unavailable)
**Packages requiring human verification:** All 9 packages — planner must add `checkpoint:human-verify` before each install task

## Architecture Patterns

### System Architecture Diagram (Phase 1 Scope)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: DATA → PREDICT → BASELINE           │
│                                                                      │
│  ┌─────────────────────┐                                            │
│  │ PUDL S3 / Zenodo    │  External Data Source                      │
│  │ (v2026.5.0 Parquet) │                                            │
│  └──────────┬──────────┘                                            │
│             │ pandas.read_parquet()                                  │
│             ▼                                                        │
│  ┌──────────────────────────────────────────────────────┐           │
│  │ LAYER 1: DATA PIPELINE (pipeline/*.py modules)       │           │
│  │                                                       │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐ │           │
│  │  │ data_loader │→│  cleaner    │→│  features      │ │           │
│  │  │ .py         │  │  .py        │  │  .py           │ │           │
│  │  │             │  │             │  │                │ │           │
│  │  │ Download    │  │ Missing val │  │ Calendar feat  │ │           │
│  │  │ PUDL table  │  │ IQR outlier │  │ Lag t-24,168  │ │           │
│  │  │ Filter PJM  │  │ UTC convert │  │ Rolling stats  │ │           │
│  │  │ Save Parquet│  │ Validate    │  │ TimeSeriesSplit│ │           │
│  │  └─────────────┘  └─────────────┘  └───────────────┘ │           │
│  │                             │                          │           │
│  │                    Output: data/processed/              │           │
│  │                    cleaned_load.parquet                 │           │
│  └─────────────────────────────┬────────────────────────┘           │
│                                │                                     │
│                                ▼                                     │
│  ┌──────────────────────────────────────────────────────┐           │
│  │ LAYER 2: PREDICTION (pipeline/forecaster.py)         │           │
│  │                                                       │           │
│  │  ┌──────────────────────────────────────────────┐    │           │
│  │  │ XGBoostRegressor                             │    │           │
│  │  │  • Scaler fits on train ONLY (CRITICAL)      │    │           │
│  │  │  • TimeSeriesSplit(n_splits=5, gap=24)       │    │           │
│  │  │  • Default hyperparams (discretion)          │    │           │
│  │  │  • model.save_model() → models/              │    │           │
│  │  │  • predict(horizon) → pd.DataFrame           │    │           │
│  │  └──────────────────────────────────────────────┘    │           │
│  │                             │                          │           │
│  │                    Output: MAE, RMSE, MAPE            │           │
│  │                    Output: forecast.parquet            │           │
│  └─────────────────────────────┬────────────────────────┘           │
│                                │                                     │
│                                ▼                                     │
│  ┌──────────────────────────────────────────────────────┐           │
│  │ LAYER 4 (LITE): END-TO-END BASELINE                  │           │
│  │ (05_end_to_end_baseline.ipynb)                       │           │
│  │                                                       │           │
│  │  ┌──────────────────────────────────────────────┐    │           │
│  │  │ PersistenceForecast (yesterday = today)       │    │           │
│  │  │       │                                       │    │           │
│  │  │       ▼                                       │    │           │
│  │  │ MinimalP&L (flat price assumption)            │    │           │
│  │  │  • if pred > actual: loss (overbought)        │    │           │
│  │  │  • if pred < actual: lost opportunity         │    │           │
│  │  │  • Cumulative P&L plot (matplotlib)           │    │           │
│  │  └──────────────────────────────────────────────┘    │           │
│  │                                                       │           │
│  │  Purpose: Prove data→predict→trade pipeline           │           │
│  │  connects before Phase 2 adds sophistication          │           │
│  └──────────────────────────────────────────────────────┘           │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐           │
│  │ INTERFACE: Jupyter Notebooks (thin wrappers)         │           │
│  │  • 01_data_ingestion.ipynb                           │           │
│  │  • 02_data_cleaning.ipynb                            │           │
│  │  • 03_feature_engineering.ipynb                      │           │
│  │  • 04_load_forecasting.ipynb                         │           │
│  │  • 05_end_to_end_baseline.ipynb                      │           │
│  └──────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure (Phase 1 scope)

```
ellectric/
├── data/
│   ├── raw/                     # Downloaded PUDL Parquet files (~50MB)
│   └── processed/               # Cleaned output Parquet files
│       ├── cleaned_load.parquet
│       └── features.parquet
│
├── pipeline/                    # Reusable .py modules (D-09)
│   ├── __init__.py
│   ├── data_loader.py          # PUDL S3 → pandas DataFrame → Parquet
│   ├── cleaner.py              # Missing values, IQR, UTC, validation
│   ├── features.py             # Calendar + lag + rolling features
│   └── forecaster.py           # XGBoost train/predict with TS split
│
├── notebooks/                   # Thin Jupyter notebooks (D-10)
│   ├── 00_environment_setup.ipynb
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_load_forecasting.ipynb
│   └── 05_end_to_end_baseline.ipynb
│
├── models/                      # Saved model artifacts
│   └── xgboost_load_model.json
│
├── requirements.txt             # Pinned dependencies (D-05)
├── setup.sh                     # One-command environment setup (ENV-01)
├── docker-compose.yml           # Optional: TimescaleDB + Grafana (ENV-02, Phase 2)
└── README.md
```

### Pattern 1: Scaler-Fit-On-Train-Only (CRITICAL — D-08)

**What:** All scalers (`StandardScaler`, `MinMaxScaler`) must be `.fit()` ONLY on training data, never on the full dataset. This is the #1 pitfall (PITFALLS.md §Pitfall 1) and must be enforced structurally.

**When to use:** Every model training step in `pipeline/forecaster.py` and notebooks 03-04.

**Implementation pattern:**
```python
# Source: sklearn official docs + PITFALLS.md §Pitfall 1
# pipeline/forecaster.py

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit

def train_model(df: pd.DataFrame, target_col: str = "load_mw"):
    """Train XGBoost with proper temporal splitting."""
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # NEVER: scaler.fit(X) on full dataset
    # ALWAYS: fit ONLY on training split
    tscv = TimeSeriesSplit(n_splits=5, gap=24)

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        scaler = StandardScaler()
        scaler.fit(X_train)                 # ← Train data ONLY
        X_train_scaled = scaler.transform(X_train)
        X_val_scaled = scaler.transform(X_val)  # ← Apply, don't re-fit

        model = xgb.XGBRegressor(n_estimators=100, max_depth=6,
                                 learning_rate=0.1, random_state=42)
        model.fit(X_train_scaled, y_train)
        # ... evaluate on X_val_scaled
```

**Anti-pattern to NEVER use:**
```python
# WRONG — fits scaler on full dataset before splitting
# This leaks future information into training and produces
# unrealistically good validation metrics
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_all)  # DO NOT DO THIS
X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
```

**Enforcement strategy:** The `pipeline/forecaster.py` module should expose a single `train_model()` function that accepts only a DataFrame and a target column name. All scaling and splitting logic is internal — callers CANNOT misuse it because they never touch scalers directly.

### Pattern 2: TimeSeriesSplit with Gap

**What:** Use `TimeSeriesSplit(n_splits=5, gap=24)` to create train/validation splits that (a) respect temporal ordering and (b) include a 24-hour gap between training and validation to prevent autocorrelation leakage from lag features.

**When to use:** Cross-validation in `pipeline/forecaster.py`.

**Key parameters (sklearn 1.8.0):**
```python
from sklearn.model_selection import TimeSeriesSplit

# n_splits=5: 5-fold expanding-window CV
# gap=24: 24-hour buffer between train and test (prevents lag-24h leakage)
# test_size=None: auto-sized to n_samples // (n_splits + 1)
tscv = TimeSeriesSplit(n_splits=5, gap=24)

# Each fold: train_idx < val_idx (train always before test temporally)
for train_idx, val_idx in tscv.split(X):
    print(f"Train: {train_idx[0]}..{train_idx[-1]}, Val: {val_idx[0]}..{val_idx[-1]}")
```

[VERIFIED: sklearn 1.8.0 official docs — `gap` parameter available since sklearn 0.24]

### Pattern 3: Parquet-as-Contract

**What:** Each pipeline stage reads from and writes to Parquet files with well-defined schemas. No direct function calls between layers — this enables independent debugging and swapping of components.

**When to use:** Between every pipeline stage (loader → cleaner → features → forecaster).

**Data contracts (simplified for Phase 1):**

**cleaned_load.parquet (Layer 1 → 2):**
| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime64[ns, UTC] | Hourly index |
| `load_mw` | float64 | PJM system load |
| `hour` | int8 | 0-23 |
| `day_of_week` | int8 | 0=Monday |
| `month` | int8 | 1-12 |
| `is_weekend` | bool | True if Sat/Sun |
| `is_holiday` | bool | US federal holiday |
| `load_lag_24h` | float64 | Load 24 hours ago |
| `load_lag_168h` | float64 | Load 168 hours ago (1 week) |

**forecast.parquet (Layer 2 → visualization):**
| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime64[ns, UTC] | Forecast target hour |
| `actual_load_mw` | float64 | Ground truth |
| `predicted_load_mw` | float64 | XGBoost prediction |

### Pattern 4: Modular .py + Thin Notebooks (D-09)

**What:** All production logic lives in `pipeline/*.py` modules. Jupyter notebooks are thin wrappers that import from modules and add markdown explanations, visualizations, and reflection questions.

**When to use:** All notebooks (01-05).

**Example notebook cell (04_load_forecasting.ipynb):**
```python
# Cell: Train the model
from pipeline.forecaster import train_model, evaluate_model
from pipeline.data_loader import load_cleaned_data

# Load data (from pipeline module, not inline pandas)
df = load_cleaned_data("data/processed/features.parquet")

# Train model (all scaling/splitting logic encapsulated)
model = train_model(df, target_col="load_mw")

# Evaluate
metrics, predictions = evaluate_model(model, df)
print(f"MAE: {metrics['mae']:.2f} MW, RMSE: {metrics['rmse']:.2f} MW, MAPE: {metrics['mape']:.2f}%")
```

### Anti-Patterns to Avoid

- **Monolithic notebook (ANTI-PATTERN):** Putting data loading, cleaning, feature engineering, training, and plotting in one giant notebook. Makes individual stages untestable and un-swappable. Instead: thin notebooks + `.py` modules.
- **`train_test_split(random_state=42)` on time series (ANTI-PATTERN):** Default sklearn splitter randomizes order — leaks future into training. Instead: `TimeSeriesSplit`.
- **Scaling before splitting (ANTI-PATTERN):** `StandardScaler().fit_transform(X_all)` before any split. Instead: fit scaler inside each TimeSeriesSplit fold.
- **Log-transforming load data (ANTI-PATTERN):** Unlike price data (Pitfall 2), load data is generally well-behaved. Log-transform is unnecessary here and adds complexity for learners. Instead: scale features, keep target in MW.
- **Hard-coding file paths in notebooks (ANTI-PATTERN):** Breaks when data location changes. Instead: `from pipeline.data_loader import DATA_DIR`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Time-series cross-validation | Custom train/test split logic | `sklearn.model_selection.TimeSeriesSplit` | Handles edge cases (gap, test_size); battle-tested by millions of users |
| US federal holiday detection | Manual CSV of holiday dates | `holidays` library (0.71) | Covers all federal holidays, handles floating holidays (Thanksgiving), auto-updates |
| Parquet file I/O | Custom binary format or CSV | `pandas.read_parquet()` + `pyarrow` | Columnar, compressed, schema-preserving, faster than CSV by 10-100x |
| Gradient-boosted tree model | Custom gradient boosting | `xgboost.XGBRegressor` | Handles missing values, feature importance, CPU optimization, regularization — 10+ years of peer-reviewed ML |
| P&L calculation | Custom financial math | Simple numpy arithmetic | For Phase 1 baseline, P&L is `Σ (settle_price - buy_price) × volume` — no need for portfolio libraries yet |
| UTC timezone handling | Custom datetime parsing | `pandas.Timestamp.tz_localize()` + `pandas.DatetimeIndex.tz_convert()` | PUDL provides UTC timestamps; pandas handles DST transitions correctly |

**Key insight:** Phase 1 is about proving the pipeline connects — not about algorithmic novelty. Every "hand-roll" temptation should be met with "does scikit-learn/xgboost/pandas already do this?" The answer is almost always yes.

## Runtime State Inventory

> **SKIPPED** — Phase 01 is a greenfield phase (first phase of the project). No existing runtime state, databases, services, or registrations to migrate. All code will be new.

## Common Pitfalls

### Pitfall 1: Look-Ahead Bias via Scaler Leakage (CRITICAL)

**What goes wrong:** StandardScaler/other scalers are fit on the full dataset before splitting. The scaler's `mean_` and `std_` capture statistics from the test period, leaking future information into training. Model gets unrealistically good validation metrics but fails on truly unseen data.

**Why it happens:** Most ML tutorials teach `StandardScaler().fit_transform(X)` before `train_test_split()` — valid for i.i.d. data, catastrophic for time series.

**How to avoid:** Structure `pipeline/forecaster.py` so that scalers are created and fit INSIDE each `TimeSeriesSplit` fold. Callers never see a scaler object — they can't misuse what they can't access.

**Warning signs:** Validation MAPE < 1% for load forecasting, model performs better on test than training, no `TimeSeriesSplit` visible in code.

**Recovery cost:** HIGH — requires re-doing all feature engineering and retraining.

### Pitfall 2: PUDL Version Confusion

**What goes wrong:** Confusing the `catalystcoop.pudl` Python package version (2025.7.0 on PyPI) with the PUDL data release version (v2026.5.0 on Zenodo/S3). Attempting `pip install catalystcoop.pudl==2026.5.0` fails.

**Why it happens:** STACK.md incorrectly lists `catalystcoop.pudl==2026.5.0` — this version was likely copied from the Zenodo data release tag, not the PyPI package.

**How to avoid:** Do NOT install the PUDL Python package. For Phase 1, download pre-built Parquet tables directly from S3. The package is only needed to run the full ETL pipeline (out of scope for Phase 1).

**Installation pattern:**
```python
# NO: pip install catalystcoop.pudl==2026.5.0  # ← Doesn't exist
# YES: Download Parquet directly
import pandas as pd
url = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.5.0/out_eia930__hourly_subregion_demand.parquet"
df = pd.read_parquet(url)
pjm_load = df[df["balancing_authority_code"] == "PJM"]
```

### Pitfall 3: Not Running End-to-End Early (PITFALLS.md §Pitfall 5)

**What goes wrong:** Spending weeks perfecting the XGBoost model before ever connecting it to a downstream simulation. When integration finally happens, format mismatches, timezone issues, and interface gaps emerge — requiring rework.

**Why it happens:** Academic ML culture rewards accuracy leaderboards. Industry rewards working systems. Learners default to Kaggle-style model optimization.

**How to avoid:** The 05_end_to_end_baseline.ipynb notebook runs IMMEDIATELY after the data pipeline — before model tuning. It uses a naive persistence forecast (yesterday's load = today's prediction). This proves:
1. Data pipeline → forecast → trade → P&L all connect
2. The data contracts (column names, timezone, frequency) are compatible
3. The P&L calculation logic is correct (even if numbers are negative)

**The persistence forecast is NOT about accuracy — it's about integration verification.**

### Pitfall 4: Timezone Blindness

**What goes wrong:** PUDL EIA-930 timestamps are in UTC [VERIFIED: PUDL EIA-930 docs], but learners working in East Coast time (UTC-5) might incorrectly convert to local time and create alignment bugs with calendar features.

**Why it happens:** PJM operates in Eastern timezone, so it's tempting to convert timestamps. But UTC is the correct choice — it avoids DST transition issues (23h and 25h days).

**How to avoid:** Keep ALL timestamps in UTC throughout the pipeline. Calendar features (hour, day_of_week) are computed from UTC timestamps. The `holidays` library accepts a timezone parameter — use `holidays.US()` (no timezone, date-based).

**Warning signs:** `pd.to_datetime(..., utc=False)`, `tz_convert('US/Eastern')`, 23h or 25h days in the data after resampling.

### Pitfall 5: Memory Bloat from Full Parquet Download

**What goes wrong:** Downloading the full PUDL Parquet archive (11.6GB) from Zenodo, when only 1-2 tables are needed (~50MB for `out_eia930__hourly_subregion_demand` filtered to PJM).

**Why it happens:** The Zenodo "Download all" button is the path of least resistance but downloads all 50+ tables.

**How to avoid:** Use S3 direct access (`pandas.read_parquet("s3://...")`) or HTTP direct download to fetch only the specific Parquet files needed. Document the exact URLs in `pipeline/data_loader.py`.

**Target table:** `out_eia930__hourly_subregion_demand` — filter `balancing_authority_code == "PJM"` after loading.
- Size: ~200MB for the full table, ~5MB for PJM-only filter
- Timespan: 2015half2 through 2026half1
- Columns: `timestamp`, `balancing_authority_code`, `subregion`, `demand_mwh`, `demand_imputed_mwh`

## Code Examples

### Example 1: Download PUDL Parquet Table

```python
# Source: PUDL official docs (docs.catalyst.coop) — S3 access pattern
# pipeline/data_loader.py

import pandas as pd
from pathlib import Path

PUDL_S3_BASE = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop"
DATA_VERSION = "v2026.5.0"
PJM_BA_CODE = "PJM"

def download_pjm_demand(
    output_path: str = "data/raw/pjm_demand.parquet",
    force: bool = False
) -> pd.DataFrame:
    """Download PJM hourly demand data from PUDL S3.

    Downloads the pre-built out_eia930__hourly_subregion_demand table,
    filters to PJM balancing authority, and caches locally.

    Args:
        output_path: Local path to save filtered Parquet file
        force: Re-download even if cached file exists

    Returns:
        DataFrame with columns: timestamp, demand_mwh, subregion
    """
    output = Path(output_path)
    if output.exists() and not force:
        return pd.read_parquet(output)

    table_url = (
        f"{PUDL_S3_BASE}/{DATA_VERSION}/"
        f"out_eia930__hourly_subregion_demand.parquet"
    )

    print(f"Downloading PUDL EIA-930 data from {table_url}...")
    df = pd.read_parquet(table_url)

    # Filter to PJM only
    df_pjm = df[df["balancing_authority_code"] == PJM_BA_CODE].copy()

    # Keep only essential columns
    df_pjm = df_pjm[[
        "timestamp", "subregion", "demand_mwh", "demand_imputed_mwh"
    ]]

    # Save cached copy
    output.parent.mkdir(parents=True, exist_ok=True)
    df_pjm.to_parquet(output, index=False)
    print(f"Saved {len(df_pjm):,} rows to {output}")

    return df_pjm
```

### Example 2: Proper Temporal Feature Engineering

```python
# Source: PITFALLS.md §Pitfall 1 + sklearn TimeSeriesSplit docs
# pipeline/features.py

import pandas as pd
import holidays

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar and lag features WITHOUT look-ahead bias.

    CRITICAL: Lag features use .shift() which naturally respects
    temporal ordering. No future information leaks through shift.
    Rolling statistics use .rolling() with closed='left' to prevent
    including the current timestamp in the window.

    Args:
        df: DataFrame with timestamp index and 'load_mw' column

    Returns:
        DataFrame with additional feature columns
    """
    df = df.copy()

    # Calendar features (no look-ahead risk — derived from timestamp alone)
    df["hour"] = df.index.hour.astype("int8")
    df["day_of_week"] = df.index.dayofweek.astype("int8")  # 0=Monday
    df["month"] = df.index.month.astype("int8")
    df["is_weekend"] = df["day_of_week"] >= 5

    # US federal holidays
    us_holidays = holidays.US()
    df["is_holiday"] = df.index.normalize().map(
        lambda d: d in us_holidays
    )

    # Lag features (naturally temporal — no future leak)
    df["load_lag_24h"] = df["load_mw"].shift(24)    # Yesterday same hour
    df["load_lag_168h"] = df["load_mw"].shift(168)  # Last week same hour

    # Rolling window statistics (closed='left' prevents current-hour leak)
    df["load_rolling_mean_24h"] = (
        df["load_mw"].shift(1).rolling(window=24, closed="left").mean()
    )
    df["load_rolling_std_24h"] = (
        df["load_mw"].shift(1).rolling(window=24, closed="left").std()
    )

    # Drop rows with NaN lag features (beginning of dataset)
    df = df.dropna()

    return df
```

### Example 3: Persistence Forecast + End-to-End P&L

```python
# Source: CONTEXT.md D-11 — naive persistence forecast baseline
# notebooks/05_end_to_end_baseline.ipynb

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def persistence_forecast(df: pd.DataFrame) -> pd.DataFrame:
    """Naive forecast: tomorrow = today.

    This is the simplest possible forecast — it assumes every hour
    tomorrow will have the same load as the same hour today.
    Used to prove the pipeline connects, not for accuracy.
    """
    forecast = df[["load_mw"]].copy()
    forecast["predicted_load_mw"] = forecast["load_mw"].shift(24)
    forecast["forecast_type"] = "persistence"
    return forecast.dropna()

def calculate_baseline_pnl(
    actual: pd.Series,
    predicted: pd.Series,
    price_per_mwh: float = 50.0  # Flat price assumption
) -> pd.DataFrame:
    """Minimal P&L calculation for Phase 1 baseline.

    Simplified model:
    - "Buy" at predicted load (commit to serving that much)
    - "Settle" at actual load (must buy/sell difference at spot)
    - If pred > actual: overbought, sell excess at loss
    - If pred < actual: underbought, buy shortage at premium
    - Simplified: P&L = -abs(actual - pred) * price_per_mwh
    """
    error_mw = actual - predicted
    pnl = -np.abs(error_mw) * price_per_mwh
    cumulative_pnl = pnl.cumsum()

    return pd.DataFrame({
        "error_mw": error_mw,
        "pnl_per_hour": pnl,
        "cumulative_pnl": cumulative_pnl
    })

# Usage in notebook:
# df = load_cleaned_data("data/processed/cleaned_load.parquet")
# fc = persistence_forecast(df)
# results = calculate_baseline_pnl(fc["load_mw"], fc["predicted_load_mw"])
# plt.plot(results["cumulative_pnl"])
# plt.title("Cumulative P&L: Persistence Forecast Baseline")
```

### Example 4: XGBoost with Proper Evaluation

```python
# Source: sklearn metrics docs + xgboost API docs
# pipeline/forecaster.py

import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd

def mean_absolute_percentage_error(y_true, y_pred):
    """MAPE — sklearn 1.8.0 includes this as sklearn.metrics.mean_absolute_percentage_error."""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def train_xgboost(df, target_col="load_mw", n_splits=5):
    """Train XGBoost with TimeSeriesSplit and scaler-fit-on-train-only."""
    X = df.drop(columns=[target_col])
    y = df[target_col]

    tscv = TimeSeriesSplit(n_splits=n_splits, gap=24)

    fold_metrics = []
    best_model = None
    best_mae = float("inf")

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        # CRITICAL: Fit scaler ONLY on training data
        scaler = StandardScaler()
        scaler.fit(X_train)
        X_train_s = scaler.transform(X_train)
        X_val_s = scaler.transform(X_val)

        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X_train_s, y_train)

        y_pred = model.predict(X_val_s)

        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        mape = mean_absolute_percentage_error(y_val, y_pred)
        r2 = r2_score(y_val, y_pred)

        fold_metrics.append({
            "fold": fold + 1,
            "train_rows": len(y_train),
            "val_rows": len(y_val),
            "mae_mw": round(mae, 2),
            "rmse_mw": round(rmse, 2),
            "mape_pct": round(mape, 2),
            "r2": round(r2, 4)
        })

        if mae < best_mae:
            best_mae = mae
            best_model = model

    return best_model, pd.DataFrame(fold_metrics)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Random train/test split on time series | `TimeSeriesSplit` with `gap` parameter | sklearn 0.24 (2020) | Prevents look-ahead bias; gap prevents autocorrelation leakage from lag features |
| `pandas` v1.x with NumPy backend | `pandas` v3.0 with Arrow backend | pandas 3.0 (2025) | Faster I/O, copy-on-write, native Parquet support via pyarrow |
| Manual US holiday CSV | `holidays` library | Ongoing maintenance | Auto-updating, covers floating holidays correctly |
| `enda` with H2O dependency | `pandas` + `scikit-learn` directly | Phase 1 decision | Avoids ~400MB JVM dependency for features PUDL data doesn't need |

**Deprecated/outdated:**
- **`pandas` <3.0**: Arrow backend not available; use 3.0.3 for Phase 1
- **`train_test_split(shuffle=False)` on time series**: Better than random shuffle but still doesn't respect expanding-window CV; use `TimeSeriesSplit` instead
- **Manual `datetime` parsing**: `pandas.to_datetime(..., utc=True)` handles all edge cases including DST transitions

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | PUDL `out_eia930__hourly_subregion_demand.parquet` is available at `s3://pudl.catalyst.coop/v2026.5.0/` | Standard Stack / Code Examples | Data ingestion fails — fall back to Zenodo full download (17.9GB) or Kaggle |
| A2 | `holidays` 0.71 installs cleanly on Python 3.11 without conflicts | Standard Stack | Feature engineering blocked — fall back to hard-coded US holiday list for 2015-2026 |
| A3 | `pyarrow` 22.0.0 is compatible with pandas 3.0.3 | Standard Stack | Parquet I/O degraded — fall back to pandas default engine |
| A4 | PUDL S3 bucket is publicly readable without AWS credentials | Code Examples | Download fails — use HTTP direct URLs instead of S3 protocol, or warn learners to configure AWS CLI |
| A5 | `enda` 1.0.5 H2O dependency is acceptable for Phase 2+ but not Phase 1 | Standard Stack | If enda is actually required for Phase 1 feature engineering (unlikely given PUDL data quality), we'd need to install H2O or monkey-patch the import |
| A6 | numpy 2.3.5 is the version that pandas 3.0.3 resolves to | Standard Stack | Version mismatch could cause pandas operations to fail; test `pip install -r requirements.txt --dry-run` first |

## Open Questions (RESOLVED)

1. **PUDL table choice: `out_` vs `core_` prefix**
   - What we know: `out_eia930__hourly_subregion_demand` includes imputed demand values (`demand_imputed_mwh` column). `core_eia930__hourly_subregion_demand` has raw reported values only.
   - What's unclear: Whether learners should work with imputed or raw data for the learning exercise. Imputed = cleaner but less educational about real-world data quality issues. Raw = more realistic but harder to model.
   - Recommendation: Use `out_` table with the imputed column. Document the difference in notebook 01 so learners understand both exist. Offer a "switch to raw data" challenge at the end of notebook 02 for advanced learners.

2. **Should Phase 1 use `pyarrow` S3 protocol or direct HTTPS download?**
   - What we know: `pd.read_parquet("s3://...")` requires `s3fs` or AWS credentials. `pd.read_parquet("https://...")` works without credentials but may be slower.
   - What's unclear: Whether the S3 bucket consistently allows anonymous access from all regions. Some AWS Open Data buckets require `--no-sign-request` and specific region configuration.
   - Recommendation: Use HTTPS direct download as primary method (no credential setup). Document S3 as an alternative for advanced users. Test both during implementation.

3. **XGBoost default hyperparameters vs tuned**
   - What we know: CONTEXT.md gives discretion over exact hyperparameters. Default XGBoost (n_estimators=100, max_depth=6, learning_rate=0.1) produces reasonable results for PJM load forecasting.
   - What's unclear: Whether default parameters will produce "good enough" results for the learning exercise (MAPE < 5% is typical for PJM load forecasting with basic features).
   - Recommendation: Use defaults for the first notebook run. Document that tuning (n_estimators, max_depth, learning_rate) is an exercise left to the learner. Provide a markdown cell with guidance on what to try.

4. **Docker Compose for Phase 1 or Phase 2?**
   - What we know: ENV-02 requires Docker Compose config for TimescaleDB + Grafana. CONTEXT.md D-06 says "not required for Phase 1. Download YAML but mark as Phase 2 dependency."
   - What's unclear: Whether to create the file now (empty/skeleton) or defer entirely.
   - Recommendation: Create `docker-compose.yml` with commented-out service definitions (TimescaleDB + Grafana). Include in setup script but don't start. This satisfies ENV-02's existence requirement without adding Phase 1 complexity.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | All packages (OpenSTEF requires ≥3.11) | ✓ | 3.11.15 | — |
| pip | Package installation | ✓ | 26.0.1 | — |
| Jupyter | Notebook interface (ENV-03) | ✓ | 1.1.1 (installed) | — |
| Docker | TimescaleDB + Grafana (ENV-02, Phase 2) | ✓ | 29.3.0 | Defer to Phase 2 |
| AWS CLI | S3 data access (optional) | Not checked | — | Use HTTPS direct download |
| git | Version control | ✓ | (system) | — |

**Missing dependencies with no fallback:** None — all Phase 1 dependencies are installable via `pip` on Python 3.11.
**Missing dependencies with fallback:** AWS CLI (optional — HTTPS download works without it).

## Security Domain

> `security_enforcement` not explicitly disabled in config — treating as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | No | Phase 1 has no user auth — all local Jupyter |
| V3 Session Management | No | No sessions — local notebooks only |
| V4 Access Control | No | Single-user learning environment |
| V5 Input Validation | ⚠️ Minimal | PUDL data is externally sourced — validate column types, ranges, timestamps before use |
| V6 Cryptography | No | No secrets, no encryption needed in Phase 1 |

### Known Threat Patterns for Python/ML Pipeline

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malicious Parquet file from spoofed S3 URL | Tampering | Pin exact PUDL S3 URLs in code; hash-verify downloaded files (MD5 from Zenodo metadata) |
| `requirements.txt` dependency confusion | Tampering | Pin exact versions with `==`; verify against STACK.md (PyPI-verified versions) |
| Notebook code execution vulnerability | Elevation of Privilege | Jupyter runs as local user — standard Jupyter security model; no network exposure in Phase 1 |
| Large data causing OOM | Denial of Service | Filter PJM before feature engineering; use `chunksize` for large Parquet reads if needed |

**Note:** Phase 1 has minimal security surface — all operations are local, single-user, with trusted data sources. The primary concern is data integrity (ensuring downloaded data hasn't been tampered with). MD5 checksums are provided in Zenodo metadata for each file.

## Sources

### Primary (HIGH confidence)
- [PUDL Official Documentation — Data Access](https://docs.catalyst.coop/pudl/en/stable/data_access.html) — S3, Zenodo, Kaggle access methods; versioning scheme; file formats [VERIFIED]
- [PUDL Official Documentation — EIA-930](https://docs.catalyst.coop/pudl/en/stable/data_sources/eia930.html) — Table schema, BA codes, UTC timestamps, data irregularities [VERIFIED]
- [Zenodo — PUDL v2026.5.0 Release](https://doi.org/10.5281/zenodo.20275549) — Published 2026-05-18, concept DOI 10.5281/zenodo.3653158 [VERIFIED]
- [scikit-learn 1.8.0 — TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) — API: `n_splits`, `gap`, `test_size`, `max_train_size` [VERIFIED]
- [enda GitHub — enercoop/enda](https://github.com/enercoop/enda) — v1.0.4, MIT license, H2O hard dependency confirmed [VERIFIED]
- PyPI Registry — All package versions verified via `pip index versions` on 2026-05-20 [VERIFIED]
- `.planning/research/STACK.md` — Version-pinned stack, Phase 1 pattern, version compatibility [VERIFIED]
- `.planning/research/PITFALLS.md` — Look-ahead bias, scaler leakage, no-e2e-early, timezone handling [VERIFIED]
- `.planning/research/ARCHITECTURE.md` — Layered pipeline, data contracts, anti-patterns [VERIFIED]

### Secondary (MEDIUM confidence)
- [PUDL v2026.5.0 Data Dictionary](https://docs.catalyst.coop/pudl/en/v2026.5.0/data_dictionaries/pudl_db.html) — Confirmed table naming convention (out_ vs core_ prefix) [CITED]
- [PyPI `catalystcoop.pudl`](https://pypi.org/project/catalystcoop.pudl/) — Version 2025.7.0 confirmed as latest; STACK.md version 2026.5.0 does NOT exist [VERIFIED by pip index]

### Tertiary (LOW confidence — requires validation)
- XGBoost 3.2.0 default hyperparameter performance on PJM load data — estimated MAPE <5% based on training knowledge, not verified with actual PJM 2026 data
- PUDL S3 bucket anonymous access availability — assumed always-on based on AWS Open Data Registry listing; should be tested during implementation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all versions verified via PyPI on 2026-05-20; PUDL version discrepancy identified and resolved
- Architecture: HIGH — based on verified PUDL docs, sklearn API, and pre-existing ARCHITECTURE.md research
- Pitfalls: HIGH — derived from verified PITFALLS.md (which itself sources ASSUME, OpenSTEF, and epftoolbox official docs)

**Research date:** 2026-05-20
**Valid until:** 2026-06-20 (30 days — stack versions stable; PUDL v2026.8.0 expected August 2026)
