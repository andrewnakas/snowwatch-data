# snowwatch-data

**Data specification for the SnowWatch snow-depth forecasting system.**

This repo is a *contract*, not a pipeline. It defines exactly which weather
and observation datasets SnowWatch needs, at what resolution and history, and
the target Zarr/Parquet layout each should land in. A reformatter (e.g. an
`open-claw`-style fetch+rechunk agent) reads `specs/*.yaml` and produces the
stores described in `schemas/`.

SnowWatch itself (the forecasting code) lives in the separate `snowwatch`
repo and *consumes* these stores. Keeping the data contract here means the
fetch/reformat work is reproducible, idempotent, and decoupled from model code.

## Why this exists

The accuracy of point snow forecasting is bottlenecked by two things the raw
NWP models don't give you directly:

1. **Snow-to-liquid ratio (SLR)** and **precip phase** — set by the vertical
   temperature + humidity structure of the atmosphere, not surface values.
   This is why the spec demands **pressure-level** temperature *and relative
   humidity* (for wet-bulb and dendritic-growth-zone diagnostics), not just
   2 m fields.
2. **Long, clean archives of past forecasts** aligned to QC'd station
   observations — the training pairs for the post-processor. Per-station API
   pulls don't scale to ~900 stations × 5 models × multi-year history;
   analysis-ready Zarr does.

## What to fetch (see `specs/` for the authoritative, machine-readable form)

| Dataset | Role | Format |
|---|---|---|
| `specs/nwp_surface.yaml` | Daily surface forecasts (snowfall/QPF/temp) per model | Zarr `(model, init_time, lead, station)` |
| `specs/nwp_profiles.yaml` | **Pressure-level temp + RH + wind + geopotential** | Zarr `(model, init_time, lead, station, level)` |
| `specs/nwp_ensemble.yaml` | GEFS / AIFS-ENS member snowfall/precip (spread) | Zarr `(model, init_time, lead, station, member)` |
| `specs/snotel_obs.yaml` | NRCS SNOTEL daily + hourly SNWD/WTEQ/PRCP/TAVG | Zarr `(station, time)` |
| `specs/reanalysis.yaml` | ERA5-Land / reanalysis profiles for the training period | Zarr `(time, station, level)` |
| `specs/static.yaml` | Station metadata + terrain (grid-vs-station elevation) | Parquet |

All forecast stores are **point-extracted at SNOTEL station coordinates**
(see `specs/stations.csv`), not full grids — SnowWatch is a point system and
this keeps the stores tiny relative to the source archives.

## Sources

- **Open-Meteo Forecast / Ensemble / Previous-Runs APIs** — the current
  SnowWatch fetch path; simplest to reproduce, terrain-downscaled to the
  station point.
- **dynamical.org reformatters** (Source Cooperative) — analysis-ready Zarr
  for GEFS / HRRR / GFS; use these for bulk model history instead of the API
  where available (no rate limits, reproducible). Gives the model *grid
  point*, so pair with `static.yaml` terrain features.
- **NOAA Open Data on AWS** — `noaa-nbm-grib2-pds`, `noaa-hrrr-bdp-pds`,
  `noaa-gefs-pds` (raw GRIB2; reformat as needed for models with no public
  Zarr, notably NBM).
- **NRCS AWDB** — SNOTEL observations (`https://wcc-awdb.example` REST).

## Layout

```
specs/        one YAML per dataset: source, variables, dims, history, target store
schemas/      the resulting Zarr/Parquet schema (dims, coords, dtypes, chunks)
scripts/      validate_specs.py — sanity-check specs against schemas
stations.csv  the station list to point-extract at (id, triplet, lat, lon, elev)
```

See `specs/_conventions.md` for units, time conventions (UTC, water year),
and the lead/init-time grid definition shared by every forecast spec.
