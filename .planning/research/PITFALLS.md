# Pitfalls Research

**Domain:** AI-driven electricity trading learning platform
**Researched:** 2026-05-20
**Confidence:** HIGH

> Sources: ASSUME official docs (assume.readthedocs.io), epftoolbox docs, OpenSTEF GitHub, ASSUME release notes v0.1.0–v0.6.1, JOSS paper (Harder et al. 2025), Energy and AI paper (Harder et al. 2023).

## Critical Pitfalls

Mistakes that cause silently wrong results — the prediction looks good, the simulation runs, but the conclusions are invalid.

### Pitfall 1: Look-Ahead Bias in Time-Series Data Preparation

**What goes wrong:**
The model accidentally sees future information during training. In electricity forecasting, this manifests as:
- Computing rolling statistics (moving average, standard deviation) over the full dataset before splitting
- Normalizing/scaling features using mean and std computed across the entire time range
- Using `train_test_split(random_state=42)` instead of temporal splitting
- Including "tomorrow's weather forecast" as a feature when that forecast itself embeds future information

The model achieves unrealistically high accuracy during validation but fails completely on live data.

**Why it happens:**
Standard ML tooling (`sklearn.preprocessing.StandardScaler`, `sklearn.model_selection.train_test_split`) is designed for i.i.d. data. Energy time series are NOT i.i.d. — hour t is highly correlated with hour t-1. Beginners apply ML workflows they learned from classification/image problems directly to temporal energy data without adapting the preprocessing pipeline.

**How to avoid:**

```python
# WRONG: Fit scaler on full dataset before splitting
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_all)  # LEAKS future into training!
X_train, X_test = train_test_split(X_scaled, shuffle=False)

# RIGHT: Fit scaler ONLY on training data
split_idx = int(len(X_all) * 0.8)
X_train, X_test = X_all[:split_idx], X_all[split_idx:]

scaler = StandardScaler()
scaler.fit(X_train)  # Only fit on training period
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# RIGHT: Use TimeSeriesSplit for cross validation
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
for train_idx, val_idx in tscv.split(X):
    # train_idx always < val_idx temporally
    X_train, X_val = X[train_idx], X[val_idx]
```

**Key principle:** Any operation that derives statistics from data (scaling, imputation, feature engineering) must ONLY use data from timestamps ≤ the current training cutoff.

**Warning signs:**
- Validation MAE is implausibly low (< 1%) for electricity price prediction
- Model performs better on test set than training set
- `TimeSeriesSplit` or `BlockingTimeSeriesSplit` NOT visible in the codebase
- Feature importance shows "tomorrow" features dominating

**Phase to address:** Phase 1 (PRED-01 / DATA-01). This MUST be prevented before any model is trained.

**Recovery cost:** HIGH — requires re-doing all feature engineering and retraining from scratch.

---

### Pitfall 2: Treating Electricity Prices Like a "Normal" Commodity — Squashing Price Spikes

**What goes wrong:**
Electricity prices exhibit extreme characteristics unseen in other commodities:
- **Negative prices** (producers PAY to offload power during renewable oversupply)
- **Price spikes of 10-100x mean** (e.g., EPEX day-ahead: mean ~€50/MWh, spikes to €500-3000/MWh)
- **Zero prices** (perfect renewable/load balance)
- **Multi-modal distributions** (spike regime vs. normal regime vs. negative regime)

Beginners apply standard ML loss functions (MSE, RMSE) and preprocessing (log-transform, clipping outliers) that destroy the very signal that matters for trading. A model with great RMSE can miss every price spike — making it useless for trading.

**Why it happens:**
Beginners learn ML on well-behaved datasets (housing prices, image classification) where outliers are noise to be removed. In electricity, the "outliers" ARE the signal — the spikes are when trading makes or loses money.

**How to avoid:**

