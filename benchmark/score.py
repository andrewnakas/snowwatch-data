#!/usr/bin/env python3
"""SnowBench scorer — offline, deterministic, no network.

    python score.py submission.csv.gz --window W2025-26core

Submission columns (headered CSV, gzip ok):
  triplet, issue_date, lead_days, valid_date, snowfall_in
  [, q05 q10 ... q95]  [, p1 p2 p6 p12]

Scores against the pinned truth snapshot for the window, prints the
scorecard, and writes <submission>.score.json for the leaderboard PR.
Multiple issue_dates may cover the same valid day at different leads —
every (station, valid_date, lead) cell scores independently, exactly like
the baselines.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verification as V  # noqa: E402  (vendored from snowwatch)

WINDOWS = {
    "W2025-26core": {"truth": "truth_T1_W2025-26core.csv.gz",
                     "start": "2025-12-01", "end": "2026-02-28"},
}
THRESHOLDS = (1.0, 2.0, 6.0, 12.0)
MIN_COVERAGE = 0.5   # fraction of truth station-days that must be forecast


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("submission", type=Path)
    ap.add_argument("--window", default="W2025-26core", choices=sorted(WINDOWS))
    ap.add_argument("--min-coverage", type=float, default=MIN_COVERAGE,
                    help="coverage gate; leaderboard entries require the "
                         "default — lower it only for partial baselines "
                         "(the score JSON records the actual coverage)")
    args = ap.parse_args()

    w = WINDOWS[args.window]
    truth = pd.read_csv(HERE / w["truth"])
    sub = pd.read_csv(args.submission)
    need = {"triplet", "issue_date", "lead_days", "valid_date", "snowfall_in"}
    missing = need - set(sub.columns)
    if missing:
        print(f"submission missing columns: {sorted(missing)}")
        return 1
    sub = sub[(sub["valid_date"] >= w["start"]) & (sub["valid_date"] <= w["end"])]
    sub["lead_days"] = pd.to_numeric(sub["lead_days"], errors="coerce")
    sub = sub[sub["lead_days"].between(1, 7)]
    # Honesty check: valid = issue + lead, exactly.
    implied = (pd.to_datetime(sub["issue_date"])
               + pd.to_timedelta(sub["lead_days"], unit="D")).dt.strftime("%Y-%m-%d")
    bad = (implied != sub["valid_date"]).sum()
    if bad:
        print(f"REJECTED: {bad} rows where valid_date != issue_date + lead_days")
        return 1

    df = sub.merge(truth, on=["triplet", "valid_date"], how="inner",
                   suffixes=("", "_obs"))
    df = df.rename(columns={"snowfall_in_obs": "obs_snowfall_in"})
    truth_cells = len(truth) * 7
    coverage = len(df) / truth_cells
    print(f"{len(df)} scored cells, coverage {coverage:.1%} of "
          f"{truth_cells} (station-day × lead)")
    if coverage < args.min_coverage:
        print(f"REJECTED: coverage below {args.min_coverage:.0%}")
        return 1

    out: dict = {"window": args.window, "n": len(df),
                 "coverage": round(coverage, 4),
                 "n_stations": int(df["triplet"].nunique())}
    out.update(V.summarize_deterministic(df, obs_col="obs_snowfall_in",
                                         pred_col="snowfall_in"))
    out["by_lead"] = {int(l): V.mae_bias(g["obs_snowfall_in"], g["snowfall_in"])
                      for l, g in df.groupby("lead_days")}

    qcols = sorted((c for c in df.columns if re.fullmatch(r"q\d{2}", c)),
                   key=lambda c: int(c[1:]))
    if qcols:
        out["crps"] = V.crps_from_quantiles(
            df["obs_snowfall_in"].to_numpy(), df[qcols].to_numpy(),
            [int(c[1:]) / 100 for c in qcols])
    for thr in THRESHOLDS:
        col = f"p{thr:g}"
        if col in df.columns:
            bs = V.brier_skill(df["obs_snowfall_in"], df[col], threshold_in=thr)
            bs["reliability"] = V.reliability_curve(
                df["obs_snowfall_in"], df[col], threshold_in=thr)
            out[f"prob_{thr:g}in"] = bs

    print(json.dumps({k: v for k, v in out.items()
                      if not isinstance(v, dict)}, indent=2, default=float))
    score_path = args.submission.with_suffix("").with_suffix(".score.json")
    score_path.write_text(json.dumps(out, indent=2, default=float))
    print(f"wrote {score_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
