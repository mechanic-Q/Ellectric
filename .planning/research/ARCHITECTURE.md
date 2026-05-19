# Architecture Research

**Domain:** AI-driven electricity trading learning platform
**Researched:** 2026-05-20
**Confidence:** HIGH

## Standard Architecture

### System Overview

The system follows a **layered pipeline architecture** with clean data-contract boundaries between layers. Each layer is independently learnable, testable, and replaceable — matching the four-stage learning roadmap in PROJECT.md.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     LAYER 5: INTERFACE LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────────┐  │
│  │  FastAPI      │  │  CLI         │  │  LLM Chatbot                  │  │
│  │  (REST API)   │  │  (assume +   │  │  (LangChain + OpenAI/Ollama)  │  │
│  │               │  │   custom)    │  │                               │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────────┬───────────────┘  │
│         │                 │                           │                  │
├─────────┴─────────────────┴───────────────────────────┴──────────────────┤
│                     LAYER 4: AGENT / TRADING LAYER                         │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    Trading Orchestrator                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │    │
│  │  │ RL Agent      │  │ Rule-Based   │  │ Backtesting Engine   │    │    │
│  │  │ (TD3/SAC/PPO) │  │ Strategies   │  │ (hist replay)        │    │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘    │    │
│  │         │                 │                      │                │    │
│  │         └─────────┬───────┴──────────────────────┘                │    │
│  │                   │  Bid decisions (price, volume, time)          │    │
│  └───────────────────┼──────────────────────────────────────────────┘    │
│                      │                                                    │
├──────────────────────┼────────────────────────────────────────────────────┤
│                      ↓                                                    │
│               LAYER 3: MARKET SIMULATION LAYER (ASSUME)                   │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    World (Orchestrator)                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │    │
│  │  │ Market Op.   │  │ Day-Ahead    │  │ Real-Time Market     │    │    │
│  │  │ (coordinator)│  │ Market       │  │ (balancing)          │    │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘    │    │
│  │         │                 │                      │                │    │
│  │         └─────────┬───────┴──────────────────────┘                │    │
│  │                   ↓  Clearing (uniform / pay-as-bid / nodal)      │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │  Unit Operators (manage portfolios)                       │    │    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │    │    │
│  │  │  │PowerPlant│  │ Storage  │  │ Demand   │  │ Renewable│ │    │    │
│  │  │  │ Unit     │  │ Unit     │  │ Unit     │  │ Unit     │ │    │    │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  │  Output: cleared prices, dispatch, profits, market metrics        │    │
│  └───────────────────────────┬──────────────────────────────────────┘    │
│                              │  Needs: load forecast, price forecast,     │
│                              │  renewable forecast, marginal costs        │
├──────────────────────────────┼────────────────────────────────────────────┤
│                              ↑                                            │
│                  LAYER 2: PREDICTION LAYER                                 │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    Prediction Pipeline                             │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │    │
│  │  │ Load Forecast │  │ Price Forecast│  │ Renewable Gen.      │    │    │
│  │  │ (XGBoost/     │  │ (LEAR/DNN/   │  │ Forecast            │    │    │
│  │  │  OpenSTEF)    │  │  epftoolbox)  │  │ (meteo→power model) │    │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘    │    │
│  │         │                 │                      │                │    │
│  │         └─────────┬───────┴──────────────────────┘                │    │
│  │                   ↓  Feature engineering + Model training         │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │  Feature Store (calendar, weather, lag features)          │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  └───────────────────────────┬──────────────────────────────────────┘    │
│                              │  Needs: cleaned time-series data           │
├──────────────────────────────┼────────────────────────────────────────────┤
│                              ↑                                            │
│                    LAYER 1: DATA LAYER                                     │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    Data Pipeline                                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │    │
│  │  │ Data Ingest  │  │ Data Clean   │  │ Feature Engineering  │    │    │
│  │  │ (PUDL/IEA/   │  │ (enda/       │  │ (time/calendar/      │    │    │
│  │  │  CSV/API)    │  │  pandas)     │  │  weather features)   │    │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘    │    │
│  │         │                 │                      │                │    │
│  │         └─────────┬───────┴──────────────────────┘                │    │
│  │                   ↓                                               │    │
│  │  ┌──────────────────────────────────────────────────────────┐    │    │
│  │  │  Data Store (SQLite/Parquet files, DuckDB for query)      │    │    │
│  │  │  Tables: load, price, generation, weather, plant_metadata │    │    │
│  │  └──────────────────────────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation | Learning Stage |
|-----------|----------------|------------------------|----------------|
| **Data Ingest** | Fetch raw data from PUDL, IEA, public APIs; store locally | Python scripts, `pudl` package, `pandas` | Stage 1 |
| **Data Cleaner** | Handle missing values, resample to uniform frequency, validate quality | `enda` (timeseries), `pandas` | Stage 1 |
| **Feature Store** | Engineer datetime features (hour, day-of-week, holidays), weather features, lag features | `enda` feature engineering, `pandas` | Stage 1-2 |
| **Data Store** | Persist cleaned time-series data in queryable format | SQLite (via PUDL pattern) or DuckDB + Parquet | Stage 1 |
| **Load Forecaster** | Predict future electricity demand (MW) at 15min/1hr resolution | XGBoost (Stage 1), OpenSTEF (Stage 2) | Stage 1-2 |
| **Price Forecaster** | Predict day-ahead electricity prices for bid optimization | LEAR model, epftoolbox DNN | Stage 2 |
| **Renewable Forecaster** | Predict wind/solar generation from weather forecasts | Physical model (wind speed→power) or ML | Stage 2 |
| **World (ASSUME)** | Orchestrate simulation: manage clock, coordinate markets + agents | `assume.World` with mango agent framework | Stage 2-3 |
| **Market Operator** | Operate one or more markets, handle post-clearing (redispatch) | `assume.markets.MarketRole` | Stage 2 |
| **Day-Ahead Market** | Collect bids, run clearing algorithm, publish prices/dispatch | `assume.markets` clearing algorithms | Stage 2 |
| **Real-Time Market** | Handle imbalances, balancing energy pricing | ASSUME balancing market (in development) | Stage 3 |
| **Unit Operator** | Manage portfolio: aggregate unit constraints, place coordinated bids | `assume.UnitOperator` | Stage 3 |
| **Power Plant Unit** | Represent thermal generator with technical constraints (ramp, min/max, efficiency) | `assume.units.PowerPlant` | Stage 2 |
| **Storage Unit** | Represent battery/pumped hydro with SoC, charge/discharge limits | `assume.units.Storage` | Stage 3 |
| **Renewable Unit** | Represent wind/solar with weather-dependent availability | `assume.units` + custom forecaster | Stage 3 |
| **Demand Unit** | Represent fixed or flexible load | `assume.units.Demand`, `DSMFlex` | Stage 2 |
| **Bidding Strategy** | Map state → bid (price, volume). Pluggable: rule-based, optimization, or RL | `assume.strategies.*` | Stage 2-3 |
| **RL Agent** | Learn bidding policy via DRL (TD3, SAC, PPO) | `assume.strategies.learning_strategies` | Stage 3 |
| **Backtesting Engine** | Replay historical data, evaluate strategy against past markets | Custom wrapper around ASSUME or standalone | Stage 3 |
| **Trading Orchestrator** | Combine predictions + simulation → execute backtest → report metrics | Custom Python module | Stage 3-4 |
| **FastAPI Server** | Expose REST API: run predictions, trigger simulations, query results | FastAPI + Pydantic schemas | Stage 4 |
| **CLI** | Command-line interface: run pipelines, backtests, inspect data | `assume` CLI + custom Click/Typer commands | All stages |
| **LLM Chatbot** | Natural language interface: "predict tomorrow's load" → runs pipeline | LangChain + OpenAI/Ollama + function calling | Stage 4 |