```python
# WRONG: Clipping "outliers" destroys trading signal
prices_clipped = prices.clip(lower=prices.quantile(0.01),
                              upper=prices.quantile(0.99))

# WRONG: Log-transform makes spike detection impossible
prices_log = np.log(prices)  # What does log(-50) mean?

# RIGHT: Use metrics that capture spike performance
from epftoolbox.evaluation import MAE, sMAPE, MASE

# ALSO compute spike-specific metrics
spike_threshold = prices.quantile(0.95)
spike_mask = y_true > spike_threshold
spike_mae = np.mean(np.abs(y_true[spike_mask] - y_pred[spike_mask]))
spike_recall = np.sum((y_pred > spike_threshold) & spike_mask) / np.sum(spike_mask)

# Use pinball loss / quantile regression for probabilistic forecasts
# that capture tail behavior
```

**Key metrics for electricity trading (beyond RMSE):**
| Metric | What it captures |
|--------|-----------------|
| sMAPE | Scale-independent error |
| MASE | Relative to naive forecast |
| Diebold-Mariano test | Statistical significance vs baseline |
| Spike MAE / Spike Recall | Performance on extreme events |
| Profit & Loss (PnL) | Real economic value of forecasts |

**Warning signs:**
- Clipping or outlier removal in the preprocessing pipeline
- Using only RMSE/MAE as evaluation metrics
- Prediction plot never exceeds ±2σ of training data
- Using `np.log()` or `BoxCox` on raw prices without handling negatives

**Phase to address:** Phase 1 (PRED-01). Establish correct evaluation before training.

---

### Pitfall 3: RL Reward Function Design That Optimizes the Wrong Thing

**What goes wrong:**
In reinforcement learning for electricity trading, the reward function defines what the agent optimizes. Common failures:
- **Pure profit maximization without risk penalty** → Agent learns degenerate strategies (bid at max price, only get accepted when market spikes, zero volume 95% of time but huge reward on spikes)
- **Reward based on accepted bids only** → Agent learns to underbid everyone, gets high acceptance rate but negative margins
- **No penalty for unused capacity** → Agent sits idle as "safe" strategy
- **Reward only at episode end** → Sparse signal, agent never learns

The ASSUME documentation explicitly warns: *"Do not rely on rewards alone. Behavior itself must be examined carefully."* and *"A larger total reward does NOT imply that the learned behavior is better."*

**Why it happens:**
Reward function design is deceptively hard. Beginners copy reward structures from Atari games or robotics papers where rewards are exogenous. In markets, rewards emerge from agent interactions — the same policy earns different rewards against different opponents. High rewards can come from "temporary exploitation of weaknesses of other agents" or "coordination effects that occur by chance."

**How to avoid:**

```python
# ASSUME's learning reward (from official docs) includes multiple terms:
# reward = profits_from_executed_bids
#          - operational_costs
#          - opportunity_costs (penalizing underutilized capacity)
#          - regret_term (minimizing missed revenue opportunities)

# START SIMPLE: Begin with naive/heuristic strategies before adding RL
# In ASSUME config:
bidding_EOM: "powerplant_energy_naive"  # Phase 1: baseline
bidding_EOM: "powerplant_energy_heuristic_flexable"  # Phase 2: heuristic
bidding_EOM: "powerplant_energy_learning"  # Phase 3: RL only after baselines

# ALWAYS validate behavior, not just reward:
# 1. Plot bid curves over time — are they reasonable?
# 2. Check acceptance rate — is agent actually participating?
# 3. Compare PnL against naive strategy — is RL adding value?
# 4. Use ASSUME's built-in Grafana dashboards for behavior inspection
```

**ASSUME-specific RL safety checks (from official docs):**
- Use `validation_episodes_interval` to evaluate without exploration noise
- Use `early_stopping` with large episodes to avoid selecting unstable high-reward snapshots
- Use the **final policy** (not best-reward policy) for evaluation — ASSUME docs: *"the framework uses the final policy for evaluation to avoid selecting a high-reward snapshot that may be far from stable"*
- Monitor TensorBoard for reward stability, not just reward magnitude
- Set `train_freq` > "72h" for storage units (they need time coupling)

