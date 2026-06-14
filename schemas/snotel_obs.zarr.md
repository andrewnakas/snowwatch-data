# Schema: snotel_obs.zarr

Target store for `specs/snotel_obs.yaml` — the observation truth.

```
snotel_obs.zarr/
  dims:
    station: ~912   str (triplet)
    time:    M      datetime64[ns], UTC, daily (00Z)

  coords:
    station (station) <U16 ; lat/lon/elevation_m (station) float32
    time (time) datetime64[ns]

  data_vars (float32, NaN fill — native units as reported by AWDB):
    snow_depth  (station, time)  in   # SNWD; RAW, despiked downstream
    swe         (station, time)  in   # WTEQ
    precip      (station, time)  in   # PRCPSA
    tavg        (station, time)  degF # TAVG
```

Separate `snotel_obs_hourly.zarr` (same dims, time = hourly) holds SNWD/WTEQ
only, and ONLY for stations flagged for QC rebuild — not the full network.

## Chunking
`station:1, time:full` (one station's whole record per tile) — SnowWatch QCs
per station over the entire history.

## Notes
- This store is intentionally raw. The QC pipeline (despike, stuck-run flags,
  pillow/gauge corroboration, SLR-banded 24h snowfall target) lives in
  snowwatch/app/targets.py and runs on read. Storing QC'd values here would
  freeze one QC version into the data.
