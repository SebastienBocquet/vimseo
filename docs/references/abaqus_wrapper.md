<!--
 Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

## Abaqus wrapper {#abaqus_wrapper}

VIMSEO proposes a wrapper dedicated to Abaqus models. It
is built on the following mechanisms:

The pre-processor:
  - generates a unique job directory in the current working directory.
  - writes a file called `job_arguments.json` in the job directory
    containing the input data for the pre-processing script.
  - executes a script file with Abaqus CAE. The script file must be
    contained in the VIMSEO package, typically under
    the `lib_vims` directory. (or plugin package in case of a plugin).
    The path to the script file is defined by: - The name of the
    package (class attribute `_PACKAGE_NAME`) - the path to the
    directory containing the script, relative to the package root
    (class attribute `_LIBRARY_DIR_NAME`). - the name of the script
    file (class attribute `_ABAQUS_SCRIPT`).

The run component executes a subprocess with the command line
defined in the configuration file (typically a text file with
extension `.config` in the working directory). This class is
expected to be generic. Only the command line to launch Abaqus is
specific.

The post-processor:
  - executes a script file with Abaqus CAE. The same attributes as in
    pre-processor are used to define its path. The script file must
    write a `job_outputs.csv` or `job_outputs.json` file containing
    the output data.

  - Reads the job output file and fills the output data of the
    post-processor.

    !!! note

        Monitoring variables (see class attribute MONITORING_VARIABLES of
        `vimseo.core.base_integratde_model.BaseIntegratedModel`{.interpreted-text role="class"}) are
        automatically added to the output grammar of the post-processor
        and model. It is the responsability of the post-processor to set
        the value of `ERROR_CODE` in the output data.

The model orchestrates the successive executions of these three
components.
