# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Copyright (c) 2019 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: XXXXXXXXXXX
#    OTHER AUTHORS   - MACROSCOPIC CHANGES

# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar

from gemseo.core.grammars.pydantic_grammar import PydanticGrammar
from gemseo.utils.pydantic_ndarray import NDArrayPydantic
from numpy import array
from numpy import atleast_1d
from numpy import linspace
from pydantic import BaseModel

from vimseo.core.base_integrated_model import IntegratedModel
from vimseo.core.base_integrated_model import IntegratedModelSettings
from vimseo.core.components.component_factory import ComponentFactory
from vimseo.core.components.external_software_component import ExternalSoftwareComponent
from vimseo.job_executor.base_executor import BaseJobExecutor
from vimseo.job_executor.job_executor_factory import JobExecutorFactory
from vimseo.problems.cfd.couette_2d import COUETTE_2D_DIR
from vimseo.problems.cfd.couette_2d.generate_mesh import generate_couette_mesh
from vimseo.utilities.fields import extract_line_y
from vimseo.utilities.file_utils import wait_for_file

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence

LOGGER = logging.getLogger(__name__)

DEFAULT_INPUT_DATA = {
    "mu": atleast_1d(0.417),
    "prandtl": atleast_1d(0.72),
    "cp": atleast_1d(1005.0),
    "dt": atleast_1d(4e-5),
    "dx": atleast_1d(0.25),
    "u_w": atleast_1d(70.0),
}


class Couette2DInputGrammar(BaseModel):
    """The input grammar for the Couette 2D model."""

    mu: NDArrayPydantic[float]
    prandtl: NDArrayPydantic[float]
    cp: NDArrayPydantic[float]
    dt: NDArrayPydantic[float]
    dx: NDArrayPydantic[float]
    u_w: NDArrayPydantic[float]


class Couette2DOutputGrammar(BaseModel):
    """The output grammar for the Couette 2D model."""