## Recommended Project Structure

```
ellectric/
├── data/                          # Data layer (Stage 1)
│   ├── raw/                       # Downloaded raw data (PUDL SQLite, IEA CSV)
│   ├── processed/                 # Cleaned Parquet files
│   ├── external/                  # Weather data, holiday calendars
│   └── README.md                  # Data dictionary
│
├── src/
│   ├── data_pipeline/             # LAYER 1: Data ingestion & preprocessing
│   │   ├── __init__.py
│   │   ├── ingest.py             # Fetch from PUDL, IEA, local CSV
│   │   ├── clean.py              # Missing values, resampling, validation
│   │   ├── features.py           # Calendar features, lag features, weather
│   │   └── store.py              # Write to Parquet, read utilities
│   │
│   ├── prediction/                # LAYER 2: Forecasting models
│   │   ├── __init__.py
│   │   ├── load_forecast.py      # XGBoost baseline + OpenSTEF integration
│   │   ├── price_forecast.py     # LEAR model via epftoolbox
│   │   ├── renewable_forecast.py # Wind/solar generation prediction
│   │   └── evaluation.py         # MAE, RMSE, sMAPE, MASE metrics
│   │
│   ├── simulation/                # LAYER 3: Market simulation (ASSUME wrapper)
│   │   ├── __init__.py
│   │   ├── config/                # ASSUME scenario YAML/CSV configs
│   │   │   ├── market_config.yaml
│   │   │   ├── power_plants.csv
│   │   │   ├── demand_units.csv
│   │   │   └── renewables.csv
│   │   ├── scenarios/             # Pre-built learning scenarios
│   │   │   ├── basic_2unit/       # 2-unit market (warmup)
│   │   │   ├── multi_agent/       # Multiple generators + storage
│   │   │   └── renewable_pen/     # High renewable penetration
│   │   ├── runner.py             # Launch ASSUME simulations
│   │   └── results.py            # Parse simulation outputs
│   │
│   ├── agents/                    # LAYER 4: Trading strategies & RL
│   │   ├── __init__.py
│   │   ├── strategies/            # Custom bidding strategies
│   │   │   ├── base.py
│   │   │   ├── marginal_cost.py   # Bid at marginal cost
│   │   │   ├── markup.py          # Cost + markup
│   │   │   └── prediction_based.py # Use layer-2 forecasts
│   │   ├── rl/                    # RL agent wrappers
│   │   │   ├── env.py            # Gym-compatible trading environment
│   │   │   ├── agent.py          # DRL agent (TD3/SAC via stable-baselines3)
│   │   │   └── reward.py         # Custom reward functions
│   │   └── backtest.py           # Historical backtesting engine
│   │
│   ├── interface/                 # LAYER 5: API, CLI, Chatbot
│   │   ├── __init__.py
│   │   ├── api/                   # FastAPI application
│   │   │   ├── main.py           # App entry point
│   │   │   ├── routes/            # API endpoints
│   │   │   │   ├── data.py       # /data/* endpoints
│   │   │   │   ├── prediction.py  # /predict/* endpoints
│   │   │   │   ├── simulation.py # /simulate/* endpoints
│   │   │   │   └── backtest.py   # /backtest/* endpoints
│   │   │   └── schemas.py        # Pydantic models
│   │   ├── cli/                   # CLI commands
│   │   │   ├── main.py           # Typer/Click CLI entry
│   │   │   ├── data_cmd.py
│   │   │   ├── predict_cmd.py
│   │   │   └── simulate_cmd.py
│   │   └── chatbot/               # LLM chatbot
│   │       ├── agent.py          # LangChain agent with tools
│   │       ├── tools.py          # Function tools (predict, simulate, query)
│   │       └── prompts.py        # System prompts
│   │
│   └── shared/                    # Shared utilities
│       ├── __init__.py
│       ├── config.py             # Project-wide configuration (paths, params)
│       ├── types.py              # Shared data types/dataclasses
│       └── visualization.py      # Plotting utilities (matplotlib/plotly)
│
├── notebooks/                     # Jupyter notebooks for learning
│   ├── 01_data_exploration.ipynb
│   ├── 02_load_forecasting_xgboost.ipynb
│   ├── 03_price_forecasting.ipynb
│   ├── 04_assume_intro.ipynb
│   ├── 05_bidding_strategies.ipynb
│   ├── 06_rl_trading.ipynb
│   └── 07_full_pipeline.ipynb
│
├── tests/
│   ├── test_data_pipeline/
│   ├── test_prediction/
│   ├── test_agents/
│   └── test_interface/
│
├── requirements.txt               # Core dependencies
├── requirements-dev.txt           # Dev dependencies (pytest, black, etc.)
└── README.md
```

