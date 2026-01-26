<!--
 Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

# Integration of models {#integration_of_model}

## Abaqus models

Consider a user that has developed an Abaqus model, containing:

- a pre-processing CAE python scripts that is already parametric
  (some input values can be changed to modify the meshing)
- a post-processing CAE python script that reads the ODB file and
  processes some final output data.

Then the integration of such a model in VIMSEO can be
done as following. Note that the same procedure applies for plugins,
typically `vimseo-composites`

### Abaqus CAE scripts

Create a new directory in `vimseo.lib_vims.new_model`. Add an empty
`__init__.py` file in this directory. Copy your Abaqus scripts in this
directory, and rename the files into: - script_preproc_new_model.py -
script_postproc_new_model.py

#### Pre-processing

VIMSEO Abaqus wrapper will write a `json` file containing
the values of `i1` and `i2` to be used in your pre-processing script.
Thus, at the beginning of your pre-processing script, you may paste the
following lines:

```
import abaqus_utilities as utils

file_job_inputs = utils.ARG_FILE
dico = utils.import_json_inputs(file_job_inputs)

inp_name = dico['job_name']  # Name of the INP file to create (without .inp)
i1 = dico['i1']
```

Then `i1` can be used as an input variable in your original script.

!!! note

    You can print information about the script by using the following
    utility: `utils.printAll('My information\n')`

#### Post-processing

In principle, your post-processing script already loads Abaqus ODB data
and processes it to extract useful Quantities of Interest. Then, these
values should be given to the post-processor of Abaqus
VIMSEO wrapper. A utility is dedicated to this task, and
can be used by pasting the following lines at the end of your script:

```
import abaqus_utilities as utils

dico_vims_output = {}
dico_vims_output['o1'] = ...
dico_vims_output['o2'] = ...

utils.write_json_dict(utils.OUT_FILE, dico_vims_output)
```

### VIMSEO Python part

First, new classes must be added in VIMSEO. The easiest
way is to start by duplicating an existing model. The EOMS UMAT model is
interesting because it is a simple model with a subroutine.

We assume the new model is called `NewModel` and has a load case called
`LC1`, and has inputs `i1`, `i2` and outputs `o1`, `o2`. We also
consider that the load case is associated to a specific domain, which
allows to avoid clashes in load case names. We assume the domain is
called `NewDomain`.

Create a new directory in `vimseo/problems`, for instance
`vimseo/problems/new_model` Add empty files: - \_\_init\_\_.py -
pre_new_model.py - post_new_model.py - new_model.py in this directory.

Also create an empty file `new_domain.py` in `vimseo/problems/load_cases`.

Then:

- paste the following code in
  `vimseo/problems/load_cases/new_domain.py`:

  ```
  from __future__ import annotations

  from dataclasses import dataclass

  from vimseo.core.load_case import LoadCase


  @dataclass
  class LC1(LoadCase):
      """An LC1 load case."""
  ```

- Paste the following code in `pre_new_model.py`:

  ```
  from __future__ import annotations
  from numpy import array
  from vimseo.wrapper.abaqus.pre_abaqus_wrapper import PreAbaqusWrapper
  from vimseo.wrapper.abaqus.utilities import LibraryFile


  class PreNewModel_LC1(PreAbaqusWrapper):
      """Pre-processor for model ``NewModel``."""

      _ABAQUS_SCRIPT = LibraryFile(
          file_path="new_model/script_preproc_new_model.py"
      )

      def __init__(self, **options):
          super().__init__(**options)
          self.default_inputs.update(
              {
                  "i1": array([1.0]),
                  "i2": array([2.0]),
              }
          )
  ```

- Paste the following code in `post_new_model.py`:

  ```
  from __future__ import annotations

  from vimseo.wrapper.abaqus.post_abaqus_wrapper import PostAbaqusWrapper
  from vimseo.wrapper.abaqus.utilities import LibraryFile


  class PostNewModel_LC1(PostAbaqusWrapper):
      """Post-process analysis of model ``NewModel``."""

      JOB_OUTPUT_FORMAT = "json"
      _ABAQUS_SCRIPT = LibraryFile(
          file_path="new_model/script_postproc_new_model.py"
      )
  ```

- Paste the following code in `new_model.py`:

  ```
  class NewModel(IntegratedModel):
      """A new model based on Abaqus."""

      SUMMARY = (
          "Describe the model."
      )

      # If the model has input variables that control its numerical behaviour
      # (mesh size, number of time steps etc...), indicate their names here.
      NUMERICAL_VARIABLE_NAMES = []

      PRE_PROC_FAMILY = "PreNewModel"

      # Use "RunAbaqusWrapper_Explicit" if the model uses Abaqus explicit.
      # Otherwise, Abaqus implicit considered.
      RUN_FAMILY = "RunAbaqusWrapper_Implicit"

      # TODO
      SUBROUTINES_NAMES = []

      # This variable defines the material grammar.
      # It is not the material values. The grammar defines the name and the type
      # of the material properties. The bounds of the properties can also be defined.
      # The values are defined in the variable ``MATERIAL_FILE``.
      # For a simple isotropic elastic material,
      # the existing ``Ta6v`` material can be used.
      # If a more complex is to be used, then you can have a look
      # at the EOMS material (orthotropic elastic max-stress material).
      # You can also write your own grammar.

      _MATERIAL_GRAMMAR_FILE = MATERIAL_LIB_DIR / "Ta6v_grammar.json"

      # The material property values are defined in this file.
      # Note that probability distributions of the material properties
      # can also be defined.
      # Unspecified distributions are defined like this:
      # "distribution":{"name":"","mode":0.0,"minimum":-1000000000000.0,"maximum":1000000000000.0,"sigma":0.0,"mu":1.0,"lower_bound":100000.0,"upper_bound":150000.0,"parameters":[]}
      # The Ta6v defines Normal distributions.
      # The EOMS material does not defines distributions.
      # You can pick-up in these two examples to define your material values.
      MATERIAL_FILE = MATERIAL_LIB_DIR / "Ta6v.json"

      POST_PROC_FAMILY = "PostNewModel"

      N_CPUS = 1

      _LOAD_CASE_DOMAIN = "NewDomain"
  ```

#### Abaqus commands under Windows

To specify the Abaqus commands for pre/post and run under Windows, the
absolute path to the `.bat` abaqus executable must be prescribed. For
this path: `C:\Users\Public\docker_abaqus\abq2022.bat`, then the
following commands must be prescribed:

```
"CMD_ABAQUS_CAE": "C:/Users/Public/docker_abaqus/abq2022.bat cae noGUI={{abaqus_script}}",
"CMD_ABAQUS_RUN": "C:/Users/Public/docker_abaqus/abq2022.bat job={{job_name}} cpus={{n_cpus}}{% if subroutine_names|length > 0 %} user={{subroutine_names[0]}}{% endif %} {% if is_implicit == False %} double=both {% endif %}inter",
```

Note that the blackslahes must be slashes in the command path, and that
the `.bat` suffix must be kept.