**Warning signs:**
- Agent reward increasing but bid acceptance rate dropping to zero
- Agent learns to always bid at extreme prices (min or max)
- Reward curve is highly volatile with sudden spikes
- Agent behavior differs dramatically between consecutive training episodes

**Phase to address:** Phase 3 (AGENT-01, AGENT-02). Use naive/heuristic baselines from Phase 1-2 to validate RL learning.

**Recovery cost:** HIGH — may require complete reward redesign and retraining.

---

### Pitfall 4: Unrealistic Market Assumptions — Running a "Perfect" Market

**What goes wrong:**
Beginners simulate electricity markets with assumptions that don't hold in reality:
- **No transmission constraints** → Every generator can serve every load (real markets have congestion)
- **No market power** → All agents are price-takers (real markets have oligopolistic generators)
- **Single market only** → Only day-ahead energy market (reality: day-ahead + intraday + real-time + ancillary services + capacity markets)
- **No renewable intermittency** → Perfect foresight of wind/solar (reality: forecast errors create balancing needs)
- **No dual settlement** → Ignoring day-ahead vs. real-time price divergence
- **Single clearing price everywhere** → Ignoring nodal/zonal price differences

The result: trading strategies that work beautifully in simulation but would lose money in reality.

**Why it happens:**
Simplifying assumptions are natural when learning. But electricity markets have specific structural features that fundamentally change optimal strategies. A strategy optimized for a congestion-free, single-price market will fail in a market with transmission bottlenecks.

**How to avoid:**

```python
# ASSUME supports realistic market configurations:
# config.yaml example:
market_config:
  market_id: "EOM"
  market_mechanism: "pay_as_clear"  # or "pay_as_bid", "complex_clearing"
  # For zonal pricing with transmission constraints:
  # market_mechanism: "complex_clearing" + grid data
  # For nodal pricing:
  # market_mechanism: "nodal_clearing" + PyPSA network

# Always include at minimum:
# 1. Merit-order-based clearing (not uniform price assumption)
# 2. Multiple unit types with different marginal costs
# 3. Some form of demand elasticity
# 4. Renewable generation with realistic availability profiles

# START WITH: ASSUME's built-in example scenarios (example_01a, example_03)
# These already include realistic German market configurations
```

**Progressive realism approach:**
1. **Phase 2 (SIM-01):** Single-zone, pay-as-clear, no congestion — learn market mechanics
2. **Phase 3 (SIM-02/AGENT-01):** Add transmission constraints, zonal pricing, multiple markets
3. **Phase 4 (advanced):** Complex clearing with block/linked bids, redispatch, nodal pricing

**Warning signs:**
- All generators in your simulation always get dispatched
- Price is always within a narrow band
- No price difference between zones/nodes
- 100% renewable utilization without curtailment
- No negative prices ever appear

**Phase to address:** Phase 2 (SIM-01) and Phase 3 (SIM-02, AGENT-01).

---

### Pitfall 5: Not Running End-to-End Early — The "Perfect Model, No Integration" Trap

**What goes wrong:**
Learners spend weeks perfecting a load prediction model (RMSE optimization, hyperparameter tuning, fancy architectures) before ever connecting it to a market simulation or trading agent. When they finally integrate, they discover:
- The prediction format doesn't match what the simulation expects (24h window vs. 1h, different timezone)
- The model was optimized for accuracy metrics that don't translate to trading PnL
- The pipeline latency makes predictions stale before they reach the agent
- Real data has gaps/holidays/timezone shifts the model can't handle

**Why it happens:**
Academic ML culture rewards accuracy leaderboards. Industry rewards working systems. Learners default to the academic pattern because it's what tutorials and Kaggle competitions reinforce.

**How to avoid:**

