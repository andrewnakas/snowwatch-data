# Conventions shared by every spec

These apply to all `specs/*.yaml`. Each spec may override where noted.

## Time
- **All timestamps UTC.** No local time anywhere in the stores.
- `init_time` (a.k.a. issue/reference time): the model run, e.g. `2025-01-01T00:00Z`.
- `valid_time`: the time a forecast value is for. `valid_time = init_time + lead`.
- `lead_days`: 1..7 (integer). Day N = the 24 h period
  `[init_time + (N-1)*24h, init_time + N*24h)` aggregated/summed as the
  variable dictates (sums for precip/snow, mean/max/min for temperature).
- Daily aggregation is over the **UTC calendar day** for surface fields.
- **Water year**: Oct 1 – Sep 30, labeled by the calendar year it ends in
  (WY2025 = 2024-10-01 .. 2025-09-30). Used for climatology features.

## Units (store these exactly; do not pre-convert to imperial)
- snowfall: **cm**
- precipitation / QPF / SWE: **mm**
- temperature, dewpoint, wet-bulb: **°C**
- relative_humidity: **%**
- wind_speed: **m/s**
- geopotential_height: **m**
- pressure: **hPa**
- elevation: **m** (store station elev in m; SnowWatch converts as needed)

## Pressure levels (profiles)
Standard set, coarse→fine as needed: **1000, 925, 850, 700, 600, 500 hPa**.
Minimum required for SLR/phase physics: 1000, 850, 700, 600, 500.
- 1000 + 500 → 1000–500 thickness (rain/snow line ~5400 m).
- 700/600 → typically span the −12…−18 °C dendritic growth zone.

## Point extraction
- Forecast stores are extracted at the SNOTEL station coordinates in
  `stations.csv` (nearest-grid-point or bilinear; record which in spec).
- Keep the source **grid-cell elevation** alongside the station elevation —
  the difference is a first-class feature (lapse-rate correction). See
  `static.yaml`.

## Missing data
- Use the store's native fill (`NaN` for floats). Do **not** zero-fill —
  zero snowfall and missing snowfall are different and the model must tell
  them apart.
- A model that doesn't cover a station (e.g. NBM/HRRR over Alaska) gets
  all-NaN for that station; don't drop the station.

## History depth (per spec, but defaults)
- Forecast archives: as far back as the source allows; NBM/GFS/HRRR ≈ late
  2024 via Open-Meteo Previous-Runs, deeper via NOAA GRIB / reformatters.
- Observations: full station record (decades where available).

## Idempotency
- Every fetch is chunk-addressable and resumable. A sidecar manifest records
  which (model, init_time-chunk, variable) tiles are complete vs known-empty
  so reruns are no-ops. Never refetch a tile marked complete or empty.
