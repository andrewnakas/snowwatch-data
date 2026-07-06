# SnowBench leaderboard

Window `W2025-26core` (2025-12-01 → 2026-02-28), truth T1 (SNOTEL QC).
Coverage = fraction of the 504,924 (station-day × lead) cells forecast.
Event-stat wins count only with frequency bias ∈ [0.8, 1.3] and a
station-week bootstrap CI excluding zero (see README).

| Rank | System | Coverage | MAE | CSI@1" | CSI@6" | CSI@12" | CRPS | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | SnowWatch v1.6 (postproc) | 8.4%* | 0.714 | 0.345 | 0.197 | 0.125 | 0.432 | LightGBM hurdle + calibrated multi-threshold cascade; [method](https://github.com/andrewnakas/snowwatch) |
| 2 | NBM v4.3 (raw, at-point) | 8.4%* | 0.991 | 0.370 | 0.237 | 0.175 | — | operational baseline; overforecasts (bias +0.43, FB@12" 1.69) |
| — | Multi-model mean | 8.4%* | 0.737 | 0.313 | 0.203 | 0.151 | — | NBM/HRRR/GFS consensus |

\* NBM Previous-Runs coverage at freeze time (74 CONUS stations). The
full-catalogue re-freeze (912 stations) replaces these rows when the NBM
backfill completes — coverage gate for new submissions stays at 50%.

**Honesty note:** SnowWatch currently *loses* CSI at 1/6/12" to raw NBM on
this window and wins MAE/bias/CRPS decisively (ΔMAE −0.247 [−0.284, −0.213],
P=1.00). Rank order weighs MAE first pending a community-agreed composite;
argue about the ranking in an issue — that's what benchmarks are for.

## Submitting

See [README](README.md#how-to-submit). PRs must include the `score.json`
produced by `score.py` at default coverage, a method paragraph, and an
at-issue-time data attestation.