```python
# Phase 1: End-to-end in ONE DAY
# Day 1 workflow:
# 1. Load PUDL data (2 hours)
# 2. Train a trivial model: predict next hour = last hour (10 minutes)
# 3. Plug naive forecast into a minimal market simulation (1 hour)
# 4. See prices, see if "trading" with naive forecast makes/loses money
# RESULT: You've run the full loop. Now improve each piece.

# This "naive end-to-end" validates:
# - Data pipeline works
# - Forecast format matches simulation input
# - You know what "better" means (beating naive baseline PnL)
# - You discover integration issues on Day 1, not Week 8
```

**The progressive integration principle:**
| Phase | Model sophistication | Integration depth |
|-------|---------------------|-------------------|
| Phase 1 (Week 1-2) | Naive persistence | Full pipeline working |
| Phase 2 (Week 3-8) | XGBoost + OpenSTEF | With ASSUME simulation |
| Phase 3 (Week 8-12) | RL agent | Prediction → Simulation → Trading |
| Phase 4 (Week 12+) | LLM + advanced | Full platform backend |

**Warning signs:**
- You've been working on "improving the model" for 2+ weeks without running the downstream simulation
- Your evaluation script doesn't import anything from the simulation/trading modules
- You have 5 model variants but 0 end-to-end runs

**Phase to address:** Phase 1. This is a process discipline, not a code fix.

---

### Pitfall 6: Confusing Day-Ahead Settlement with Real-Time — The Dual Settlement Gap

**What goes wrong:**
Electricity markets operate on a dual-settlement system: day-ahead market (DAM) + real-time market (RTM). Beginners model only the day-ahead market, assuming:
- Day-ahead price = real-time price (they diverge significantly)
- All power is traded day-ahead (actually ~80-90%, rest in intraday/real-time)
- Settlement is a single transaction (reality: day-ahead is a financial commitment, real-time settles physical deviations)

A strategy that looks profitable day-ahead can hemorrhage money in real-time settlement due to imbalance charges, especially for intermittent generators.

**Why it happens:**
Most public datasets and tutorials focus on day-ahead prices because they're more available. Real-time market data is harder to find. The dual-settlement mechanism is also genuinely complex and easy to overlook.

**How to avoid:**

```python
# Key market concepts to model (even approximately):

# 1. DAM price != RTM price
# In PJM 2019-2023, DAM-RTM spread had std dev of ~$8/MWh
# Episodes of $100+/MWh divergence during extreme events

# 2. Imbalance settlement: generators pay for deviations
# If you bid 100 MW day-ahead but only generate 80 MW (wind drops):
# You must buy 20 MW in real-time at potentially much higher prices

# 3. ASSUME supports sequential market participation:
# Configure multiple markets (EOM day-ahead + CRM/intraday)
# Learning agents in ASSUME can now participate in sequential markets
# (Added in v0.4.0: "Learning agents to participate in sequential markets")

# Minimum realistic setup:
market_configs = [
    {"market_id": "EOM", "product_type": "energy_day_ahead"},
    {"market_id": "CRM_pos", "product_type": "capacity_reserve_pos"},
    {"market_id": "CRM_neg", "product_type": "capacity_reserve_neg"},
]
```

**Warning signs:**
- Your simulation has only one market
- You never compute imbalance costs/charges
- You assume generation = bid volume exactly
- Your PnL is just `price × volume` with no adjustment

**Phase to address:** Phase 2 (SIM-01) — introduce dual settlement concept. Phase 3 — implement in simulation.

---

## Moderate Pitfalls

### Pitfall 7: Using XGBoost Without Temporal Awareness — Feature Engineering on Full Dataset

**What goes wrong:**
Engineers create lag features (price_t-1, price_t-24, price_t-168) correctly, then do feature selection or importance ranking on the FULL dataset (including test period). This leaks future information through the feature selection process itself.