### Structure Rationale

- **`data/`:** Separate from `src/` — large binary files (SQLite, Parquet) not tracked in git. `.gitignore` excludes `data/raw/` and `data/processed/` beyond small samples.
- **`src/data_pipeline/`:** Isolated ingestion → clean → features pipeline. Can run independently before other layers exist. Produces Parquet files consumed by downstream layers via file paths.
- **`src/prediction/`:** Each forecaster is a standalone module. Can be trained/evaluated independently. Produces CSV/Parquet forecast outputs. Forecasters share a common `predict(horizon) → pd.DataFrame` interface.
- **`src/simulation/`:** Wraps ASSUME (not reinvents it). Configuration-driven — YAML/CSV files define the world. `runner.py` is a thin launcher. Scenario folders are self-contained (portable between learners).
- **`src/agents/`:** Strategy code separate from simulation engine. Strategies consume prediction outputs and produce bids. RL agents use a Gym-compatible environment wrapper that can use either ASSUME or a lightweight simulator.
- **`src/interface/`:** Three access modes (API, CLI, Chatbot) — all call the same underlying service layer. Chatbot tools are function-calling wrappers around CLI/API services.
- **`notebooks/`:** The primary learning surface. Each notebook walks through one concept end-to-end with explanatory text and executable code.
- **`src/shared/`:** Avoid circular dependencies. All layers import shared types and config from here.

