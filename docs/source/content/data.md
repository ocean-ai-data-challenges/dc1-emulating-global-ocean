# Data

## Training data

DC1 does not prescribe a fixed training dataset. Participants can use reanalyses,
observations, model outputs, and their own preprocessing pipelines.

## Evaluation references

The default DC1 configurations evaluate submissions against:

- GLORYS (gridded reference fields)
- SARAL (altimetry)
- Jason-3 (altimetry)
- SWOT (wide-swath altimetry)
- Argo profiles (surface extraction of TEMP/PSAL)

Depending on the selected YAML profile and parameters, additional datasets may be available.

## Evaluation period

- Start: 2024-01-01
- End: 2025-01-01 (profile-dependent during testing)

## Surface-only rule

Even when source datasets are 3-D, DC1 scoring is performed on surface values only.

## Where dataset definitions live

Dataset sources and metric assignments are defined in:

- `dc1/config/dc1_wasabi.yaml`
- `dc1/config/dc1_edito.yaml`

These files contain:

- connection settings (public or credentialed endpoints)
- per-dataset `keep_variables` and `eval_variables`
- matching tolerances
- metric lists (`rmsd`, `mae`, etc.)

## Practical note

The local run workflow does not require manual download of all references.
The evaluation pipeline fetches and caches required data as needed under the output directory.
