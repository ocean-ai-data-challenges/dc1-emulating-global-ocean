# Task description

## Overview

Data Challenge 1 (DC1) is an open benchmark for **emulating global ocean reanalyses at the
surface level**. Participants train a neural emulator on historical ocean data and submit
10-day surface-level predictions of the global ocean state. Predictions are evaluated against
a suite of independent in-situ and satellite observations covering the period
**1 January 2024 – 1 January 2025**.

The fundamental goal of DC1 is to assess whether neural networks can faithfully reproduce
the time evolution of a global ocean reanalysis (e.g. GLORYS12) using only 2-D surface
fields, without requiring the full 3-D water column.

DC1 is part of the [PPR Océan & Climat](https://www.ocean-climat.fr/) (*Projet Prioritaire
de Recherche*), a national research program launched by the French government and managed
by CNRS and Ifremer to improve understanding of the ocean and climate.

## Goal

Given any set of input data (e.g. reanalysis fields, satellite observations, in-situ
profiles), produce daily global ocean state emulations at 0.25° × 0.25° horizontal
resolution for lead times $t = 0, 1, \ldots, 9$ days. Five physical variables must be
predicted **at the surface level only**:

| CF standard name | Short name | Description |
|---|---|---|
| `sea_surface_height_above_geoid` | `zos` | Sea surface height |
| `sea_water_potential_temperature` | `thetao` | Sea surface temperature |
| `sea_water_salinity` | `so` | Sea surface salinity |
| `eastward_sea_water_velocity` | `uo` | Surface eastward current |
| `northward_sea_water_velocity` | `vo` | Surface northward current |

All variables are 2-D fields with dimensions `(time, lat, lon)`. Unlike DC2, **no depth
dimension is required**: the evaluation pipeline automatically extracts the surface level
(~0.5 m depth) from any submission that includes a depth axis.

## Evaluation setup

Predictions are launched every **7 days** (evaluation interval) throughout the benchmark
year. Each forecast covers **10 days** of lead time. The evaluation pipeline:

1. Downloads or reads the submitted emulation for each initialization date.
2. Interpolates predicted surface fields to the space-time locations of each observation
   dataset.
3. Computes RMSD (and other metrics) between the interpolated prediction and the
   observations.
4. Aggregates scores per variable and lead time and publishes them on the
   [leaderboard](leaderboard.md).

## Spatial domain

The target grid covers the global ocean **at the surface only**:

- **Latitude:** −78° to +90° (step 0.25°, 672 points)
- **Longitude:** −180° to +180° (step 0.25°, 1 440 points)
- **Depth:** surface only (~0.49 m)

This is the key distinction from DC2 which evaluates on 21 depth levels from ~0.5 m to
~5 275 m.

## Reference model — GloNet

The baseline against which all submissions are compared is **GloNet** (*Global Neural Ocean
Forecasting System*), a deep-learning model developed by Mercator Ocean International within
the PPR Océan & Climat framework. GloNet produces daily global forecasts at 0.25° resolution.
For DC1, only the surface level of GloNet's output is used for evaluation, serving as the
benchmark score on the leaderboard.
