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
from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar

import subprocess

from numpy import atleast_1d
from numpy import atleast_2d
from numpy import loadtxt
from vimseo.config.global_configuration import _configuration as config
from vimseo.core.base_integrated_model import IntegratedModel
from vimseo.core.base_integrated_model import IntegratedModelSettings
from vimseo.core.components.component_factory import ComponentFactory
from vimseo.core.components.external_software_component import ExternalSoftwareComponent
from vimseo.core.model_metadata import MetaDataNames
from vimseo.job_executor.base_executor import BaseJobExecutor
from vimseo.job_executor.job_executor_factory import JobExecutorFactory
from vimseo.material.material import Material
from vimseo.utilities.curves import Curve
from vimseo.utilities.file_utils import wait_for_file

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Mapping
    from collections.abc import Sequence

LOGGER = logging.getLogger(__name__)

DEFAULT_INPUT_DATA = {
    "E": atleast_1d(70000.0),
    "nu": atleast_1d(0.3),
    "sigma_y_0": atleast_1d(250.0),
    "sigma_y_u": atleast_1d(350.0),
    "delta": atleast_1d(100.1),
}


couette_ini = """
[backend]
precision = double

[constants]
gamma = 1.4
mu = 0.417
Pr = 0.72

cp = 1005.0
Uw = 70
Pc = 100000.0
Tw = 300.0

[solver]
system = navier-stokes
order = 2

[solver-time-integrator]
scheme = rk4
controller = none
tstart = 0.0
tend = 4
dt = 0.00004

[solver-interfaces]
riemann-solver = rusanov
ldg-beta = 0.5
ldg-tau = 0.1

[solver-interfaces-line]
flux-pts = gauss-legendre

[solver-elements-tri]
soln-pts = williams-shunn

[solver-elements-quad]
soln-pts = gauss-legendre

[soln-plugin-nancheck]
nsteps = 50

[soln-plugin-writer]
dt-out = 0.4
basedir = .
basename = couette-flow-{n:03d}

[soln-bcs-bcwallupper]
type = no-slp-isot-wall
cpTw = cp*Tw
u = Uw

[soln-bcs-bcwalllower]
type = no-slp-isot-wall
cpTw = cp*Tw

[soln-ics]
rho = 4*(Pc*sqrt(Pr*(Pr*Uw*Uw+8*cp*Tw))*log((sqrt(Pr*(Pr*Uw*Uw+8*cp*Tw))+Pr*Uw)/(sqrt(Pr*(Pr*Uw*Uw+8*cp*Tw))-Pr*Uw))*gamma)/(Pr*Uw*(Pr*Uw*Uw+8*cp*Tw)*(gamma-1))
u = Uw
v = 0.0
p = Pc
"""

Path("couette-flow.ini").write_text(couette_ini)

class Couette2DRun_Dummy(ExternalSoftwareComponent):
    USE_JOB_DIRECTORY = True

    auto_detect_grammar_files = False
    default_grammar_type = "SimpleGrammar"
    default_cache_type = "SimpleCache"

    def __init__(self, **options):
        super().__init__(**options)
        self.output_grammar.update_from_data({
            MetaDataNames.error_code.name: atleast_1d(0),
        })

        self._job_executor = JobExecutorFactory().create(
            "BaseInteractiveExecutor", 
            "pyfr run -b cuda couette-flow.pyfrm couette-flow.ini"
        )

    def _run(self, input_data):

        is_empty = not any(self.job_directory.iterdir())
        if not is_empty:
            msg = f"{self.job_directory} should be empty."
            raise ValueError(msg)

        # Prepare Input.txt file
        content = Path("couette-flow.ini").read_text()
        # template = Path(PAOLO_MODEL_DIR / "input.txt").read_text()
        # input_str = BaseJobExecutor._render_template(
        #     template,
        #     {"input_values": [value[0] for value in input_data.values()]},
        # )
        Path(self.job_directory / "couette-flow.ini").write_text(content)

        subprocess.run(
            "wget couette-flow.msh https://github.com/PyFR/PyFR-Test-Cases/raw/main/2d-couette-flow/couette-flow.msh".split(),
            cwd=self._job_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        subprocess.run(
            "pyfr import couette-flow.msh couette-flow.pyfrm".split(),
            cwd=self._job_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
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
        for i, file in enumerate(files):
            suffix = file.split("-")[-1]
            suffix = suffix.split(".pyfrs")[0]
            pyfrm_file = "couette-flow.pyfrm"
            vtu_file = f"solution_couette-flow_{suffix}.vtu"
            print(f"Conversion de {file} en format VTU dans {vtu_file}")
            subprocess.run(
                f"pyfr export volume {pyfrm_file} {file} {vtu_file}".split(),
                cwd=self._job_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print("Conversion terminée.")

        output_data = {}

        output_data[MetaDataNames.error_code] = atleast_1d(error_run)

        return output_data

    def __load_curve(self, file_path: Path, output_name: str) -> Curve:
        data = loadtxt(file_path)
        return Curve({"pseudo_time": data[:, 0], output_name: data[:, 1]})

    def _check_job_completion(
        self,
    ) -> int:
        """Check job completion by reading the last pseudo-time."""
        result_file_path = self.job_directory / "couette-flow-040.pyfrs"
        wait_for_file(result_file_path)
        return 0


class Couette2DModel(IntegratedModel):
    """A research CFD model of 2D Couette flow solved by PyFR."""

    default_cache_type = "SimpleCache"
    default_grammar_type = "SimpleGrammar"

    FIELDS_FROM_FILE: ClassVar[Mapping[str, str]] = {
        "solution": r"^euler-vortex-+\d\.pyfrs$"
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
