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
from numpy import atleast_1d, zeros
from numpy import loadtxt
from pydantic import BaseModel

from vimseo.core.base_integrated_model import IntegratedModel
from vimseo.core.base_integrated_model import IntegratedModelSettings
from vimseo.core.components.component_factory import ComponentFactory
from vimseo.core.components.external_software_component import ExternalSoftwareComponent
from vimseo.core.model_metadata import MetaDataNames
from vimseo.job_executor.base_executor import BaseJobExecutor
from vimseo.job_executor.job_executor_factory import JobExecutorFactory
from vimseo.problems.cfd.couette_2d import COUETTE_2D_DIR
from vimseo.problems.cfd.couette_2d.generate_mesh import generate_couette_mesh
from vimseo.utilities.curves import Curve
from vimseo.utilities.file_utils import wait_for_file

if TYPE_CHECKING:
    from collections.abc import Mapping

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

    u_profile: NDArrayPydantic[float]
    error_code: NDArrayPydantic[int]


class Couette2DRun_Dummy(ExternalSoftwareComponent):
    USE_JOB_DIRECTORY = True

    auto_detect_grammar_files = False
    default_grammar_type = "SimpleGrammar"
    default_cache_type = "SimpleCache"

    def __init__(self, **options):
        super().__init__(**options)

        self.input_grammar = PydanticGrammar("grammar", model=Couette2DInputGrammar)
        self.output_grammar = PydanticGrammar("grammar", model=Couette2DOutputGrammar)

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
        import glob

        files = glob.glob(f"{self.job_directory}/*.pyfrs")
        for file in files:
            suffix = file.split("-")[-1]
            suffix = suffix.split(".pyfrs")[0]
            pyfrm_file = "couette-flow.pyfrm"
            vtu_file = f"solution_couette-flow_{suffix}.vtu"
            print(f"Conversion de {file} en format VTU dans {vtu_file}")
            subprocess.run(
                f"pyfr export volume {pyfrm_file} {file} {vtu_file}".split(),
                cwd=self._job_directory,
                capture_output=True,
            )
            print("Conversion terminée.")

        output_data = {}

        output_data["u_profile"] = zeros((10))
        output_data[MetaDataNames.error_code] = atleast_1d(error_run)

        return output_data

    def __load_curve(self, file_path: Path, output_name: str) -> Curve:
        data = loadtxt(file_path)
        return Curve({"pseudo_time": data[:, 0], output_name: data[:, 1]})

    def _check_job_completion(
        self,
    ) -> int:
        """Check job completion by reading the last pseudo-time."""
        result_file_path = self.job_directory / "couette-flow-010.pyfrs"
        # TODO add a try except to catch the case where the file is not found, 
        # and return an error code in this case
        wait_for_file(result_file_path)
        return 0


class Couette2DModel(IntegratedModel):
    """A research CFD model of 2D Couette flow solved by PyFR."""

    default_cache_type = "SimpleCache"
    default_grammar_type = "SimpleGrammar"

    FIELDS_FROM_FILE: ClassVar[Mapping[str, str]] = {
        "solution": r"^couette-flow_+\d\.pyfrs$"
    }

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
