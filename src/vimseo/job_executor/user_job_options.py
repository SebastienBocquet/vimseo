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

"""The user job options for all job executors."""

from __future__ import annotations

from pydantic import Field

from vimseo.job_executor.base_user_job_options import BaseUserJobSettings


class InteractiveAbaqusUserJobSettings(BaseUserJobSettings):
    """The user options for an Abaqus interactive job."""

    is_implicit: bool = True
    subroutine_names: list[str] = Field(default_factory=lambda: [""])
    abaqus_script: str = ""
    convergence_sources: list[str] = Field(
        default_factory=lambda: ["sta", "msg"],
        description="The extensions of the '<job_name>.<ext>' solver files whose new "
        "lines are surfaced into the log (e.g. 'sta', 'msg', 'dat').",
    )
    convergence_live_tail: bool = Field(
        default=True,
        description="Whether to surface convergence lines during the solve (throttled), "
        "and not only once the solver has exited.",
    )
    convergence_msg_filter: bool = Field(
        default=True,
        description="Whether to keep only the significant lines of the '.msg' file "
        "(warnings, errors, non-convergence, cut-backs, attempts) rather than its "
        "whole content.",
    )


class SlurmAbaqusUserJobSettings(BaseUserJobSettings):
    """The user options for an Abaqus job submitted through Slurm."""

    max_wall_clock_time: int = Field(
        default=1, description="The maximum wall clock time in hours."
    )
    job_type: str = Field(
        default="mono", description="The job type, among 'mono', 'noeud', 'mesca'."
    )
