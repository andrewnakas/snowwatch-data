# Schema: reanalysis.zarr

Target store for `specs/reanalysis.yaml` — analysis-grade profiles over
stations for the historical training window. No model/init/lead axes: this is
the best estimate of what the atmosphere *did*, used to fit the physical SLR
model. Priority: optional (v2).

```
reanalysis.zarr/
  dims:
    time:    K       datetime64[ns], UTC, 6-hourly
    station: ~912    str (triplet)
    level:   6       int16 hPa [1000,925,850,700,600,500]

  coords:
    time/station/level ; lat/lon (station) float32

  data_vars (float32, NaN fill):
    temperature        (time, station, level)  degC
    relative_humidity  (time, station, level)  percent
    geopotential       (time, station, level)  m
    u_wind/v_wind      (time, station, level)  m/s   (optional)
  surface:
    t2m   (time, station)  degC
    d2m   (time, station)  degC   # 2m dewpoint
    tp    (time, station)  mm     # total precip
```

## Chunking
`time:240 (~60 days @6h), station:1, level:6` — one station-season per tile.

## Notes
- Source: ARCO-ERA5 (gs://gcp-public-data-arco-era5) point-extracted, or any
  ERA5 pressure-level Zarr mirror.
- Pair with snotel_obs to build the SLR training set: observed SLR (ΔSNWD /
  ΔSWE on clean event days) vs the reanalysis column → a physical SLR model
  with no forecast error in the inputs.