## Architectural Patterns

### Pattern 1: Data Contract via DataFrame

**What:** Each layer communicates with the next through Pandas DataFrames (or file-based Parquet) with well-defined column schemas. No direct function calls between layers — data is materialized and passed.

**When to use:** Every inter-layer boundary.

**Trade-offs:**
- **Pro:** Each layer is independently debuggable — inspect intermediate DataFrames.
- **Pro:** Learners can replace one layer without touching others (e.g., swap XGBoost for LSTM).
- **Con:** File I/O overhead. Mitigated by using Parquet (fast, compressed) and in-memory DataFrame passing in notebooks.

**Example:**
```python
# Layer 1 → Layer 2 contract: cleaned_load.csv
# Columns: timestamp (UTC), load_mw (float), region (str)
# Frequency: hourly

# Layer 2 → Layer 3 contract: forecast_24h.csv
# Columns: timestamp, predicted_load_mw, predicted_price_eur_mwh, 
#           predicted_wind_mw, predicted_solar_mw
# Frequency: hourly, horizon: 24h

# Layer 3 → Layer 4 contract: market_results.csv
# Columns: timestamp, cleared_price, dispatched_mw, unit_id, profit_eur
```

### Pattern 2: Strategy Pattern for Bidding

**What:** Bidding strategies implement a common interface (`calculate_bids(state) → List[Order]`). The simulation engine calls this interface — it doesn't care if the strategy is rule-based, optimization-based, or RL-based.

**When to use:** Agent layer. ASSUME already implements this internally — our wrapper respects the same interface.

**Trade-offs:**
- **Pro:** Learners start with simple marginal-cost bidding, then upgrade to RL without changing simulation code.
- **Pro:** Backtesting can replay the same market against different strategies.
- **Con:** State representation must be standardized. Some strategies need more state than others (RL needs full observation space).

**Example:**
```python
# ASSUME already uses this pattern:
class BiddingStrategy(ABC):
    @abstractmethod
    def calculate_bids(self, unit, market_config, forecaster) -> List[Order]:
        ...

# Rule-based (Stage 2 - warmup):
class MarginalCostStrategy(BiddingStrategy):
    def calculate_bids(self, unit, market_config, forecaster):
        mc = unit.calculate_marginal_cost()
        max_power = unit.calculate_min_max_power()[1]
        return [Order(price=mc * 1.1, volume=max_power)]

# Prediction-based (Stage 3):
class ForecastBasedStrategy(BiddingStrategy):
    def __init__(self, price_forecast_df):
        self.forecast = price_forecast_df
    
    def calculate_bids(self, unit, market_config, forecaster):
        predicted_price = self.forecast.loc[timestamp, 'price']
        mc = unit.calculate_marginal_cost()
        # Only bid if predicted price > marginal cost
        if predicted_price > mc:
            return [Order(price=predicted_price * 0.95, volume=max_power)]
        return []
```

### Pattern 3: Pipeline with Checkpoints

**What:** Long-running pipelines (data → predict → simulate) save intermediate results to disk. Each stage checks for existing output and skips if already computed.

**When to use:** Data pipeline and backtesting.

