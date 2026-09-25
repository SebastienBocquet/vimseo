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

"""The archive of the results of the tools."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from docstring_inheritance import GoogleDocstringInheritanceMeta

if TYPE_CHECKING:
    from vimseo.tools.base_result import BaseResult


class BaseToolArchive(metaclass=GoogleDocstringInheritanceMeta):
    """A base class for the archive of the results of the tools.

    The life of a tool run in the archive is:

    1. :meth:`start_tool_run`, before the tool is executed, so that the simulations
       it launches can be attached to the run,
    2. :meth:`publish_tool_result`, when the tool succeeded, or
       :meth:`end_tool_run` with the status ``"FAILED"`` when it raised.

    The identifiers are the ones described in :mod:`vimseo.core.run_context`: a tool
    run is identified by ``tool_run_id``, and its result lists the ``run_id`` of the
    simulations it used.

    The methods are prefixed by ``tool`` because an archive of tool results can also
    be a model archive (see :class:`.DirectoryToolArchive`).
    """

    STATUS_FINISHED = "FINISHED"
    """The status of a tool run whose result was published."""

    STATUS_FAILED = "FAILED"
    """The status of a tool run which raised."""

    STATUS_RUNNING = "RUNNING"
    """The status of a tool run which has started."""

    @abstractmethod
    def start_tool_run(
        self, tool_name: str, tool_run_id: str, parent_run_id: str = ""
    ) -> None:
        """Start the archive of a tool run.

        Args:
            tool_name: The name of the tool.
            tool_run_id: The unique identifier of the tool run.
            parent_run_id: The identifier of the run of the tool executing this tool.
        """

    @abstractmethod
    def publish_tool_result(self, result: BaseResult) -> None:
        """Publish the result of the current tool run.

        Args:
            result: The result of the tool.
        """

    @abstractmethod
    def end_tool_run(self, status: str, error: str = "") -> None:
        """End the current tool run without a result.

        Args:
            status: The status of the run.
            error: The message of the error which ended the run, if any.
        """

    @abstractmethod
    def get_tool_result(self, tool_run_id: str, tool_name: str = "") -> BaseResult:
        """Return an archived tool result.

        Args:
            tool_run_id: The unique identifier of the tool run.
            tool_name: The name of the tool. If empty, all the tools are searched.

        Raises:
            KeyError: If there is no archived result for this tool run.
        """

    @abstractmethod
    def search_tool_runs(
        self, tool_name: str = "", status: str = ""
    ) -> list[dict[str, object]]:
        """Search the archived tool runs.

        Args:
            tool_name: The name of the tool. If empty, all the tools are searched.
            status: The status of the runs. If empty, all the runs are returned.

        Returns:
            A summary of each run, without its result: ``tool_run_id``,
            ``tool_name``, ``status``, ``result_class``, ``datetime``,
            ``parent_run_id``, ``child_tool_run_ids``, ``simulation_run_ids``,
            ``settings``...
        """

    @abstractmethod
    def find_tool_runs_of_simulation(self, simulation_run_id: str) -> list[str]:
        """Return the tool runs which used a simulation.

        A simulation retrieved from the model cache is used by all the tool runs
        which got it, not only by the one which created it.

        Args:
            simulation_run_id: The ``run_id`` of the simulation.

        Returns:
            The ``tool_run_id`` of the runs.
        """


class NullToolArchive(BaseToolArchive):
    """An archive which archives nothing, to disable the archive of tool results."""

    def start_tool_run(
        self, tool_name: str, tool_run_id: str, parent_run_id: str = ""
    ) -> None:
        """Do nothing."""

    def publish_tool_result(self, result: BaseResult) -> None:
        """Do nothing."""

    def end_tool_run(self, status: str, error: str = "") -> None:
        """Do nothing."""

    def get_tool_result(self, tool_run_id: str, tool_name: str = "") -> BaseResult:
        msg = "The archive of the tool results is disabled."
        raise KeyError(msg)

    def search_tool_runs(
        self, tool_name: str = "", status: str = ""
    ) -> list[dict[str, object]]:
        return []

    def find_tool_runs_of_simulation(self, simulation_run_id: str) -> list[str]:
        return []
