# DC1 — Emulating Global Ocean Reanalyses

[![Documentation](https://readthedocs.org/projects/dc1-emulating-global-ocean/badge/?version=latest)](https://dc1-emulating-global-ocean.readthedocs.io/en/latest/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

**Data Challenge 1 (DC1)** is an open benchmark for **emulating global ocean reanalyses at
the surface level**. Participants build neural emulators that reproduce the time evolution
of the global 2-D ocean state vector (latitude × longitude), given perfectly known initial
conditions and time-varying forcings. Predictions are evaluated against independent in-situ
and satellite observations over the period **January 2024 – January 2025**.

Unlike [DC2](https://github.com/ocean-ai-data-challenges/dc2-forecasting-global-ocean-dynamics)
which evaluates forecasts across the full 3-D water column (21 depth levels), **DC1 focuses
exclusively on surface-level (2-D) evaluation**. All predicted variables are assessed at the
ocean surface only.

DC1 is part of the [PPR Océan & Climat](https://www.ocean-climat.fr/) (*Projet Prioritaire de
Recherche*), a national programme launched by the French government and managed by CNRS and
Ifremer.

---

## Scientific overview

### Task

Given any set of input data (reanalysis, satellite observations, in-situ profiles…), produce
daily global ocean surface state emulations for lead times 0–9 days. Five physical variables
must be predicted **at the surface level only**:

| Variable | Description | Dimensions |
|---|---|---|
| `zos` | Sea surface height | 2-D (surface) |
| `thetao` | Sea surface temperature | 2-D (surface) |
| `so` | Sea surface salinity | 2-D (surface) |
| `uo` | Surface eastward current | 2-D (surface) |
| `vo` | Surface northward current | 2-D (surface) |

All variables have shape `(time, lat, lon)` — **no depth dimension is required** (unlike DC2
where `thetao`, `so`, `uo`, `vo` have 21 depth levels).

### Evaluation data

Surface emulations are evaluated against five independent reference datasets:

- **GLORYS12** — Global ocean reanalysis (surface level only)
- **SARAL/AltiKa** — Ka-band along-track altimetry (SSH)
- **Jason-3** — Ku-band along-track altimetry (SSH)
- **SWOT** — Wide-swath 2-D radar interferometry (SSH)
- **Argo floats** — In-situ surface temperature & salinity (shallowest measurement only)

### Metrics

- **RMSD** (Root Mean Square Deviation) against all reference datasets
- **Geostrophic current RMSD** derived from the SSH gradient

> DC1 does **not** compute depth-resolved metrics, Mixed Layer Depth RMSD, Lagrangian
> trajectory deviation, or Class 4 metrics (which are specific to DC2's 3-D evaluation).

### Reference model

The baseline is **GloNet** (Global Neural Ocean Forecasting System), developed by Mercator Ocean
International within the PPR Océan & Climat framework. For DC1, only the surface level of
GloNet's output is used for evaluation.

> For a detailed description of the task, data, and metrics, see the
> [scientific documentation](https://dc1-emulating-global-ocean.readthedocs.io/en/latest/).

---

## Getting started

### Option A — Local installation (conda + Poetry)

**Prerequisites:** [Conda](https://docs.conda.io/) (or Mamba/Micromamba) and
[Poetry](https://python-poetry.org/) (install via
[pipx](https://pipx.pypa.io/): `pipx install poetry`).

```bash
# 1. Clone the repository
git clone https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean.git
cd dc1-emulating-global-ocean

# 2. Create a conda environment and install ESMF (not supported by Poetry)
conda create --name dc1 python=3.11
conda activate dc1
conda install -c conda-forge esmf esmpy

# 3. Install project dependencies with Poetry
poetry lock
poetry install

# 4. (Optional) Install dev dependencies (pytest, ruff, mypy, poethepoet…)
poetry install --with dev
```

**Quick test:**

```bash
poetry run python -c "import dc1; print('dc1 installed successfully')"
```

### Option B — Docker

A pre-built Docker image includes all dependencies (see [`docker/`](docker/) for
build instructions):

```bash
# Console mode
docker run -it --rm --name dc1 \
    ghcr.io/ocean-ai-data-challenges/dc1-emulating-global-ocean:latest bash

# JupyterLab mode
docker run --rm -p 8888:8888 --name dc1-lab \
    ghcr.io/ocean-ai-data-challenges/dc1-emulating-global-ocean:latest
```

Then open the JupyterLab URL printed in the terminal and use the built-in terminal.

### Option C — EDITO Datalab

A ready-to-use environment is available on the **EDITO Datalab** platform (no local
installation required):

> <https://datalab.dive.edito.eu/launcher/service-playground/dc1-emulating-global-ocean>

Open a terminal inside the service and run the evaluation commands described below.

---

## Evaluating a new model

### 1. Prepare your surface emulation

Your emulation must conform to the DC1 grid (0.25° × 0.25°, surface only, 10 lead-time
days). The recommended format is **one Zarr store per initialisation date** (Layout A):

```
my_model/
    2024-01-03.zarr
    2024-01-10.zarr
    ...
    2024-12-25.zarr
```

All variables are 2-D surface fields with shape `(10, 672, 1440)`. If your dataset
includes a depth axis, the pipeline will automatically extract the surface level (~0.49 m).

### 2. Validate the submission format

```bash
python dc1/submit.py validate /path/to/my_model --model-name MyModel
```

This checks variable presence, grid conformity, NaN fraction (< 10%), temporal coverage,
and CF metadata. Add `--quick` for a fast check on the first few dates only.

### 3. Run the full evaluation

```bash
python dc1/evaluate.py --model-name MyModel
```

Or, equivalently, via the submit CLI (validate → evaluate → leaderboard):

```bash
python dc1/submit.py run /path/to/my_model --model-name MyModel \
    -d ./dc1_output \
    --team "My Team" \
    --description "Short description of the model"
```

The pipeline will:
1. Download observation catalogues (SARAL, Jason-3, SWOT, Argo, GLORYS12)
2. Extract surface level from any 3-D data (`standardize_to_surface`)
3. Interpolate emulated surface fields to observation positions
4. Compute metrics (RMSD, geostrophic current RMSD)
5. Write results to `dc1_output/results/results_<MODEL_NAME>.json`

> **Tip — resuming interrupted runs:** the configuration option `resume: true` (enabled
> by default) lets the pipeline skip already-completed batches when restarted after a
> crash or interruption.

### Configuration

The pipeline is configured via `dc1/config/dc1_wasabi.yaml`. Key settings include:

- **Parallelism presets** (`parallelism_presets` and `voluminous_parallelism_presets`)
  controlling Dask worker count, memory limits, batch sizes, and download concurrency.
- **Memory safety** (`restart_workers_per_batch`, `cleanup_between_batches`,
  `max_worker_memory_fraction`) to handle long runs on memory-constrained machines.
- **Resume** (`resume: true`) to skip already-completed batches on restart.

See the [evaluation documentation](https://dc1-emulating-global-ocean.readthedocs.io/en/latest/content/evaluation.html#configuration-profiles)
for details on tuning these presets for your hardware.

### 4. Inspect the DC1 specification

```bash
python dc1/submit.py info --config dc1
```

---

## Submitting to the leaderboard

To appear on the official DC1 leaderboard, send the following to the organisers:

1. The **`results_<MODEL_NAME>.json`** file (aggregated scores)
2. A brief description of the model and training data
3. A reference (paper, preprint, or code repository)

The result file is produced by the evaluation pipeline in `dc1_output/results/`.

Open a [GitHub issue](https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean/issues)
for any questions about submission.

---

## Documentation

- **Full technical documentation** (task, data, metrics, API reference):
  [dc1-emulating-global-ocean.readthedocs.io](https://dc1-emulating-global-ocean.readthedocs.io)

---

## Project structure

```
dc1/                  # Core package
  config/             # YAML configuration (dc1_wasabi.yaml)
  evaluation/         # DC1-specific evaluation logic (surface-only)
  evaluate.py         # CLI: run evaluation
  submit.py           # CLI: validate & submit
docker/               # Dockerfile & conda environment
docs/                 # Sphinx documentation (readthedocs)
notebooks/            # Jupyter notebooks
```

---

## What is the PPR Océan & Climat?

A *Priority Research Project* launched by the French government and managed by CNRS and Ifremer,
aiming to structure French research efforts to improve understanding of the ocean and climate.
See the [project website](https://www.ocean-climat.fr/) (in French) for more details.

---

## License

This project is licensed under the [GPL-3.0](LICENSE) license.
