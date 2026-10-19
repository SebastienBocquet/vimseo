

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

# Version 0.1.6 (05/12/2026)

## Added

- Export to disk of analysis results (DOE, Sensitivity etc...) in hd5 format.
- `PostProcessor.POSTPROCESS_DESPITE_FAULTY_RUN`: a post-processor can opt in to
  postprocess a faulty run, provided that `_can_postprocess()` finds what it needs
  in the job directory.
- `solver_utilities.evaluate_modulus_10_50()` (strain- or stress-based interval)
  and `solver_utilities.evaluate_modulus_e005_e025()`.

## Changed

- Renamed the `TanOpenHole` model input `grid_size` to `grid_resolution` (same
  meaning: number of grid points per direction) to remove the ambiguity with a
  grid spacing.
- `PostProcessor._run` is now generic: it handles the faulty-run logic from the
  `_is_run_faulty()` and `_can_postprocess()` hooks, and delegates the actual
  postprocessing to `_postprocess()`, which subclasses implement instead of `_run`.
- `PostProcessor.evaluate_modulus_10_50()` and `evaluate_modulus_e005_e025()` are
  removed, use their `solver_utilities` counterparts. The `Modulus1050` and
  `ModulusE005E025` direct measures use them too.

## Fixed

- None
