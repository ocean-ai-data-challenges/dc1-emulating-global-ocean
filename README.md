# DC1 - Emulating Global Ocean Reanalyses

[![Documentation](https://readthedocs.org/projects/dc1-emulating-global-ocean/badge/?version=latest)](https://dc1-emulating-global-ocean.readthedocs.io/en/latest/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

Data Challenge 1 (DC1) is an open benchmark for emulating global ocean reanalyses at the
surface level. Participants submit 10-day global surface emulations and are evaluated
against independent satellite and in situ observations over the period 2024-01-01 to
2025-01-01.

DC1 is surface-only (2-D). Unlike DC2, no depth-resolved submission is required.

## Challenge summary

Required predicted variables:

- `zos` (sea surface height)
- `thetao` (sea surface temperature)
- `so` (sea surface salinity)
- `uo` (surface eastward current)
- `vo` (surface northward current)

Expected shape for a flat submission is `(time, lat, lon) = (10, 672, 1440)`.
If a depth axis is present, the evaluation pipeline enforces surface-only processing.

Reference datasets used during evaluation include GLORYS, SARAL, Jason-3, SWOT, and Argo
profiles (surface extraction).

## Installation

### Option A (recommended): Docker image

```bash
docker run -it --rm --name dc1 \
  ghcr.io/ocean-ai-data-challenges/dc1-emulating-global-ocean:latest bash
```

JupyterLab mode:

```bash
docker run --rm -p 8888:8888 --name dc1-lab \
  ghcr.io/ocean-ai-data-challenges/dc1-emulating-global-ocean:latest
```

Build instructions are available in `docker/README.md`.

### Option B: local environment (Conda + pip)

```bash
git clone https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean.git
cd dc1-emulating-global-ocean

conda create --name dc1 python=3.11
conda activate dc1
conda install -c conda-forge esmf esmpy

python -m pip install -U pip
python -m pip install -e .
python -m pip install "dctools @ git+https://github.com/ocean-ai-data-challenges/dc-tools.git"
```

The `dc1` package itself is in this repository. The evaluation CLI also requires
`dctools` at runtime.

### Option C: EDITO Datalab

A ready-to-use environment is available at:

<https://datalab.dive.edito.eu/launcher/service-playground/dc1-emulating-global-ocean>

## Usage

### 1. Validate a submission

```bash
python dc1/submit.py validate /path/to/my_model --model-name MyModel
```

Useful options:

- `--quick` for a faster pre-check
- `--save-report report.json` to write the validation report
- `--variables zos thetao` for partial validation

### 2. Run full submission pipeline (recommended)

```bash
python dc1/submit.py run /path/to/my_model --model-name MyModel \
  -d ./dc1_output \
  --team "My Team" \
  --description "Short description"
```

This command chains validation, evaluation, and result generation.

### 3. Inspect expected specification

```bash
python dc1/submit.py info --config dc1
```

### 4. Low-level evaluation entrypoint

`dc1/evaluate.py` is the low-level runner used by the pipeline. In most cases,
prefer `submit.py run`.

```bash
python dc1/evaluate.py --model-name MyModel
```

By default, `dc1/evaluate.py` writes logs and outputs under `dc1_output/`.

## Outputs

Typical generated artifacts:

- `dc1_output/results/results_<MODEL_NAME>.json`
- `dc1_output/results/results_<MODEL_NAME>_per_bins.jsonl.gz` (when per-bin export is enabled)
- `dc1_output/results/coordinate_conformance_report.json`
- `dc1_output/logs/dc1.log`

## Configuration

DC1 config files are in `dc1/config/`:

- `dc1_wasabi.yaml` (default repository profile)
- `dc1_edito.yaml` (EDITO/public profile)

Key runtime controls include:

- parallelism presets (`parallelism_presets`, `voluminous_parallelism_presets`)
- memory safety (`restart_workers_per_batch`, `max_worker_memory_fraction`)
- resume mode (`resume: true`)
- per-bin map resolution (`per_bins_resolution`)

## Documentation

Full docs: <https://dc1-emulating-global-ocean.readthedocs.io>

Build locally:

```bash
python -m pip install -r docs/requirements.txt
sphinx-build -b html docs/source docs/build/html
```

## Project structure

```text
dc1/
  config/
  evaluation/
  evaluate.py
  submit.py
docs/
docker/
notebooks/
```

## License

GPL-3.0. See `LICENSE`.
