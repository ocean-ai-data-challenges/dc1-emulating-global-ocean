# Evaluation metrics

All metrics are computed by the `dctools` library
([`dctools.metrics`](https://github.com/ocean-ai-data-challenges/dc-tools)), which relies on
the [OceanBench](https://github.com/jejjohnson/oceanbench) backend from Mercator Ocean. The
orchestrating class is `DC1Evaluation` (`dc1/evaluation/dc1.py`), inherited from
`BaseDCEvaluation` in `dctools`.

---

## Evaluation pipeline

For each initialisation date in the period 2024-01-01 → 2025-01-01 (one emulation every
7 days, i.e. 52 cycles):

1. The submitted model is loaded; its **surface fields** are spatially and temporally
   interpolated to the exact positions of each reference dataset using **`pyinterp`**
   (bilinear interpolation).
2. The **temporal matching window** is ±12 hours around each observation.
3. Metrics are computed per variable and per forecast lead time (lead-time 0 to 9 days).
   Since DC1 is surface-only, **no depth decomposition** is performed (unlike DC2).
4. Results are aggregated by initialisation date and then published on the leaderboard.

### DC1 variable ↔ OceanBench internal name mapping

| DC1 variable | CF standard name | OceanBench identifier |
|---|---|---|
| `zos` | `sea_surface_height_above_geoid` | `SEA_SURFACE_HEIGHT_ABOVE_GEOID` |
| `thetao` | `sea_water_potential_temperature` | `SEA_WATER_POTENTIAL_TEMPERATURE` |
| `so` | `sea_water_salinity` | `SEA_WATER_SALINITY` |
| `uo` | `eastward_sea_water_velocity` | `EASTWARD_SEA_WATER_VELOCITY` |
| `vo` | `northward_sea_water_velocity` | `NORTHWARD_SEA_WATER_VELOCITY` |

---

## Metrics per reference dataset

The following table summarises the metrics assigned in `dc1/config/dc1_wasabi.yaml`:

| Reference dataset | Applied metric(s) | Evaluated variables |
|---|---|---|
| SARAL/AltiKa | `rmsd` | `zos` (SSH anomaly) |
| Jason-3 | `rmsd` | `zos` (SSH anomaly) |
| SWOT (KaRIn + nadir) | `rmsd` | `zos` (filtered SSH) |
| Argo (profiles — surface) | `rmsd` | `thetao`, `so` |
| GLORYS12 (surface level) | `rmsd` | `ssh`, `temperature`, `salinity`, `u_current`, `v_current` |

> **Note:** Unlike DC2, DC1 does **not** compute depth-resolved metrics, Lagrangian trajectory
> deviations, Mixed Layer Depth RMSD, or Class 4 metrics. The evaluation is purely surface-level.

---

## 1. RMSD — Root Mean Square Deviation

The central metric of DC1. For each *(emulation, observation)* pair, the predicted surface
field is interpolated to the observation positions; the RMSD is then:

$$
\text{RMSD} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} \left( \hat{x}_i - x_i \right)^2}
$$

where $\hat{x}_i$ is the predicted value at position $i$ and $x_i$ the observed value.

Two variants coexist in `dctools.metrics.oceanbench_metrics`:

| Case | Function used |
|---|---|
| Reference available (real-time obs) | `func_with_ref: rmsd` (oceanbench) |
| No reference (GLORYS12 comparison) | `func_no_ref: rmsd_of_variables_compared_to_glorys` |

### Spatial RMSD maps by bins

In addition to the global score, the pipeline computes **per-cell RMSD maps** at a configurable
resolution (default `per_bins_resolution = 1°` in DC1). These maps are published on the
leaderboard as interactive visualisations, enabling regional error diagnosis at the surface.

---

## 2. Geostrophic current RMSD

Surface geostrophic currents $(u_g, v_g)$ are derived from the SSH field $\eta$ using the
geostrophic balance relations:

$$
u_g = -\frac{g}{f} \frac{\partial \eta}{\partial y}, \qquad
v_g = \frac{g}{f} \frac{\partial \eta}{\partial x}
$$

with $g = 9.81\,\text{m s}^{-2}$ and $f = 2\Omega\sin\phi$ the Coriolis parameter.

This metric is particularly relevant for DC1 because it **evaluates the quality of the SSH
gradient without any depth dependency**, making it sensitive to mesoscale surface features
(eddies, fronts) — exactly the type of dynamics that a 2-D surface emulator should capture.

> **Advantage**: this metric evaluates the quality of the SSH gradient independently of any
> absolute altitude offset.

---

## Aggregation and leaderboard

Scores are computed for each initialisation date, then aggregated (mean ± standard deviation)
over the entire 2024–2025 period. The leaderboard publishes:

- a global score per metric and per variable;
- spatial RMSD maps per bin (1° × 1° resolution) for each forecast lead time.

Since DC1 is surface-only, there is **no depth decomposition** in the leaderboard tables
(unlike DC2 which breaks down scores by depth level for `thetao`, `so`, `uo`, `vo`).

See the [leaderboard](leaderboard.md) for current scores and interactive maps.