**How to avoid:**
```python
# WRONG: Feature selection before split
from sklearn.feature_selection import mutual_info_regression
mi = mutual_info_regression(X_all, y_all)  # LEAKS

# RIGHT: Feature selection inside each time-series fold
for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
    X_t, y_t = X[train_idx], y[train_idx]
    mi = mutual_info_regression(X_t, y_t)  # Only on training data
    selected_features = features[mi > threshold]
```

**Warning signs:** Feature selection code that doesn't reference `train_idx`/`val_idx`.

**Phase to address:** Phase 1 (PRED-01).

---

### Pitfall 8: Survivorship Bias in Backtesting — Only Testing on "Normal" Periods

**What goes wrong:**
Backtesting a trading strategy on 2017-2019 (stable markets) and concluding it works. The strategy would have failed catastrophically during:
- Texas 2021 winter storm (ERCOT prices hit $9,000/MWh cap)
- European energy crisis 2022 (EPEX prices 5-10x historical average)
- Any period of extreme renewable drought or transmission failure

**How to avoid:**
```python
# Always test on stress periods
test_periods = [
    ("2017-01-01", "2019-12-31"),  # Normal
    ("2020-01-01", "2020-06-30"),  # COVID demand shock
    ("2021-06-01", "2021-09-30"),  # European gas price spike begins
    ("2022-01-01", "2022-12-31"),  # Full energy crisis
]

for name, (start, end) in test_periods:
    results[name] = backtest(strategy, prices[start:end])

# Strategy should survive (not necessarily profit) in all periods
```

**Phase to address:** Phase 3 (AGENT-02) — include stress-test scenarios.

---

### Pitfall 9: Ignoring the Merit Order Effect — Assuming Flat Supply Curves

**What goes wrong:**
Learners model electricity supply as a simple production function: `price = f(demand, fuel_cost)`. This misses the fundamental market mechanism: the merit order. Generators are dispatched from cheapest to most expensive. As demand increases, more expensive generators (gas peakers, oil) set the price. A small demand increase can cause a massive price jump when it crosses a merit order "step."

**How to avoid:**
```python
# ASSUME implements merit order naturally through its bidding mechanism
# Each unit bids at its marginal cost — the market clearing finds the intersection

# Understanding merit order helps debug simulation results:
# If your simulated prices are too flat, check:
# 1. Are you including peaking units (high marginal cost)?
# 2. Is your demand varying enough to cross merit order steps?
# 3. Are you modeling renewable must-run (zero marginal cost)?

# ASSUME visualizations include Merit Order plots on the Grafana dashboard
# (added in v0.5.1) — use these to verify realistic merit order behavior
```

**Phase to address:** Phase 2 (SIM-01).

---

### Pitfall 10: Pipeline Coupling — Forecast and Trading in Same Process

**What goes wrong:**
The prediction model and trading agent are tightly coupled — the agent directly calls `model.predict()`. This makes it impossible to:
- Update the model without restarting the agent
- Compare different models with the same agent
- Simulate forecast delays or errors
- Test the agent with "perfect foresight" (useful for establishing upper bound)

**How to avoid:**
```python
# Interface-based separation:
class ForecastProvider(Protocol):
    def get_forecast(self, timestamp: pd.Timestamp,
                     horizon_hours: int) -> pd.DataFrame:
        """Returns forecast for next horizon_hours from timestamp."""
        ...

# The trading agent consumes ANY ForecastProvider:
class TradingAgent:
    def __init__(self, forecast_provider: ForecastProvider):
        self.forecast = forecast_provider

    def decide(self, timestamp: pd.Timestamp):
        pred = self.forecast.get_forecast(timestamp, horizon_hours=24)
        # Use pred to make trading decisions...

# Now you can swap:
# - NaiveForecastProvider (baseline)
# - XGBoostForecastProvider
# - PerfectForesightProvider (cheating — establish upper bound)
# - OpenSTEFForecastProvider
# - DelayedForecastProvider (simulate 1-hour data delay for realism)
```

