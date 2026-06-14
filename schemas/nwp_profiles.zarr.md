# Schema: nwp_profiles.zarr

Target store for `specs/nwp_profiles.yaml` — the pressure-level profiles.

```
nwp_profiles.zarr/
  dims:
    model:     5     (nbm, hrrr, gfs, ifs, aifs)   # whichever provide levels
    init_time: N     datetime64[ns], UTC, 6-hourly
    lead_days: 7     int8, 1..7
    station:   ~912  str (triplet)
    level:     6     int16 hPa [1000,925,850,700,600,500]

  coords:
    model      (model)      <U8
    init_time  (init_time)  datetime64[ns]
    lead_days  (lead_days)  int8
    station    (station)    <U16
    level      (level)      int16
    lat        (station)    float32
    lon        (station)    float32

  data_vars (all float32, NaN fill):
    temperature        (model, init_time, lead_days, station, level)   degC
    relative_humidity  (model, init_time, lead_days, station, level)   percent
    wind_speed         (model, init_time, lead_days, station, level)   m/s
    geopotential_height(model, init_time, lead_days, station, level)   m
```

## Chunking
Chunk so a single (station, all-leads, all-levels, ~1 month of inits) read is
one tile — that is SnowWatch's access pattern at training time.

```
model:1, init_time:120 (~30 days @6h), lead_days:7, station:1, level:6
```

float32 + this chunking keeps per-station-month tiles ~tens of KB; the whole
profiles store for one snow season is ~single-digit GB (storm-gated, so most
(station, init) cells are absent/NaN and compress to nothing).

## Notes
- Storm-gated: only (station, init_time) pairs where a model forecast
  meaningful QPF are populated; the rest are NaN. Zarr + compression makes
  the sparsity free.
- `relative_humidity` is mandatory — without it wet-bulb and dendritic-zone
  saturation can't be computed and the store loses its reason to exist.
