# Quickstart

This page gets you from zero to a validated evaluation run in a few minutes.

---

## 1. Installation

Choose one of three options:

### Option A — Local installation (conda + Poetry)

Install [Poetry](https://python-poetry.org/) (e.g. via [pipx](https://pipx.pypa.io/):
`pipx install poetry`), then:

```bash
# Clone the repository
git clone https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean.git
cd dc1-emulating-global-ocean

# Create a conda environment and install ESMF (not supported by Poetry)
conda create --name dc1 python=3.11
conda activate dc1
conda install -c conda-forge esmf esmpy

# Install project dependencies
poetry lock
poetry install

# (Optional) Install dev dependencies (pytest, ruff, mypy, poethepoet…)
poetry install --with dev
```

### Option B — Docker

A pre-built Docker image includes all dependencies:

```bash
# Console mode
docker run -it --rm --name dc1 \
    ghcr.io/ocean-ai-data-challenges/dc1-emulating-global-ocean:latest bash

# JupyterLab mode
docker run --rm -p 8888:8888 --name dc1-lab \
    ghcr.io/ocean-ai-data-challenges/dc1-emulating-global-ocean:latest
```

See [`docker/`](https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean/tree/main/docker)
for build and publish instructions.

### Option C — EDITO Datalab

A ready-to-use environment is available on the EDITO Datalab platform (no local
installation required):

> <https://datalab.dive.edito.eu/launcher/service-playground/dc1-emulating-global-ocean>

Open a terminal inside the service and run the commands described below.

---

## 2. Prepare a surface emulation

Your emulation must conform to the DC1 grid (0.25° × 0.25°, surface only, 10 lead-time
days). The recommended format is **one Zarr store per initialisation date** (Layout A):

```
my_model/
    2024-01-03.zarr
    2024-01-10.zarr
    ...
    2024-12-25.zarr
```

All five variables (`zos`, `thetao`, `so`, `uo`, `vo`) are 2-D surface fields with
shape `(10, 672, 1440)`. If your dataset includes a depth axis, the pipeline will
automatically extract the surface level (~0.49 m).

See {doc}`submissions` for the full grid specification and accepted file formats.

---

## 3. Validate the format

Before running the full evaluation, verify that the submission is correctly formatted:

```bash
python dc1/submit.py validate /path/to/my_model --model-name my_sample
```

A successful run prints a conformance summary. See {doc}`submissions` for all validation
options and the full grid specification.

---

## 4. Run the evaluation

Launch the complete evaluation pipeline:

```bash
python dc1/submit.py run /path/to/my_model --model-name my_sample
```

This will:
1. Download observation catalogues from the DC1 S3 bucket.
2. Extract the surface level from any 3-D data (`standardize_to_surface`).
3. Interpolate emulated surface fields to observation positions.
4. Compute metrics (RMSD, geostrophic current RMSD).
5. Write results to `dc1_output/results/results_my_sample.json`.

See {doc}`evaluation` for detailed options and pipeline internals.

---

## 5. Inspect the configuration

The `info` subcommand displays the full specification (grid, variables, metrics,
accepted formats) without running any computation:

```bash
python dc1/submit.py info --config dc1
```

---

## Next steps

- {doc}`evaluation` — detailed evaluation options and pipeline steps
- {doc}`submissions` — submission format, file layouts, and leaderboard participation
- {doc}`metrics` — explanation of every metric
- {doc}`data` — datasets used for evaluation
