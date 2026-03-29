# Evaluation

This page describes the evaluation pipeline in detail: what it does, how to configure it,
and how to interpret the results.

---

## Running the evaluation

### Via the submit CLI (recommended)

```bash
python dc1/submit.py run <data_path> --model-name <MODEL_NAME> [options]
```

This wraps validation, evaluation, and leaderboard generation in a single command.

### Via evaluate.py directly

```bash
python dc1/evaluate.py --model-name <MODEL_NAME>
```

---

## Execution options

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

---

## Pipeline steps

The evaluation proceeds through the following stages:

### 1. Catalogue download

Observation catalogues (SARAL, Jason-3, SWOT, Argo, GLORYS12) are downloaded from the
DC1 Wasabi S3 bucket (`ppr-ocean-climat`). These catalogues specify the space-time positions
of all observations used for scoring.

### 2. Surface extraction

The `standardize_to_surface` transform is automatically applied. If submitted data includes
a depth axis, only the surface level (~0.49 m) is retained. This ensures all evaluations
are performed on 2-D surface fields regardless of the input format.

### 3. Interpolation

Emulated surface fields are spatially and temporally interpolated to the positions of each
reference dataset using **`pyinterp`** (bilinear interpolation, ±12 h temporal window).

### 4. Metric computation

The following metrics are computed (see {doc}`metrics` for full details):

| Metric | Reference datasets | Variables |
|---|---|---|
| RMSD | SARAL, Jason-3, SWOT, Argo (surface), GLORYS12 (surface) | all |
| Geostrophic current RMSD | GLORYS12 (surface) | `zos` (SSH) |

> **Note:** Unlike DC2, DC1 does **not** compute Mixed Layer Depth RMSD, Lagrangian trajectory
> deviation, or Class 4 depth-resolved metrics. All evaluation is surface-level only.

### 5. Output files

Results are written to the output directory (default `dc1_output/`):

| File | Content |
|---|---|
| `results/results_<NAME>.json` | Aggregated scores per variable and lead time |
| `leaderboard/*.html` | Rebuilt leaderboard HTML pages |

### 6. Leaderboard

Leaderboard HTML pages are automatically rebuilt from the results files. They include
interactive maps showing spatial RMSD distributions at 1° × 1° resolution and summary
tables comparing all submitted models against the GloNet baseline.

---

## Evaluation period and temporal setup

| Parameter | Value |
|---|---|
| Evaluation period | 1 January 2024 – 1 January 2025 |
| Initialisation frequency | Every 7 days (52 emulations) |
| Forecast horizon | 10 days (lead times 0–9) |
| Temporal matching tolerance | ±12 hours |

---

## Interpreting results

The `results_<NAME>.json` file contains scores structured by:

- **Variable** (`zos`, `thetao`, `so`, `uo`, `vo`)
- **Lead time** (0–9 days)
- **Reference dataset** (SARAL, Jason-3, SWOT, Argo, GLORYS12)

Since DC1 is surface-only, there is **no depth decomposition** (unlike DC2 which breaks
down scores by depth level).

Lower RMSD values indicate better performance. A submission improves on the baseline if it
achieves lower scores than GloNet on at least one metric/variable combination.
