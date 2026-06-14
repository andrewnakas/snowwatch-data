# Schema: nwp_ensemble.zarr

Target store for `specs/nwp_ensemble.yaml`. Two acceptable forms — pick one.

## Form A — raw members (preferred for archives; lets SnowWatch re-reduce)
```
dims: model, init_time, lead_days, station, member
data_vars (float32, NaN fill):
  snowfall      (model, init_time, lead_days, station, member)  cm
  precipitation (model, init_time, lead_days, station, member)  mm
chunk: model:1, init_time:120, lead_days:7, station:1, member:full
```

## Form B — pre-reduced spread (smaller; fine for the operational build)
```
dims: model, init_time, lead_days, station
data_vars (float32):
  snow_mean, snow_std, snow_p10, snow_p50, snow_p90, snow_prob_pos   cm / —
  precip_mean, precip_std                                            mm
chunk: model:1, init_time:180, lead_days:7, station:1
```

## Notes
- GEFS member *history* comes from dynamical.org / noaa-gefs-pds, not the
  Open-Meteo ensemble API (which is recent-only). Use Form A there.
- `prob_pos` = fraction of members with snowfall > 0; the calibrated
  event-probability feature the deterministic models can't provide.
