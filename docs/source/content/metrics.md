# Metrics

Metrics are computed by `dctools` during evaluation and aggregated in the result JSON files.

## Core metric

The main score family is RMSD (Root Mean Square Deviation):

$$
\mathrm{RMSD} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} (\hat{x}_i - x_i)^2}
$$

where $\hat{x}_i$ is the model value interpolated at observation location/time and $x_i$
is the reference value.

## Metric set in current DC1 configs

In `dc1/config/dc1_wasabi.yaml` and `dc1/config/dc1_edito.yaml`, dataset-level metric lists
typically include:

- `rmsd`
- `mae` (for several observation datasets)

The pipeline also supports leaderboard display labels for additional metrics via
`dc1/config/leaderboard_config.yaml`.

## Surface-only evaluation

DC1 metrics are computed on surface data only. If depth is present in inputs, the evaluation
extracts the surface level before interpolation/scoring.

## Spatial per-bin outputs

When enabled, the pipeline exports per-bin metric summaries using `per_bins_resolution`
(configured in YAML). This is used for map-based diagnostics.

## Practical interpretation

- Lower values indicate better agreement with references.
- Compare scores by variable and lead time rather than only a single global value.
- Validate stability across references (altimetry, Argo, gridded reanalysis).
