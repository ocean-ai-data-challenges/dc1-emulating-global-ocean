# Evaluation

This page describes what happens when you run DC1 evaluation and which configuration knobs
matter in practice.

## Run commands

Recommended command:

```bash
poetry run python dc1/submit.py run <data_path> --model-name <MODEL_NAME> --data-directory ./dc1_output
```

Validation only:

```bash
poetry run python dc1/submit.py validate <data_path> --model-name <MODEL_NAME>
```

Low-level runner:

```bash
poetry run python dc1/evaluate.py --model-name <MODEL_NAME>
```

`evaluate.py` injects default paths under `dc1_output/` when they are not provided.

## Main pipeline stages

1. Read submission files and normalize coordinates/aliases.
2. Enforce surface-only processing (`surface_only = true` in `DC1Evaluation`).
3. Fetch and prepare reference observations/reanalysis according to YAML config.
4. Interpolate predictions to observation support and compute configured metrics.
5. Write consolidated outputs under the chosen data directory.

## Default outputs

Typical files produced in `dc1_output/results/`:

- `results_<MODEL_NAME>.json`
- `results_<MODEL_NAME>_per_bins.jsonl.gz` (when per-bin output is enabled)
- `coordinate_conformance_report.json`

Logs are written in `dc1_output/logs/` (default logfile name `dc1.log`).

## Configuration profiles

DC1 ships two YAML profiles in `dc1/config/`:

- `dc1_wasabi.yaml`
- `dc1_edito.yaml`

Important keys to tune:

- `parallelism_presets` and `voluminous_parallelism_presets`
- `restart_workers_per_batch`
- `cleanup_between_batches`
- `resume`
- `max_worker_memory_fraction`
- `per_bins_resolution`

## Surface-only behavior

DC1 is strictly 2-D at evaluation time. If input data contains a depth dimension,
the pipeline uses surface extraction and evaluates only the top level.

## Temporal setup

- Evaluation window: 2024-01-01 to 2025-01-01
- Forecast horizon: 10 lead times (0..9)
- Matching tolerance in configs: typically 12 hours for observation datasets

## Practical guidance

- Use `validate --quick` before full runs for fast format checks.
- Keep `resume: true` for long jobs.
- Adjust worker counts and memory limits before increasing batch sizes.
- Start with a short period/profile when benchmarking a new environment.