**Trade-offs:**
- **Pro:** Faster iteration — change only the last stage.
- **Pro:** Reproducible — each checkpoint is a versioned artifact.
- **Con:** Cache invalidation complexity. Mitigated by content-hashing input configs.

**Example:**
```python
# In backtest.py:
def run_backtest(config: BacktestConfig):
    # Stage 1: Load/cache data
    data = load_or_compute("cache/cleaned_data.parquet", 
                           lambda: ingest_and_clean(config.data_start, config.data_end))
    
    # Stage 2: Generate predictions
    forecasts = load_or_compute("cache/forecasts.parquet",
                                lambda: generate_forecasts(data, config.model))
    
    # Stage 3: Run simulation
    results = load_or_compute("cache/results.parquet",
                              lambda: run_assume_simulation(forecasts, config.scenario))
    
    return results
```

### Pattern 4: Config-Driven Simulation

**What:** ASSUME simulations are defined entirely by YAML/CSV configuration files. No code changes needed to test different market designs, unit mixes, or strategies.

**When to use:** Simulation layer. Enables rapid experimentation.

**Example:**
```yaml
# config/market_config.yaml
markets:
  - name: EOM
    start: "2019-01-01 00:00"
    end: "2019-01-07 00:00"
    time_step: 1h
    market_mechanism: pay_as_clear
    clearing_algorithm: complex_clearing
    products:
      - type: energy
        duration: 1h
        count: 24
```

## Data Flow

### Complete Pipeline Flow

```
[Public Data Sources]
    │  PUDL, IEA, weather APIs
    ↓
┌───────────────────────────────────────┐
│ LAYER 1: DATA                          │
│                                         │
│ PUDL SQLite / IEA CSV                   │
│     → enda/pandas: resample, fill gaps  │
│     → Feature engineering (calendar,    │
│       weather, lags)                    │
│     → Store: Parquet files              │
│  Output: cleaned_load.parquet,          │
│          cleaned_price.parquet,         │
│          weather_features.parquet       │
└───────────────┬───────────────────────┘
                │
                ↓
┌───────────────────────────────────────┐
│ LAYER 2: PREDICTION                    │
│                                         │
│ Load Forecaster:                        │
│   features → XGBoost/OpenSTEF → load    │
│ Price Forecaster:                       │
│   features → LEAR/DNN → price           │
│ Renewable Forecaster:                   │
│   weather → physics/ML → wind, solar    │
│                                         │
│  Output: forecast_24h.parquet with      │
│   columns: [timestamp, load_mw,         │
│   price_eur_mwh, wind_mw, solar_mw]    │
└───────────────┬───────────────────────┘
                │
                ↓
┌───────────────────────────────────────┐
│ LAYER 3: MARKET SIMULATION (ASSUME)    │
│                                         │
│ World.setup(config.yaml)                │
│   → Creates markets, units, operators   │
│   → Forecaster.init_forecasts()         │
│     → Reads forecast_24h.parquet        │
│ World.run()                             │
│   → Clock ticks (hourly)                │
│   → Market opens → agents bid → clear   │
│   → Results stored (TimescaleDB/CSV)    │
│                                         │
│  Output: results.csv with columns:      │
│   [timestamp, market, unit_id,          │
│    bid_price, bid_volume, cleared_price, │
│    dispatched_mw, profit_eur]           │
└───────────────┬───────────────────────┘
                │
                ↓
┌───────────────────────────────────────┐
│ LAYER 4: AGENT / BACKTEST              │
│                                         │
│ Backtest Engine:                        │
│   → Loop over historical windows       │
│   → For each window:                    │
│       1. Generate forecasts from data   │
│       2. Run ASSUME with strategy       │
│       3. Collect metrics (PnL, Sharpe,  │
│          win rate)                      │
│   → Compare strategies                  │
│                                         │
│ RL Training Loop:                       │
│   → Environment = ASSUME wrapper        │
│   → Agent observes state (forecasts,    │
│     portfolio, market history)          │
│   → Action = bid (price, volume)        │
│   → Reward = profit or risk-adjusted    │
│   → Train via TD3/SAC/PPO              │
└───────────────┬───────────────────────┘
                │
                ↓
┌───────────────────────────────────────┐
│ LAYER 5: INTERFACE                     │
│                                         │
│ FastAPI:                                │
│   POST /predict → returns forecast      │
│   POST /simulate → runs ASSUME → JSON   │
│   GET  /results/{run_id} → metrics      │
│                                         │
│ CLI:                                    │
│   $ ellectric predict --horizon 24h     │
│   $ ellectric simulate --scenario basic │
│   $ ellectric backtest --strategy rl    │
│                                         │
│ LLM Chatbot:                            │
│   User: "What will tomorrow's load be?" │
│   → Tool call: run_load_forecast()      │
│   → Response: "Predicted load: 450MW    │
│     peak at 18:00, min 280MW at 04:00"  │
└───────────────────────────────────────┘
```

