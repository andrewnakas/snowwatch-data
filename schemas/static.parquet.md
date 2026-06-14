# Schema: static.parquet

Target store for `specs/static.yaml` — one row per station (or per
station×model for the grid-elevation columns). Parquet, not Zarr: it's small
and tabular.

```
columns:
  station_id        str
  triplet           str        e.g. "1344:CO:SNTL"
  name              str
  state             str
  lat               float64
  lon               float64
  elevation_m       float64    station elevation
  grid_elev_m_nbm   float64    model grid-cell elevation at extraction point
  grid_elev_m_hrrr  float64
  grid_elev_m_gfs   float64
  djf_tavg_c        float64    (optional, derivable downstream)
  djf_precip_mm     float64    (optional)
  median_slr        float64    (optional)
  snow_class        str        (optional) maritime|intermountain|continental
```

## The key feature
`elevation_m - grid_elev_m_<model>` is the elevation correction term. In
complex terrain the NWP grid cell can sit hundreds of meters off the real
station; this difference explains a large, *systematic* temp/precip/phase
bias the post-processor can learn out. Without it, point extraction silently
injects terrain error into every forecast.