**Phase to address:** Phase 3 (AGENT-01) — design the interface, Phase 4 (INTG-01) — formalize.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hard-coding market parameters (price caps, ramp rates) in code | Fast to write | Must change code when switching markets (e.g., PJM→EPEX) | Only in exploratory notebooks |
| Using `pd.read_csv()` directly in model code | No abstraction overhead | Can't swap data sources (PUDL → IEA → live API) | Phase 1 only |
| Storing predictions as CSV files | Simple, human-readable | Pipeline breaks when format drifts; no versioning | Phase 1 discovery only |
| Training on one year, testing on the same year (random split) | "Great" metrics | Model is useless; you haven't tested generalization | NEVER |
| Ignoring timezone handling (assuming UTC everywhere) | One less thing to think about | European market data in CET/CEST; US data in multiple timezones; DST transitions create 23h or 25h days | NEVER for multi-market |
| Using global `random.seed(42)` without controlling PyTorch seeds | Reproducible-ish | ASSUME docs: "Completely reproducible results are not guaranteed across different PyTorch versions, hardware, or CUDA configurations." RL performance degrades with fixed seeds. | Acceptable for XGBoost; use `seed: null` in ASSUME config for RL |
| Training RL on a single episode type | Fast iteration | Agent overfits to that scenario; fails on market regime changes | First RL experiments only |

## Integration Gotchas

