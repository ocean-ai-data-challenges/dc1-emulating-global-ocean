# Submissions

This page describes accepted input formats and the CLI workflow used in this repository.

## CLI entrypoint

Use the repository script:

```bash
python dc1/submit.py <command> ...
```

Equivalent module form:

```bash
python -m dc1.submit <command> ...
```

## Required content

DC1 evaluates surface-only variables:

- `zos`
- `thetao`
- `so`
- `uo`
- `vo`

Expected target grid:

- latitude: -78 to 90, step 0.25 (672 points)
- longitude: -180 to 180, step 0.25 (1440 points)
- lead times: 0..9

Submissions can be native 2-D fields `(time, lat, lon)`. If depth exists,
surface extraction is applied during evaluation.

## Accepted layouts for `data_path`

The validator accepts:

1. Single zarr store
2. Single netcdf file (`.nc` or `.nc4`)
3. Directory of forecast files (for example one zarr per initialization date)
4. Glob pattern (for example `/data/model/*.nc`)

Recommended layout:

```text
my_model/
  2024-01-03.zarr
  2024-01-10.zarr
  ...
```

## Validate

```bash
python dc1/submit.py validate <data_path> --model-name <MODEL_NAME>
```

Common options:

- `--quick`
- `--save-report path.json` (or `--output path.json`)
- `--variables zos thetao`
- `--max-nan-fraction 0.10`

## Run

```bash
python dc1/submit.py run <data_path> --model-name <MODEL_NAME> -d ./dc1_output
```

Common options:

- `--skip-validation`
- `--quick-validation`
- `--force`
- `--team`, `--description`, `--email`, `--url`

## Inspect expected specification

```bash
python dc1/submit.py info --config dc1
```

## Typical output files

- `dc1_output/results/results_<MODEL_NAME>.json`
- `dc1_output/results/results_<MODEL_NAME>_per_bins.jsonl.gz`
- `dc1_output/results/coordinate_conformance_report.json`

## Leaderboard submission process

To appear on the official leaderboard, share at least:

1. `results_<MODEL_NAME>.json`
2. model description and training data summary
3. paper or repository URL

For questions, open an issue in the project repository.
