# pypemesh-core

The open-source pipe stress analysis engine behind [pypemesh](../README.md).

Pure Python library, `pip install pypemesh-core`. Can be used standalone
(CLI or Python API) or embedded in the web/desktop UIs.

## Install (dev)

```bash
cd pypemesh-core
pip install -e ".[dev]"
pytest
```

## Layout

- `solver/` — FEA beam solver (static, non-linear, dynamic)
- `codes/` — pluggable code-compliance checks (B31.3 ships in v0.1)
- `materials/` — temperature-dependent material database
- `fittings/` — ASME B16.9, B16.5, B36.10 component catalogs
- `io/` — project JSON, PCF, PDF report
- `validation/` — benchmark harness

See `../docs/ARCHITECTURE.md` for the full picture.
