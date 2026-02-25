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

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from numpy import atleast_1d

from vimseo.core.components.external_software_component import ExternalSoftwareComponent
from vimseo.core.model_metadata import MetaDataNames
from vimseo.job_executor.base_executor import BaseJobExecutor
from vimseo.job_executor.base_user_job_options import BaseUserJobSettings

if TYPE_CHECKING:
    from vimseo.core.components.subroutines.subroutine_wrapper import SubroutineWrapper

LOGGER = logging.getLogger(__name__)

class RunProcessor(ExternalSoftwareComponent):
    """Class defining library of components dedicated to running models.

    _run method to be overloaded.
    """

    subroutine_list: list[SubroutineWrapper]
    """A list of subroutines."""

    def __init__(self, **options):
        """
        Args:
            material: The material.
        """
        super().__init__(**options)
        self.subroutine_list = []

    @property
    def n_cpus(self):
        """The number of CPUs used to run the external software."""
        return self._job_executor.options["n_cpus"]
    
    def write_input_files(self, input_data):
        """Write the input files for the external software."""
        pass

    def pre_run(self, input_data):
        """Pre-run operations."""
        pass

    def post_run(self, input_data):
        """Post-run operations."""
        pass

    def _run(self, input_data):
        """Run the external software."""

        self.pre_run(input_data)

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
        output_data[MetaDataNames.error_code] = atleast_1d(error_run)

        self.post_run(input_data, output_data)

        return output_data