### Key Data Contract Schemas

**Cleaned Data Schema (Layer 1 → 2):**
| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime64[ns, UTC] | Hourly index |
| `load_mw` | float64 | Actual system load |
| `price_eur_mwh` | float64 | Day-ahead clearing price |
| `wind_mw` | float64 | Actual wind generation |
| `solar_mw` | float64 | Actual solar generation |
| `temp_c` | float64 | Temperature |
| `hour` | int8 | 0-23 |
| `day_of_week` | int8 | 0=Monday |
| `is_holiday` | bool | Public holiday flag |
| `month` | int8 | 1-12 |

**Forecast Schema (Layer 2 → 3):**
| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime64[ns, UTC] | Forecast target hour |
| `predicted_load_mw` | float64 | Load forecast |
| `predicted_price_eur_mwh` | float64 | Price forecast |
| `predicted_wind_mw` | float64 | Wind gen forecast |
| `predicted_solar_mw` | float64 | Solar gen forecast |
| `forecast_created_at` | datetime64[ns, UTC] | When forecast was generated |

**Market Results Schema (Layer 3 → 4):**
| Column | Type | Description |
|--------|------|-------------|
| `simulation_id` | str | Unique run identifier |
| `timestamp` | datetime64[ns, UTC] | Dispatch hour |
| `market` | str | "EOM" or "CRM" |
| `unit_id` | str | Generator/unit identifier |
| `unit_type` | str | "power_plant", "storage", "demand", "renewable" |
| `bid_price` | float64 | Submitted bid price |
| `bid_volume` | float64 | Submitted bid volume (MW) |
| `cleared_price` | float64 | Market clearing price |
| `dispatched_mw` | float64 | Actual dispatch (MW) |
| `marginal_cost` | float64 | Unit's marginal cost |
| `revenue_eur` | float64 | Revenue from dispatch |
| `profit_eur` | float64 | Revenue minus cost |

### State Management

- **Configuration:** YAML/CSV files in `src/simulation/config/` and scenario folders. No runtime state — everything is declarative.
- **Simulation State:** Managed entirely by ASSUME's `World` class and mango agent framework. We don't reimplement this.
- **Model Artifacts:** Trained models saved as `.pkl` (XGBoost, scikit-learn) or `.pt` (PyTorch RL policies) in `models/` directory.
- **API State:** FastAPI is stateless. Run metadata stored in SQLite (`results.db`).
- **Chatbot:** LangChain conversation memory (buffer) — ephemeral, not persisted.

## Building / Build Order Implications

The architecture implies a strict build order matching the four-stage learning roadmap:

### Phase 1: Data Foundation + Basic Prediction
**Build:** `src/data_pipeline/` + basic `src/prediction/load_forecast.py`
- Data ingestion from PUDL or IEA
- Data cleaning pipeline
- Simple XGBoost load predictor
- **Why first:** Everything downstream needs clean data. Basic prediction validates the pipeline works.
- **Dependencies:** None (standalone)
- **Deliverable:** Working notebook showing "data → load forecast"

### Phase 2: Deep Prediction + Market Simulation Introduction
**Build:** Full `src/prediction/` + `src/simulation/` (ASSUME setup)
- OpenSTEF integration for automated ML forecasting
- Price forecasting with epftoolbox
- ASSUME installation and basic scenarios (2-unit market)
- **Why second:** Predictions feed simulation. ASSUME is the platform for all later trading work.
- **Dependencies:** Phase 1 (needs clean data)
- **Deliverable:** Running ASSUME simulation with naive strategies

