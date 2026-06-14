#!/usr/bin/env python3
"""Validate specs/*.yaml against repo conventions before a reformatter runs.

Catches the cheap mistakes (missing target schema, unknown units, no station
file, profile spec without relative_humidity) so the expensive fetch job
doesn't discover them after burning an API budget.

Usage: python scripts/validate_specs.py
Exit 0 = all good, 1 = problems (printed).
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml required: pip install pyyaml")
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "specs"

KNOWN_UNITS = {
    "cm", "mm", "degC", "degF_native", "in_native", "percent", "m_s", "m", "hPa",
}
REQUIRED_KEYS = {"id", "role"}


def _walk_units(obj, found: set):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "units" and isinstance(v, str):
                found.add(v)
            else:
                _walk_units(v, found)
    elif isinstance(obj, list):
        for v in obj:
            _walk_units(v, found)


def main() -> int:
    errors: list[str] = []
    specs = sorted(p for p in SPECS.glob("*.yaml"))
    if not specs:
        print("no specs found")
        return 1

    stations = ROOT / "stations.csv"
    if not stations.exists():
        errors.append("stations.csv missing — forecast specs point-extract at it")

    for sp in specs:
        try:
            doc = yaml.safe_load(sp.read_text())
        except Exception as exc:
            errors.append(f"{sp.name}: YAML parse error: {exc}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{sp.name}: top level is not a mapping")
            continue

        for key in REQUIRED_KEYS:
            if key not in doc:
                errors.append(f"{sp.name}: missing required key '{key}'")

        # target store schema must exist (Parquet specs allowed too)
        tgt = doc.get("target_store")
        if tgt and not (ROOT / tgt).exists():
            errors.append(f"{sp.name}: target_store '{tgt}' has no schema file")

        # units sanity
        found_units: set = set()
        _walk_units(doc, found_units)
        for u in found_units - KNOWN_UNITS:
            errors.append(f"{sp.name}: unknown unit '{u}' (add to _conventions.md / validator)")

        # the whole point of the profiles spec
        if doc.get("id") == "nwp_profiles":
            vars_ = doc.get("variables") or {}
            if "relative_humidity" not in vars_:
                errors.append(f"{sp.name}: profiles spec must include relative_humidity "
                              "(required for wet-bulb + dendritic-zone SLR)")
            levels = set(doc.get("required_levels_hpa") or [])
            if not {1000, 500} <= levels:
                errors.append(f"{sp.name}: required_levels_hpa must include 1000 and 500 "
                              "(1000-500 thickness)")

    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK — {len(specs)} specs valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
