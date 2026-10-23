

<!--
 Copyright 2021 IRT Saint Exupery, https://www.irt-saintexupery.com

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

<!--
Changelog titles are:
- Added: for new features.
- Changed: for changes in existing functionality.
- Deprecated: for soon-to-be removed features.
- Removed: for now removed features.
- Fixed: for any bug fixes.
- Security: in case of vulnerabilities.
-->

# Changelog

All notable changes of this project will be documented here.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0)
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Unreleased

## Added

- A `BaseDisciplineModel` takes a material, declared by `MATERIAL_FILE` or passed to its
  constructor (`material=...`, also through `create_model`). The material values are
  the default values of the discipline inputs of the same names. A `ValueError` is
  raised when a material property is not an input of the discipline.

## Fixed

- The cache of the discipline wrapped by a `BaseDisciplineModel` (GEMSEO sets a
  `SimpleCache` by default) is now disabled, the model managing the cache. With the
  model cache disabled, it still answered: the discipline was not executed but the
  model archived a new simulation.

# Version 0.1.7 (10/12/2026)

## Added

- Tools accept the data users already have: a mapping of variable names to values,
  a nested `{"inputs": ..., "outputs": ...}` mapping, a mono-index `DataFrame`, the
  legacy `name{group}[component]` `DataFrame` or a `Dataset`
  (`vimseo.utilities.datasets.to_dataset`, `resolve_io_groups`, `DatasetInput`).
  Input and output groups are resolved from explicit names or the model grammars.
  `StochasticValidationPointSettings.input_names` (#91).
- Models and load cases declare their figures with `PLOTS`: a tuple of variable names
  (abscissa then ordinates) or a `Plot` with several styled lines, a secondary
  ordinate axis, horizontal reference lines and an `x_label`. A load case `PLOTS`
  entry overrides the model one with the same abscissa and first ordinate, or adds
  a figure. Figures are rendered with Plotly. `ModelResult.plots` groups the curves
  per figure (`CurveSet`) (#107).
- `TanOpenHole`, an open-hole tension model (Tan), with utilities to extract lines
  from a field (#18).
- Optional extras `dashboard`, `mlflow`, `mesh`, `jax` and `all`: the mandatory
  dependencies only build, execute and serialize a model, so VIMSEO installs on a
  machine without graphical stack (HPC) (#18).
- `ReaderFileTecplot`, a reader of Tecplot ASCII files, with aliases of the
  coordinate variable names, and `FieldResult` (#64, #103).
- A model can be built with an alternative compatible material; material registry;
  `Ta6v_annealed` material.
- How-to page on configuring VIMSEO with `VIMSEO_*` environment variables or a
  `.env` file.

## Changed

- VIMSEO depends on the official `gemseo >= 6.3.3` and `gemseo-calibration >= 4.0.1`
  instead of the private forks `gemseo-vimseo` and `gemseo_calibration-vimseo`.
  Calibration follows the upstream renames: measures become metrics
  (`IntegratedMeasure` → `BaseIntegratedMetric`, `MeanMeasure` → `BaseMeanMetric`),
  settings `output`/`measure`/`mesh` → `output_name`/`metric_name`/`mesh_name`.
  The SBPISE curve-scaling settings move to `CalibrationMetricSettings`. The
  `ScatterMatrix` argument `coloring_variable` becomes `classifier` (#105).
- **Breaking:** the `CURVES` class attribute of the models is replaced by `PLOTS`; a
  model still declaring `CURVES` is rejected at import time. The per-load-case JSON
  file of `plot_parameters` is replaced by `LoadCase.PLOTS`; a stray JSON file next to
  a load case raises a `ValueError` (#107).
- **Breaking:** `plot_curves` is renamed `superpose_curves` (#107).
- The plots are no longer part of the load case and model descriptions; results
  saved with the former `plots` field still load (#107).
- Renamed the `TanOpenHole` model input `grid_size` to `grid_resolution` (number of
  grid points per direction), bounded to 5..1000 (#104).
- Mock models: `MockCurves` outputs `y_axis`/`y` → `x_history`/`y_history`;
  `MockMultiCurves` `critical_energy` → `critical_crack_position` (#107).
- The components are reorganized under `vimseo.core.components` (#58).
- The Streamlit dashboards move to `vimseo.dashboards`; the console scripts are
  updated (#56, #67).
- `api.create_model` merges `model_options` with keyword options (keyword wins)
  instead of rejecting the combination.

## Removed

- `vimseo.core.model_run_executor` and its unused entry point.
- The unfinished `MockModelLongRun` mock (#105).

## Fixed

- A model input silently rejected by the grammar and reverted to its default now
  raises a `ValueError` (#104).
- The `TanOpenHole` grid resolution was not applied (#104).
- The truncation bounds of the material properties are kept in the parameter space
  and its JSON serialization.
- The internal coupling variables of a `PreRunPostModel` are no longer archived, so
  `create_cache_from_archive` replays archived runs (#105).
- `JobExecutor` splits commands with `shlex`, keeping quoted arguments (#105).
- The external software subprocess is killed in every case (#52).
- `ReaderFileTecplot` reads every zone, not only the first one (#103).
- Conversion of a `DataFrame` to a `Dataset` in the database viewer (#67).
- Serialization roundtrip of pandas masked dtypes; Python 3.10 compatibility
  (`operator.call`); intermittent pydantic "not fully defined" errors (#105).
- Documentation: broken links, image paths, popups and crash of the doc build
  (#54, #62, #87).

# Version 0.1.6 (05/12/2026)

## Added

- Export to disk of analysis results (DOE, Sensitivity etc...) in hd5 format.

## Changed

- None

## Fixed

- None
