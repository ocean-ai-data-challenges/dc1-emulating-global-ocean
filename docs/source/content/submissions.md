# Submitting a model

This page describes the complete procedure for formatting a surface emulation, validating it
locally, and submitting results to DC1.

---

## 1. Prerequisites and installation

Clone the repository and install the package in *editable* mode:

```bash
git clone https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean.git
cd dc1-emulating-global-ocean
pip install -e .
```

The installation provides the `dc-submit` CLI command (also callable via
`python -m dc.submit`).

---

## 2. Required submission format

### 2.1 DC1 grid

Every emulation must be provided on the DC1 global **surface** grid:

| Dimension | Values | No. of points |
|---|---|---|
| `lat` | −78 to +90°, step 0.25° | 672 |
| `lon` | −180 to +180°, step 0.25° | 1 440 |
| `lead_time` | 0, 1, 2, …, 9 (days after initialisation) | 10 |

> **No depth dimension is required.** DC1 is a surface-only challenge. If your dataset
> includes a `depth` axis, the pipeline will automatically extract the surface level
> (~0.49 m). However, providing flat 2-D fields `(time, lat, lon)` is preferred.

### 2.2 Required variables

All five variables are **2-D surface fields** with shape `(time, lat, lon)`:

| Variable | Dimensions | Shape | Unit | Description |
|---|---|---|---|---|
| `zos` | `(time, lat, lon)` | (10, 672, 1 440) | m | Sea surface height |
| `thetao` | `(time, lat, lon)` | (10, 672, 1 440) | °C | Sea surface temperature |
| `so` | `(time, lat, lon)` | (10, 672, 1 440) | PSU | Sea surface salinity |
| `uo` | `(time, lat, lon)` | (10, 672, 1 440) | m s⁻¹ | Surface zonal current |
| `vo` | `(time, lat, lon)` | (10, 672, 1 440) | m s⁻¹ | Surface meridional current |

> The `time` dimension encodes **valid dates** (initialisation date + lead-time), not indices.
> CF metadata (`units`, `long_name`) are mandatory for each coordinate.

> **Key difference with DC2**: in DC2, 3-D variables (`thetao`, `so`, `uo`, `vo`) have shape
> `(time, depth, lat, lon)` with 21 depth levels. In DC1, all variables are 2-D surface
> fields — no depth dimension.

### 2.3 Accepted variable names (aliases)

The validation pipeline accepts common aliases:

| Coordinate | Accepted names |
|---|---|
| latitude | `lat`, `latitude` |
| longitude | `lon`, `longitude` |
| depth | `depth`, `lev` |
| time | `time` |
| SSH | `zos`, `ssh`, `ssha` |
| Temperature | `thetao`, `temperature` |
| Salinity | `so`, `salinity` |
| Zonal current | `uo`, `u` |
| Meridional current | `vo`, `v` |

---

## 3. Accepted file formats

The `dc-submit info` command lists supported formats. Four layouts are recognised:

| Layout | Description | Example |
|---|---|---|
| **A** — directory of Zarr stores per date | *Recommended.* One `.zarr` per initialisation date in a directory | `model/2024-01-03.zarr`, `model/2024-01-10.zarr`, … |
| **B** — single Zarr store | A single Zarr store covering the entire period | `model/all_emulations.zarr` |
| **C** — single NetCDF file | A single `.nc` or `.nc4` file | `model/emulations.nc` |
| **D** — glob of NetCDF files | Any path accepted by `glob` | `/data/model/*.nc` |

Layout A is recommended for large submissions as it enables lazy loading via Dask and
better fault tolerance.

### Layout A structure (directory of Zarr stores per date)

```
my_model/
    2024-01-03.zarr
    2024-01-10.zarr
    2024-01-17.zarr
    ...
    2024-12-25.zarr
```

---

## 4. Validating the submission

Before running the full evaluation, verify locally that the format is correct:

```bash
dc-submit validate <data_path> --model-name <MODEL_NAME> [options]
```

### Validation options

| Option | Description |
|---|---|
| `--model-name NAME` | Model identifier *(required)* |
| `--quick` | Validate only the first few dates (quick test) |
| `--save-report PATH` | Save the validation report to a JSON file |
| `--max-nan-fraction F` | Maximum allowed NaN fraction (default: `0.10`, i.e. 10%) |
| `--variables V [V …]` | Restrict validation to specific variables |
| `--config {dc1,…}` | Configuration profile (default: `dc1`) |

### What the validation checks

1. **Variable presence**: `zos`, `thetao`, `so`, `uo`, `vo` (or a subset if `--variables`
   is specified).
2. **Grid conformity**: lat and lon match the DC1 specification (no depth check required).
3. **NaN fraction**: no variable exceeds `max_nan_fraction` (10% by default).
4. **Temporal coverage**: the expected initialisation dates are present.
5. **Types and units**: arrays are floating-point and CF units are provided.

---

## 5. Running the full evaluation

```bash
dc-submit run <data_path> --model-name <MODEL_NAME> [options]
```

### Execution options

| Option | Description |
|---|---|
| `-d DIR`, `--data-directory DIR` | Output directory for results and catalogues |
| `--force` | Overwrite existing results without confirmation |
| `--skip-validation` | Skip initial validation (not recommended) |
| `--quick-validation` | Run a quick validation before evaluation |
| `--description TEXT` | Short model description |
| `--team TEXT` | Team name |
| `--email TEXT` | Contact email |
| `--url TEXT` | Model URL (paper, code, …) |

### Pipeline steps

1. **Catalogue download**: observation catalogues (SARAL, Jason-3, SWOT, Argo, GLORYS12)
   are downloaded from the DC1 Wasabi S3 bucket.
2. **Surface extraction**: the `standardize_to_surface` transform is automatically applied,
   extracting the surface level from any 3-D data.
3. **Interpolation**: emulated surface fields are spatially and temporally interpolated to
   the positions of each reference dataset (`pyinterp`, bilinear, ±12 h window).
4. **Metric computation**: RMSD and geostrophic current RMSD (see [metrics](metrics.md)).
5. **Output**: results are written to `<data_directory>/results/results_<NAME>.json`.
6. **Leaderboard**: leaderboard HTML pages are rebuilt in `<data_directory>/leaderboard/`.

---

## 6. Inspecting the specification

The `dc-submit info` subcommand displays the full configuration (grid, variables, metrics,
accepted formats) without running any evaluation:

```bash
dc-submit info --config dc1
```

---

## 7. Participating in the public leaderboard

To appear on the official leaderboard, contact the DC1 organisers providing:

- the `results_<NAME>.json` file generated by `dc-submit run`;
- a brief description of the model and training data used;
- a reference (paper, preprint, GitHub repository).

> **Note**: the `dctools.submission` module (remote submission backend) is under development.
> The current procedure involves running `dc-submit run` locally and manually sending the
> results to the organisers. Open a
> [GitHub issue](https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean/issues)
> for any questions about submission.

See also [`dc1/submit.py`](https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean/blob/main/dc1/submit.py)
for the complete CLI interface code.