Common mistakes when connecting components.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| PUDL → Forecast Model | Using raw PUDL tables without understanding EIA data model (generator IDs, fuel types, timezone handling) | Read PUDL documentation; use PUDL's built-in data validation; expect 6-12 month data lag |
| Forecast → ASSUME | Forecast format mismatch: ASSUME expects specific column names and timezone-aware DatetimeIndex | Use ASSUME's `forecast_df.csv` format; verify column names match `forecast_algorithms` config |
| ASSUME → Grafana | Expecting real-time dashboard updates during long simulations | ASSUME writes to TimescaleDB; Grafana refreshes on configurable interval; use TensorBoard for RL training progress (real-time) |
| OpenSTEF pipeline | Installing without reading CPU-only XGBoost note | `pip install openstef[cpu]` on x86_64 Linux; full XGBoost on macOS Apple Silicon needs special setup (brew libomp) |
| Multiple learning agents | Too many gradient steps per timestep | ASSUME docs: "For environments with many agents one should use not many gradient steps, as policies of other agents are updated as well outdating the current best strategy" |
| RL across episodes | Buffer/update ordering bug (fixed in v0.6.1) | Update to latest ASSUME; if stuck on old version, verify buffer writes occur before policy updates |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| ASSUME simulation with many RL agents on CPU | Training time increases super-linearly | Use CUDA if available; limit concurrent learning agents; use v0.5.1+ (2x-5x speedup) | >4 learning agents |
| Full PyPSA network optimization every market clearing | Simulation crawls for year-long scenarios | ASSUME v0.6.0+: solver instance is reused across clearings (major optimization) | >1 month simulation horizon |
| Pandas `.loc[]` in simulation hot loop | Simulation 10x slower than necessary | ASSUME v0.5.0+ uses custom FastIndex/FastSeries (2-3x speedup). For custom code: use numpy arrays in core loops. | >100 units |
| Storing all RL replay buffer data in memory | OOM for multi-agent, year-long training | `replay_buffer_size: 500000` is default; reduce for memory-constrained setups | >5 agents, >1 year horizon |
| `batch_size: 128` with many learning agents | GPU memory exhaustion | ASSUME docs: "In environments with many learning agents we advise small batch sizes" | >8 agents on consumer GPU |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Load forecasting model:** Often missing backtest on out-of-sample periods — verify temporal split, not random split
- [ ] **Price forecasting model:** Often evaluated only with RMSE — verify spike recall, PnL impact, and statistical significance (Diebold-Mariano test)
- [ ] **Market simulation:** Often runs without verifying against historical prices — verify simulated prices correlate with real market data for same period (r > 0.6 for day-ahead mean price)
- [ ] **RL trading agent:** Often judged by reward curve only — verify behavior (bid curves, acceptance rate, PnL vs naive baseline)
- [ ] **Data pipeline:** Often assumes data is clean — verify handling of: missing timestamps, DST transitions (23h and 25h days), timezone-naive vs aware datetimes
- [ ] **End-to-end integration:** Often each component works in isolation — verify one complete run: Data → Forecast → Simulation → Agent Decision → PnL Calculation
- [ ] **ASSUME configuration:** Often copied from example without modification — verify `forecast_algorithms` match your data, `learning_config` tuned for your scenario, `train_freq` adjusted for simulation length (ASSUME docs: "if simulation length is not a multiple of train_freq, train_freq is adjusted dynamically")

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Look-ahead bias (Pitfall 1) | HIGH | 1. Audit all preprocessing for temporal leakage 2. Re-split data using TimeSeriesSplit 3. Re-fit all scalers on training period only 4. Retrain all models 5. Discard all previous evaluation results |
| Wrong metrics (Pitfall 2) | MEDIUM | 1. Add spike-specific metrics to evaluation 2. Re-evaluate existing models with new metrics 3. Model that "looked good" may now look terrible — that's correct 4. Retrain if model architecture can't capture spikes |
| RL reward collapse (Pitfall 3) | HIGH | 1. Revert to known-good baseline (naive/heuristic strategy) 2. Inspect reward components separately (profit, costs, regret) 3. Simplify reward: start with pure profit, add penalties gradually 4. Reduce number of learning agents (easier environment) 5. Follow ASSUME docs: "early stopping with a very large number of episodes" |
| No end-to-end (Pitfall 5) | MEDIUM | 1. Stop model optimization immediately 2. Build minimal integration with current (even bad) model 3. Run full loop, measure end-to-end PnL 4. Now optimize pieces with integration feedback |
| Unrealistic market (Pitfall 4) | MEDIUM | 1. Add one realism feature at a time (congestion, then dual market, then ancillary) 2. Retest strategy after each addition 3. Strategy that survived simplification may fail — redesign |
| Pipeline coupling (Pitfall 10) | LOW | 1. Define ForecastProvider interface 2. Wrap existing model in interface 3. Swap implementations as needed |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Look-ahead bias (P1) | Phase 1 (PRED-01) | TimeSeriesSplit in train script; scaler fit on train only |
| Spikes as signal (P2) | Phase 1 (PRED-01) | Spike MAE + sMAPE in evaluation; no outlier clipping |
| RL reward design (P3) | Phase 3 (AGENT-01/02) | Behavior plot (not just reward); PnL vs naive baseline |
| Unrealistic market (P4) | Phase 2 (SIM-01) | Prices correlate with real data (r > 0.6); negative prices appear |
| No end-to-end (P5) | Phase 1 (overall) | Full pipeline runs in Week 1 with naive model |
| Dual settlement (P6) | Phase 2 (SIM-01) | Model includes intraday/balancing market concept |
| Feature leakage (P7) | Phase 1 (PRED-01) | Feature selection inside cross-validation fold |
| Survivorship bias (P8) | Phase 3 (AGENT-02) | Backtest includes crisis periods (2022, 2021) |
| Merit order ignorance (P9) | Phase 2 (SIM-01) | Merit order plot in Grafana shows realistic steps |
| Pipeline coupling (P10) | Phase 3 (AGENT-01) | Forecast interface is swappable; perfect foresight test works |
| XGBoost without temporal awareness | Phase 1 (PRED-01) | Lag features only; no future-leaking features |
| ASSUME config misuse | Phase 2 (SIM-01) | Run example_01a first; modify incrementally |

## ASSUME-Specific Gotchas (from official docs and release notes)

These come directly from the ASSUME framework's own documentation and bug fix history:

1. **Seed setting:** ASSUME docs: "We advise to not use the setting of a seed in the general config (`seed=null`) when using learning, as it will decrease performance." Deterministic mode hurts RL training.

