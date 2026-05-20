# Phase 1: Data Foundation + Basic Prediction - Discussion Log

**Gathered:** 2026-05-20
**Mode:** auto

## Areas Auto-Resolved

### Data Source
[auto] Q: "Which electricity market dataset to use?" → Selected: PJM (Recommended) — Largest US RTO, most data available via PUDL, well-documented

### Data Storage Format
[auto] Q: "Parquet vs SQLite for data storage?" → Selected: Parquet (Recommended) — Portable, columnar, pandas-native, no server needed

### Environment Setup
[auto] Q: "pip+venv vs conda vs Docker?" → Selected: pip+venv with requirements.txt (Recommended) — Fastest path to <30min setup target

### Feature Engineering
[auto] Q: "Progressive vs all-at-once features?" → Selected: Progressive — start with 5 core features, add iteratively with before/after comparison

### Notebook Structure
[auto] Q: "Monolithic vs modular notebooks?" → Selected: Modular .py modules + thin notebooks (Recommended) — Prevents the anti-pattern identified in research

### End-to-End Baseline
[auto] Q: "Simple persistence forecast vs ASSUME-lite?" → Selected: Simple persistence + basic P&L (Recommended) — No framework dependency, proves pipeline in <50 lines

## Deferred Ideas

- Chinese electricity data — v2 (EXT-01), custom scraping needed
- Weather data — Phase 2 (OpenSTEF integration)
- HAMLET — repo 404, lower priority
- Real-time data — out of scope

---
*Discussion completed: 2026-05-20 (auto mode)*
