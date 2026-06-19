# Copyright 2021 IRT Saint Exupery, https://www.irt-saintexupery.com
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

from __future__ import annotations

import logging
from argparse import ArgumentParser
from pathlib import Path

from vimseo.api import activate_logger
from vimseo.api import create_model
from vimseo.core.model_settings import IntegratedModelSettings

LOGGER = logging.getLogger(__name__)

parser = ArgumentParser(
    prog="Model run executor",
    description="Execute the run-processor of a model.",
)
parser.add_argument(
    "-m",
    "--model_name",
    type=str,
    default="",
    help="The model name.",
)
parser.add_argument(
    "-l",
    "--load_case_name",
    type=str,
    default="",
    help="The load case name.",
)
parser.add_argument(
    "-j",
    "--job_name",
    type=str,
    default="",
    help="The job name (for a prepared inp file job_1.inp, the job name if job_1).",
)
parser.add_argument(
    "-d",
    "--dir_path",
    type=str,
    default="",
    help="The directory containing the model pre-processing.",
)
parser.add_argument(
    "-n",
    "--n_cpus",
    type=int,
    default=0,
    help="The number of CPUs to use. To specify other job options, copy the config file"
    "(`vimseo_abaqus/docs/configuration_examples/`)"
    " and directly modify the run command line.",
)


def model_run_executor(
    model_name: str, load_case_name: str, job_name: str, dir_path: str, n_cpus: int
):
    """Execute the run-processor of a model."""
    model = create_model(
        model_name,
        load_case_name,
        IntegratedModelSettings(job_name=job_name.split("job_")[-1]),
    )
    if n_cpus == 0:
        n_cpus = model.N_CPUS
    model._chain.disciplines[1]._job_directory = Path(dir_path)
    model.run.job_executor.set_options(
        model.run._job_executor._USER_JOB_OPTIONS_MODEL(n_cpus=n_cpus)
    )
    model._chain.disciplines[1].execute({"error_pre": 0})


def main():
    activate_logger()
    arguments = vars(parser.parse_args())
    model_run_executor(
        arguments["model_name"],
        arguments["load_case_name"],
        arguments["job_name"],
        arguments["dir_path"],
        arguments["n_cpus"],
    )


if __name__ == "__main__":
    main()
