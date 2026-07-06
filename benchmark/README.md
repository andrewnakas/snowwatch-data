# SnowBench — a point snowfall forecast benchmark for mountain snow stations

**Predict 24h snowfall (inches) at SNOTEL stations, 1–7 days ahead. Beat the
National Blend of Models. Prove it with paired bootstrap CIs.**

There is no public leaderboard for point snowfall forecasts at snow stations —
published verification scatters across NOHRSC-grid studies, airport METAR
studies, and manual-observer SLR studies, none of them reproducible against a
frozen dataset. SnowBench is that frozen target: a fixed station list, fixed
evaluation windows, pinned truth data, reference metric implementations, and
baseline scores with uncertainty. If your system beats the table below under
the protocol, open a PR — the leaderboard accepts submissions.

## The task

For each (station, issue_date, lead ∈ 1..7) produce:

1. **Point forecast** — expected 24h snowfall (inches) for the UTC valid day
   `issue_date + lead`.
2. *(Optional, for probabilistic scores)* quantiles (any levels) and/or
   exceedance probabilities P(snowfall ≥ 1/2/6/12 in).

Forecasts must use only information available at 00Z on the issue date
(NWP runs initialized ≤ 00Z, observations through the prior day). Anything
that peeks — reanalysis at valid time, later NWP cycles, the observations
themselves — disqualifies the submission. This is the same rule the
operational baselines live under.

## Truth

- **T1 (primary): SNOTEL QC'd 24h snowfall** — positive daily snow-depth
  change from the ultrasonic sensor, cross-checked against the snow pillow
  and precip gauge, with despiking, stuck-sensor and wind-drift rules.
  Reference implementation: [`app/targets.py`] in the snowwatch repo;
  pinned per-window snapshots (CSV) ship as release assets here.
- **T2 (comparability): NOHRSC observer reports** — human-measured 24h
  snowfall from COOP/CoCoRaHS/spotter networks at co-located and nearby
  points, as compiled by the National Snowfall Analysis. Scores against T2
  make results comparable with the gridded-verification literature; the
  T1-vs-T2 agreement table is published rather than hidden.

## Stations and windows

- **Stations:** the frozen list in [`stations_benchmark.csv`](stations_benchmark.csv)
  (SNOTEL triplets + coordinates + elevation + snow climate class).
  CONUS subset is the NBM head-to-head set; Alaska is reported separately.
- **Evaluation windows** (frozen; one row of the leaderboard each):
  - `W2025-26core`: 2025-12-01 → 2026-02-28
  - `W2026-27core`: 2026-12-01 → 2027-02-28 *(opens when the winter closes)*
  - Training data: anything strictly before the window start.

## Metrics (reference implementation: `app/verification.py`, vendored here)

| Family | Metrics |
|---|---|
| Deterministic | MAE, bias, RMSE; event-conditional MAE (obs ≥ 1") |
| Events | CSI / POD / FAR / frequency bias at 1", 2", 6", 12" |
| Probabilistic | CRPS (quantile pinball), CRPSS vs station-month climatology; Brier + BSS + reliability at each threshold |
| Significance | paired station-week block bootstrap (95% CI) vs the NBM baseline — storms correlate errors within a station-week, naive CIs are too tight |

A submission "beats the baseline" at a metric only when the bootstrap CI of
the difference excludes zero. Frequency bias must stay in [0.8, 1.3] at each
threshold for event-stat wins to count (no CSI-by-spam).

## Baselines (W2025-26core, SNOTEL truth, CONUS)

| System | MAE | CSI@1" | CSI@6" | CSI@12" | CRPSS |
|---|---|---|---|---|---|
| Climatology (station-month) | — | — | — | — | 0.000 |
| NBM v4.3 (raw, at-point) | 0.991 | 0.370 | 0.237 | 0.175 | — |
| NBM (thresholds CSI-tuned) | 0.991 | 0.364 | 0.233 | 0.141 | — |
| Multi-model mean (NBM/HRRR/GFS) | 0.737 | 0.313 | 0.203 | 0.151 | — |
| **SnowWatch v1.6** | **0.714** | 0.345 | 0.197 | 0.125 | **0.238** |

*(98-station subset pending the full-catalogue retrain; the table re-freezes
with the 912-station run. SnowWatch's own outstanding gaps at 6"/12" are
listed — a benchmark that hides its author's losses isn't a benchmark.)*

## How to submit

1. Produce `submission.csv.gz`: `triplet, issue_date, lead_days, valid_date,
   snowfall_in[, q05..q95, p1, p2, p6, p12]` covering ≥ 90% of the
   (station, day, lead) cells of a frozen window.
2. Run `python score.py submission.csv.gz --window W2025-26core` (vendored
   metrics + pinned truth; no network).
3. Open a PR adding your row to `leaderboard.md` with the score JSON and a
   one-paragraph method description. Reproducibility material (code link,
   model card) strongly encouraged; "available at issue time" attestation
   required.

## Provenance & citation

Built by the SnowWatch project. Verification-honesty notes, negative
results, and the pre-registered win conditions live in
[`snowwatch/benchmarks/published.json`]. Published-literature context:
Veals et al. 2025 (WaF, SLR prediction), Scheuerer & Hamill 2019 (MWR,
NOHRSC-truth probabilistic snowfall), Uden et al. 2023 (WaF, NBM event
verification).
