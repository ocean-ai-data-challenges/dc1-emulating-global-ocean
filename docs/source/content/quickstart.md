# Quickstart

This page gets you from installation to a first validated run.

## 1. Install

Choose one option.

### Option A: Docker (recommended)

```bash
docker run -it --rm --name dc1 \
    ghcr.io/ocean-ai-data-challenges/dc1-emulating-global-ocean:latest bash
```

JupyterLab mode:

```bash
docker run --rm -p 8888:8888 --name dc1-lab \
    ghcr.io/ocean-ai-data-challenges/dc1-emulating-global-ocean:latest
```

### Option B: local Conda + pip

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

### Option C: EDITO Datalab

<https://datalab.dive.edito.eu/launcher/service-playground/dc1-emulating-global-ocean>

## 2. Prepare model outputs

Recommended layout (one zarr store per initialization date):

```text
my_model/
    2024-01-03.zarr
    2024-01-10.zarr
    ...
    2024-12-25.zarr
```

Target shape is surface-only `(time, lat, lon) = (10, 672, 1440)` for each variable.

## 3. Validate

```bash
python dc1/submit.py validate /path/to/my_model --model-name my_model
```

Quick validation:

```bash
python dc1/submit.py validate /path/to/my_model --model-name my_model --quick
```

## 4. Run full pipeline

```bash
python dc1/submit.py run /path/to/my_model --model-name my_model -d ./dc1_output
```

This command performs validation, evaluation, and result export.

## 5. Inspect expected spec

```bash
python dc1/submit.py info --config dc1
```

## Next pages

- {doc}`submissions`
- {doc}`evaluation`
- {doc}`metrics`
- {doc}`data`