2. **Output clamping bug (fixed v0.5.5):** "The action clamping was changed... Previously, the output range was incorrectly assumed based only on the input, which failed when weights were negative due to Xavier initialization." Lesson: verify agent action ranges are actually being respected.

3. **Buffer/update ordering (fixed v0.6.1):** "Fixed the order of buffer writing and policy updating... This bug will have compromised learning with very heterogeneous units." Lesson: in multi-agent RL, the order of operations matters critically.

4. **train_freq mismatch:** "Fixed a bug where, if the simulation length was not a multiple of the train_freq, the remaining simulation steps were not used for training." Now ASSUME auto-adjusts. Lesson: verify your time alignment.

5. **Bid shuffling bias (fixed v0.4.0):** "Improved clearing with shuffling of bids, to avoid bias in clearing of units early in order book." Lesson: ordering effects in market clearing can bias results.

6. **Continue learning limitations:** "This process will fail, when the number of hidden layers differs between the loaded critic and the new critic." Lesson: plan your agent architecture before starting multi-stage training.

7. **PyTorch reproducibility warning:** "Completely reproducible results are not guaranteed across different PyTorch versions, hardware, or CUDA configurations." Lesson: don't expect bit-exact reproducibility in RL experiments.

8. **Complex clearing paradoxically accepted bids:** The complex clearing algorithm iteratively resolves paradoxically accepted bids (PABs) — bids accepted at a price below their bid price. Lesson: clearing algorithms have corner cases; verify your clearing results.

9. **DMAS bidding strategies are optional:** Pyomo is not a required dependency; optimization-based strategies need it. Lesson: check dependencies before using advanced strategies.

## Sources

- **ASSUME Official Documentation** — https://assume.readthedocs.io/en/latest/
  - [Bidding Strategies](https://assume.readthedocs.io/en/latest/bidding_strategies.html) — Strategy types, naive/heuristic/learning/optimization
  - [Market Mechanisms](https://assume.readthedocs.io/en/latest/market_mechanism.html) — Pay-as-clear, pay-as-bid, complex clearing, nodal, redispatch
  - [Reinforcement Learning](https://assume.readthedocs.io/en/latest/learning.html) — Multi-agent MATD3, centralized critic, reward interpretation warnings
  - [RL Algorithms](https://assume.readthedocs.io/en/latest/learning_algorithm.html) — TD3, buffer design, config parameters
  - [Unit Forecasts](https://assume.readthedocs.io/en/latest/unit_forecasts.html) — Forecast lifecycle, algorithm resolution, registries
  - [Release Notes](https://assume.readthedocs.io/en/latest/release_notes.html) — Bug fixes and lessons learned across v0.1.0–v0.6.1
- **ASSUME JOSS Paper** — Harder et al. (2025), "ASSUME: An agent-based simulation framework for exploring electricity market dynamics with reinforcement learning," *SoftwareX*, Vol. 30, Article 102176.
- **ASSUME Energy and AI Paper** — Harder, Qussous & Weidlich (2023), "Fit for purpose: Modeling wholesale electricity markets realistically with multi-agent deep reinforcement learning," *Energy and AI*, Vol. 14, 100295.
- **epftoolbox** — Lago et al. (2021), "Forecasting day-ahead electricity prices: A review of state-of-the-art algorithms, best practices and an open-access benchmark," *Applied Energy*, Vol. 293, 116983. https://github.com/jeslago/epftoolbox
- **OpenSTEF GitHub** — https://github.com/OpenSTEF/openstef — Automated ML pipeline for short-term energy forecasting, LF Energy project
- **PUDL** — https://github.com/catalyst-cooperative/pudl — Public Utility Data Liberation, cleaned US EIA power data

---

*Pitfalls research for: AI-driven electricity trading learning platform*
*Researched: 2026-05-20*
*Confidence: HIGH — based on official framework documentation and published research*