### Phase 3: Trading Agents
**Build:** `src/agents/` (strategies, RL, backtesting)
- Custom bidding strategies (marginal cost, markup, prediction-based)
- RL agent training (ASSUME's learning capabilities)
- Historical backtesting engine
- **Why third:** Strategies are meaningless without a market to test in. SIMULATION MUST EXIST FIRST.
- **Dependencies:** Phase 2 (needs ASSUME + predictions)
- **Deliverable:** RL agent outperforms naive strategy in backtest

### Phase 4: Integration + LLM Interface
**Build:** `src/interface/` (API, CLI, Chatbot)
- FastAPI wrapping all pipeline stages
- CLI with subcommands for each layer
- LangChain chatbot with tool-calling
- **Why last:** Interface layer wraps all previous layers. Everything underneath must be stable.
- **Dependencies:** Phases 1-3 (all layers)
- **Deliverable:** End-to-end "ask chatbot → get prediction → run simulation" flow

### Phase Dependency Graph

```
Phase 1 (Data + Basic Predict)
    │
    ├──→ Phase 2 (Deep Predict + Market Sim)
    │        │
    │        ├──→ Phase 3a (Rule-Based Strategies)
    │        │        │
    │        │        └──→ Phase 3b (RL Agents)
    │        │                 │
    │        │                 └──→ Phase 4 (Interface)
    │        │
    │        └──→ Phase 2b (Price Forecast Enhancement)
    │
    └──→ Notebooks (ongoing across all phases)
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **Learning (1 user)** | All layers run in single process. Data is small (<1GB). SQLite + Parquet on local disk. Model training on CPU (XGBoost). ASSUME with <20 units. |
| **Research (1-5 users)** | Add Docker Compose for reproducibility. ASSUME with 50+ units, 1-year simulation. DuckDB replaces SQLite for faster analytical queries. GPU optional for RL training. |
| **Classroom (20+ users)** | Pre-built Docker image with all dependencies. Pre-downloaded data in image. Cloud JupyterHub. Each learner gets isolated environment. |
| **Production-scale** | Out of scope per project constraints. |

### Scaling Priorities

1. **First bottleneck:** ASSUME simulation speed with many agents. Mitigation: Use ASSUME's built-in parallel execution (distributed simulation with mango containers).
2. **Second bottleneck:** Data volume (years of hourly data). Mitigation: DuckDB (columnar, fast analytical queries) over SQLite.

## Anti-Patterns

### Anti-Pattern 1: Monolithic Notebook

**What people do:** Put everything in one massive Jupyter notebook — data loading, cleaning, training, simulation, plotting.

**Why it's wrong:** Unrunnable independently. Can't swap one piece. Restart kernel = rerun everything. Impossible to test.

**Do this instead:** Each layer is a Python module with functions. Notebooks import from modules and are thin (visualization + narrative). The modules are unit-testable.

### Anti-Pattern 2: Reinventing Market Simulation

**What people do:** Write their own order book, clearing engine, unit models from scratch "to learn how it works."

**Why it's wrong:** Electricity market simulation is extremely complex (block orders, linked orders, network constraints, redispatch). Months of work to get a buggy version. No time left for the AI/learning part — which is the actual goal.

**Do this instead:** Use ASSUME as the simulation engine. Wrap it, configure it, extend its strategies. ASSUME already handles the market mechanics correctly. Focus learning energy on prediction models and trading strategies — where the AI value is.

### Anti-Pattern 3: Tight Coupling Between Prediction and Trading

**What people do:** Trading strategy code directly calls prediction models inline.

**Why it's wrong:** Can't backtest against different prediction quality levels. Can't swap XGBoost for LSTM without touching strategy code. Can't evaluate prediction and strategy separately.

**Do this instead:** Predictions are materialized as DataFrames/files. Trading strategies consume prediction DataFrames through a defined interface. Backtesting replays different prediction files against the same strategy.

### Anti-Pattern 4: Premature LLM Integration

**What people do:** Start building the chatbot before the pipeline works.

**Why it's wrong:** The chatbot is a thin wrapper around function tools. If the underlying functions don't work, the chatbot hallucinates, errors compound, and the learner loses trust.

**Do this instead:** Every function tool MUST be a working CLI command first. Chatbot is the LAST layer added — only when all pipelines are proven stable.

## Learning Objective Mapping

| Component | Learning Objective |
|-----------|-------------------|
| `data_pipeline/ingest.py` | How to fetch and version public energy datasets |
| `data_pipeline/clean.py` | Time-series data quality: gaps, resampling, UTC handling |
| `data_pipeline/features.py` | Domain-specific feature engineering for energy |
| `prediction/load_forecast.py` | ML pipeline: train/test split, feature importance, evaluation |
| `prediction/price_forecast.py` | Day-ahead market mechanics, LEAR model, forecast benchmarking |
| `simulation/config/` | Electricity market design: EOM, clearing mechanisms, product types |
| `simulation/runner.py` | Running multi-agent simulations at scale |
| `agents/strategies/marginal_cost.py` | Generator cost structures, merit order, bid formulation |
| `agents/rl/` | Reinforcement learning: state/action/reward design, DRL algorithms |
| `agents/backtest.py` | Strategy evaluation: Sharpe ratio, PnL, drawdown, statistical tests |
| `interface/api/` | Building production-ready Python APIs with FastAPI |
| `interface/chatbot/` | LLM function calling, prompt engineering, tool composition |

## Integration Points

### External Libraries

| Library | Integration Pattern | Notes |
|---------|---------------------|-------|
| **ASSUME** | Imported as `assume` package. Scenario configs in YAML/CSV. Our code wraps `World.setup()` and `World.run()`. | AGPL-3.0 license. Install `pip install assume-framework[learning]`. |
| **OpenSTEF** | Import `openstef` for automated ML pipeline. Use its `openstef.model` and `openstef.pipeline` modules. | MPL-2.0 license. Requires custom database connector or file-based fallback. |
| **enda** | Import `enda` for timeseries utilities: `enda.timeseries`, `enda.feature_engineering`. | MIT license. Lightweight, no database dependency. |
| **epftoolbox** | Import `epftoolbox` for LEAR model and benchmark datasets. | Apache-2.0 license. Includes 5 market datasets. |
| **PUDL** | Use `pudl` Python package or download pre-built SQLite from Kaggle/AWS. | MIT license. 500MB+ SQLite database. |
| **LangChain** | `langchain` + `langchain-openai` or `langchain-ollama` for chatbot. | MIT license. |
| **FastAPI** | Standard FastAPI + Pydantic v2 for REST API. | MIT license. |
| **stable-baselines3** | Imported internally by ASSUME for RL. We extend via ASSUME's strategy interface. | MIT license. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Data → Prediction | Parquet file (path passed as config) | Schema defined in `shared/types.py` |
| Prediction → Simulation | DataFrame passed to ASSUME forecaster or CSV file | ASSUME natively supports CSV forecast input |
| Simulation → Agent | ASSUME outputs CSV → parsed by backtest engine | Or direct Python object if running inline |
| Agent → Interface | Function calls within same process | All pipeline stages are importable Python functions |
| Interface → User | JSON (API), text (CLI), natural language (Chatbot) | Three parallel access modes |

## Sources

- **ASSUME Framework Architecture:** https://assume.readthedocs.io/en/latest/introduction.html#architecture (official docs, HIGH confidence)
- **ASSUME API Reference:** https://assume.readthedocs.io/en/latest/assume.html (official docs, HIGH confidence)
- **ASSUME Unit Forecasts:** https://assume.readthedocs.io/en/latest/unit_forecasts.html (official docs, HIGH confidence)
- **OpenSTEF GitHub:** https://github.com/OpenSTEF/openstef (official repo, HIGH confidence)
- **enda GitHub:** https://github.com/enercoop/enda (official repo, HIGH confidence)
- **epftoolbox GitHub:** https://github.com/jeslago/epftoolbox (official repo, HIGH confidence)
- **PUDL GitHub:** https://github.com/catalyst-cooperative/pudl (official repo, HIGH confidence)
- **ASSUME Paper (SoftwareX 2025):** Harder et al., "ASSUME: An agent-based simulation framework for exploring electricity market dynamics with reinforcement learning" (peer-reviewed, HIGH confidence)
- **epftoolbox Paper (Applied Energy 2021):** Lago et al., "Forecasting day-ahead electricity prices" (peer-reviewed, HIGH confidence)

---

*Architecture research for: AI-driven electricity trading learning platform*
*Researched: 2026-05-20*
