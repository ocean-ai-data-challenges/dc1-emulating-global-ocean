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

## Configuration profiles

The YAML configuration file `dc1/config/dc1_wasabi.yaml` controls all pipeline
behaviour: S3 connection, parallelism, memory safety, and dataset definitions.

### Parallelism presets

Two groups of presets are defined, each with three levels (`low`, `medium`, `high`).
The active level is set via a YAML anchor (`&PARALLEL` or `&PARALLEL_VOLUMINOUS`)
and can be switched by moving the anchor:

```yaml
# Standard datasets (SARAL, Jason-3, Argo, …)
parallelism_presets:
  medium: &PARALLEL                     # ◄ active level
    obs_batch_size: 30
    n_parallel_workers: 6
    nthreads_per_worker: 2
    memory_limit_per_worker: "3GB"
    download_workers: 16

# Heavy datasets (GLORYS gridded, SWOT wide-swath)
voluminous_parallelism_presets:
  medium: &PARALLEL_VOLUMINOUS          # ◄ active level
    obs_batch_size: 24
    n_parallel_workers: 4
    nthreads_per_worker: 2
    memory_limit_per_worker: "4GB"
    download_workers: 4
    gridded_batch_size: 6
```

Each dataset source merges one of these presets via `<<: *PARALLEL` or
`<<: *PARALLEL_VOLUMINOUS` and may override individual keys (e.g. SWOT
uses `n_parallel_workers: 3`, `c_lib_threads: 2`).

### Memory management

| Key | Default | Description |
|---|---|---|
| `reduce_precision` | `true` | Store intermediate results in float32 to halve memory |
| `restart_workers_per_batch` | `true` | Restart Dask workers between batches to reclaim leaked memory |
| `cleanup_between_batches` | `true` | Delete prefetched files after each batch to free disk space |
| `max_worker_memory_fraction` | `0.65` | Trigger worker restart when managed memory exceeds this fraction |

### Resuming interrupted runs

Setting `resume: true` enables **checkpoint/resume**: the pipeline skips
already-completed batch result files on restart. This is essential for
long-running evaluations that may be interrupted by OOM kills or transient
network errors.

### Cluster lifecycle

The Dask cluster is **shut down automatically** after all evaluation batches
complete and before post-processing (results consolidation + leaderboard
generation), freeing worker RAM for the driver.

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