class Couette2DRun_Dummy(ExternalSoftwareComponent):
    USE_JOB_DIRECTORY = True

    _PERSISTENT_FILE_NAMES: ClassVar[Sequence[str]] = [
        f"couette-flow-{int(t):03d}_{field}.png"
        for field in ["Velocity", "Density"]
        for t in linspace(0, 9, num=10)
    ]

    auto_detect_grammar_files = False
    default_grammar_type = "PydanticGrammar"
    default_cache_type = "SimpleCache"

    def __init__(self, **options):
        super().__init__(**options)

        self.input_grammar = PydanticGrammar("grammar", model=Couette2DInputGrammar)
        self.output_grammar = PydanticGrammar("grammar", model=Couette2DOutputGrammar)

        self.output_grammar.update_from_data({"error_code": atleast_1d(0)})
        # self.output_grammar.required_names.add("error_code")

        line_data = {}
        # for t in linspace(0, 10, num=11):
        for t in linspace(0, 9, num=10):
            for field in ["velocity_0", "velocity_1", "density", "pressure"]:
                line_data[f"line_{field}_{int(t):03d}"] = array([0.0])

        line_data["line_y"] = array([0.0])
        line_data["line_distance"] = array([0.0])
        self.output_grammar.update_from_data(line_data)
        for name in line_data:
            self.output_grammar.required_names.add(name)

        self.default_input_data = DEFAULT_INPUT_DATA

        self._job_executor = JobExecutorFactory().create(
            "BaseInteractiveExecutor",
            "pyfr run -b {{ backend }} couette-flow.pyfrm couette-flow.ini",
        )

    def _run(self, input_data):

        is_empty = not any(self.job_directory.iterdir())
        if not is_empty:
            msg = f"{self.job_directory} should be empty."
            raise ValueError(msg)

        generate_couette_mesh(
            mesh_size=input_data["dx"][0],
            output=str(self.job_directory / "couette-flow.msh"),
        )

        template = Path(COUETTE_2D_DIR / "couette_2d.ini.j2").read_text()
        input_str = BaseJobExecutor._render_template(
            template,
            {key: value[0] for key, value in input_data.items()},
        )
        Path(self.job_directory / "couette-flow.ini").write_text(input_str)

        subprocess.run(
            ["pyfr", "import", "couette-flow.msh", "couette-flow.pyfrm"],
            cwd=self._job_directory,
            capture_output=True,
        )

        self._job_executor._set_job_options(
            self.job_directory,
        )
        error_run = self._job_executor.execute(
            check_subprocess=self._check_subprocess,
        )
        if error_run:
            LOGGER.warning(
                f"An error has occurred in {self.__class__.__name__}, "
                f"running command {self._job_executor._command_line}."
            )

        error_run = 0
        error_run = self._check_subprocess_completion(
            error_run, self._check_subprocess, self._job_executor.command_line.split()
        )

        if error_run:
            LOGGER.warning(
                f"An error has occurred in {self.__class__.__name__}, "
                f"in check subprocess completion."
            )

        output_data = {}

        # Mapping name from PyFR to name in grammar:
        mapping = {
            "Velocity": "velocity",
            "Density": "density",
            "Pressure": "pressure",
        }

        files = Path.glob(f"{self.job_directory}/*.pyfrs")
        print(f"Found pyfrs files: {files}.")
        for i, file in enumerate(files):
            suffix = file.split("-")[-1]
            suffix = suffix.split(".pyfrs")[0]
            pyfrm_file = "couette-flow.pyfrm"

            # # temp
            # vtu_file = file
            # suffix = suffix.replace(".vtu", "")
            # # ----

            vtu_file = file.replace(".pyfrs", ".vtu")
            print(f"Conversion de {file} en format VTU dans {vtu_file}")
            pyfrs_filename = Path(file).name
            vtu_filename = Path(vtu_file).name
            subprocess.run(
                f"pyfr export {pyfrm_file} {pyfrs_filename} {vtu_filename}".split(),
                cwd=self._job_directory,
                capture_output=True,
            )
            print("Conversion terminée.")

            line = extract_line_y(
                vtu_file=vtu_file,
                x_probe=0.0,
                n_points=200,
                fields=["Velocity", "Density", "y", "Distance", "Pressure"],
            )

            # Store constant data only for first file:
            if i == 0:
                output_data["line_y"] = line["y"]
                output_data["line_distance"] = line["Distance"]

            for field, mapped_field in mapping.items():
                if field == "Velocity":
                    # On suppose que Velocity est un champ vectoriel, et on prend sa composante x
                    for i in range(2):
                        output_data[f"line_{mapped_field}_{i}_{suffix}"] = line[field][
                            :, i
                        ]
                else:
                    output_data[f"line_{mapped_field}_{suffix}"] = line[field]

            # vtu_to_png([vtu_file], output_folder=self.job_directory, scalar_name="Velocity", clim=(0, 70))
            # vtu_to_png([vtu_file], output_folder=self.job_directory, scalar_name="Density", clim=(0, 1.2))

        output_data["error_code"] = atleast_1d(error_run)

        return output_data

    def _check_job_completion(
        self,
    ) -> int:
        """Check job completion by reading the last pseudo-time."""
        result_file_path = self.job_directory / "couette-flow-010.pyfrs"
        try:
            wait_for_file(result_file_path)
        except FileNotFoundError:
            return 1
        else:
            return 0


class Couette2DModel(IntegratedModel):
    """A research CFD model of 2D Couette flow solved by PyFR."""

    default_cache_type = "SimpleCache"
    default_grammar_type = "PydanticGrammar"

    FIELDS_FROM_FILE: ClassVar[Mapping[str, str]] = {
        "solution": r"^couette-flow-+\d+\.vtu$"
    }

    CURVES: ClassVar[Sequence[tuple[str]]] = [
        ("line_y", "line_density_009"),
        ("line_y", "line_velocity_0_009"),
        ("line_y", "line_velocity_1_009"),
        ("line_y", "line_pressure_009"),
    ]

    def __init__(self, load_case_name: str, **options):
        options = IntegratedModelSettings(**options).model_dump()
        super().__init__(
            load_case_name,
            [
                ComponentFactory().create(
                    "Couette2DRun",
                    load_case_name,
                    check_subprocess=options["check_subprocess"],
                )
            ],
            **options,
        )
