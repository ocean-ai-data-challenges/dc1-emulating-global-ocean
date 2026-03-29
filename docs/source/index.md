# DC 1: Emulation of Global Ocean Reanalyses

**DC1** is an open benchmark for **emulating global ocean reanalyses at the surface level**,
part of the [PPR Océan & Climat](https://www.ocean-climat.fr/) national research programme
(CNRS / Ifremer).

Participants build a neural emulator on historical ocean data and submit **10-day surface-level
emulations** of the global ocean state (SSH, temperature, salinity, currents) at 0.25°
resolution. Predictions are evaluated against independent satellite altimetry (SARAL, Jason-3,
SWOT), Argo surface measurements, and the GLORYS12 reanalysis over the period
**January 2024 – January 2025**.

Unlike [DC2](https://github.com/ocean-ai-data-challenges/dc2-forecasting-global-ocean-dynamics)
which evaluates forecasts across the full 3-D water column (21 depth levels), **DC1 focuses
exclusively on surface-level (2-D) evaluation**. All predicted variables are assessed at the
ocean surface only.

::::{grid} 2
:::{grid-item-card} 🌊 Scientific context
:link: content/task
:link-type: doc

Task definition, variables, evaluation setup and reference model (GloNet).
:::

:::{grid-item-card} 📊 Datasets
:link: content/data
:link-type: doc

Training data (free choice), evaluation observations, and the GLORYS12 reference.
:::

:::{grid-item-card} 📐 Metrics
:link: content/metrics
:link-type: doc

RMSD and geostrophic current RMSD — surface-level evaluation only.
:::

:::{grid-item-card} 🏆 Leaderboard
:link: content/leaderboard
:link-type: doc

Live leaderboard with interactive maps comparing submitted models.
:::
::::

## Quick start

```bash
# 1. Clone and install
git clone https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean.git
cd dc1-emulating-global-ocean
conda create --name dc1 python=3.11 && conda activate dc1
conda install -c conda-forge esmf esmpy
poetry install

# 2. Validate a submission
python dc1/submit.py validate /path/to/my_model --model-name my_model

# 3. Run the evaluation
python dc1/submit.py run /path/to/my_model --model-name my_model
```

For detailed installation options (Docker, EDITO Datalab), see the
{doc}`Quickstart guide <content/quickstart>`.

## Citing DC1

If you use DC1 in your research, please cite the challenge description paper and the relevant
observation datasets listed in {doc}`content/references`.

> Ait Mohand, K., Cossio, G., et al. (2025).
> *DC1: An Open Benchmark for Emulating Global Ocean Reanalyses.*
> PPR Océan & Climat / CNRS / Ifremer.
> [GitHub repository](https://github.com/ppr-ocean-ia/dc1-emulating-global-ocean)

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
