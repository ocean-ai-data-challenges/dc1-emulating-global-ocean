# DC1: Emulation of Global Ocean Reanalyses

DC1 is an open benchmark for emulating global ocean reanalyses at the surface level.
Participants submit 10-day global surface emulations (0.25 deg grid) and are evaluated
against independent satellite and in situ observations.

Challenge period: 2024-01-01 to 2025-01-01.

Required variables:

- `zos` (sea surface height)
- `thetao` (sea surface temperature)
- `so` (sea surface salinity)
- `uo` (surface eastward current)
- `vo` (surface northward current)

All evaluation in DC1 is surface-only.

::::{grid} 2
:::{grid-item-card} Scientific context
:link: content/task
:link-type: doc

Task definition, variables, evaluation schedule, baseline.
:::

:::{grid-item-card} Data
:link: content/data
:link-type: doc

Reference datasets and practical data notes.
:::

:::{grid-item-card} Metrics
:link: content/metrics
:link-type: doc

RMSD-based metrics used by the evaluation pipeline.
:::

:::{grid-item-card} Submissions
:link: content/submissions
:link-type: doc

Input layouts, validation, and run commands.
:::
::::

## Quick start

```bash
# 1) Install (example: conda + pip)
git clone https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean.git
cd dc1-emulating-global-ocean
conda create --name dc1 python=3.11
conda activate dc1
conda install -c conda-forge esmf esmpy
python -m pip install -U pip
python -m pip install -e .
python -m pip install "dctools @ git+https://github.com/ocean-ai-data-challenges/dc-tools.git"

# 2) Validate
poetry run python dc1/submit.py validate /path/to/my_model --model-name my_model

# 3) Run full pipeline
poetry run python dc1/submit.py run /path/to/my_model --model-name my_model --data-directory ./dc1_output
```

For Docker and EDITO options, see {doc}`content/quickstart`.

```{toctree}
:maxdepth: 2
:caption: Getting started

content/quickstart.md
content/evaluation.md
content/submissions.md
```

```{toctree}
:maxdepth: 2
:caption: DC1 Challenge

content/task.md
content/data.md
content/metrics.md
content/leaderboard.md
content/references.md
```

```{toctree}
:maxdepth: 2
:caption: API Reference

content/api
content/dctools_api
```
