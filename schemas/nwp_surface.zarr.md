# Schema: nwp_surface.zarr

Target store for `specs/nwp_surface.yaml` — daily surface forecasts.

```
nwp_surface.zarr/
  dims:
    model:     5      (nbm, hrrr, gfs, ifs, aifs)
    init_time: N      datetime64[ns], UTC, 6-hourly
    lead_days: 7      int8, 1..7
    station:   ~912   str (triplet)

  coords:
    model/init_time/lead_days/station  as in nwp_profiles
    valid_date (model?, init_time, lead_days)  datetime64[ns]  # = init + lead
    lat (station) / lon (station) float32

  data_vars (float32, NaN fill):
    snowfall                   (model, init_time, lead_days, station)  cm
    precipitation              (model, init_time, lead_days, station)  mm
    temperature_2m_mean        (model, init_time, lead_days, station)  degC
    temperature_2m_max         (model, init_time, lead_days, station)  degC
    temperature_2m_min         (model, init_time, lead_days, station)  degC
    precipitation_probability  (model, init_time, lead_days, station)  percent  (optional)
```

## Chunking
```
model:1, init_time:180 (~45 days @6h), lead_days:7, station:1
```
One station's full lead×variable record for ~1.5 months is a single tile.

## Notes
- NBM/HRRR are CONUS-only: their slices are all-NaN for Alaska stations.
  Keep the station; do not drop. (A model trained where its key feature is
  NaN is the failure SnowWatch hit at 24-station scale.)
- `snowfall` NaN (missing) != 0 (forecast no snow). Preserve the distinction.
