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

"""An archive of the results of the tools in local directories."""

from __future__ import annotations

import json
import logging
from dataclasses import fields
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import vimseo
from vimseo.storage_management.base_storage_manager import PersistencyPolicy
from vimseo.storage_management.directory_storage import DirectoryArchive
from vimseo.storage_management.tool_archive.base_tool_archive import BaseToolArchive
from vimseo.utilities.json_grammar_utils import EnhancedJSONEncoder

if TYPE_CHECKING:
    from vimseo.tools.base_result import BaseResult

LOGGER = logging.getLogger(__name__)


def _to_json_value(value: object) -> object:
    """Convert a value that :mod:`json` cannot encode, without ever failing.

    The settings of a tool can hold any object, like a model.
    """
    try:
        return EnhancedJSONEncoder().default(value)
    except TypeError:
        return repr(value)


class DirectoryToolArchive(DirectoryArchive, BaseToolArchive):
    """An archive of the results of the tools in local directories.

    It reuses the directory management of :class:`.DirectoryArchive`, the archive of
    the simulations, which it derives from: the archive of a tool run is a job
    directory named after the ``tool_run_id``, under the directory of its tool::

        {root_directory}/tools/{tool_name}/{tool_run_id}/
            result.hdf5           # the result, as written by BaseResult.to_hdf5
            result_metadata.json  # a readable summary of the run

    The summary lets the runs be searched without opening any result, and holds the
    links to the simulations (``simulation_run_ids``) and to the other tool runs
    (``parent_run_id``, ``child_tool_run_ids``). The simulations themselves are in
    the archive of their model. A tool run which is still running, or which was
    interrupted, has the status ``"RUNNING"``.

    Most of the methods inherited from :class:`.DirectoryArchive` are meant for the
    simulations, and are not used.
    """

    RESULT_FILE_NAME = "result.hdf5"
    """The name of the file of the result, in the directory of a tool run."""

    SUMMARY_FILE_NAME = "result_metadata.json"
    """The name of the file of the summary, in the directory of a tool run."""

    TOOLS_DIRECTORY_NAME = "tools"
    """The name of the directory, under the root, of the tool runs."""

    def __init__(self, root_directory: Path | str):
        """Create an archive.

        Args:
            root_directory: The root directory of the archive.
        """
        super().__init__(
            PersistencyPolicy.DELETE_NEVER,
            self.TOOLS_DIRECTORY_NAME,
            "",
            root_directory=Path(root_directory),
        )
        self._tool_name = ""
        self._parent_run_id = ""
        self._tool_run_id = ""

    @property
    def _tools_directory(self) -> Path:
        return self._root_directory / self.TOOLS_DIRECTORY_NAME

    def start_tool_run(
        self, tool_name: str, tool_run_id: str, parent_run_id: str = ""
    ) -> None:
        self._tool_name = tool_name
        self._tool_run_id = tool_run_id
        self._parent_run_id = parent_run_id
        self.set_experiment(f"{self.TOOLS_DIRECTORY_NAME}/{tool_name}")
        self.set_run_name(tool_run_id)
        self.create_job_directory()
        self._write_summary(self.STATUS_RUNNING)

    def publish_tool_result(self, result: BaseResult) -> None:
        result.to_hdf5(self._job_directory / self.RESULT_FILE_NAME)
        self._write_summary(self.STATUS_FINISHED, result=result)

    def end_tool_run(self, status: str, error: str = "") -> None:
        self._write_summary(status, error=error)

    def _write_summary(
        self, status: str, result: BaseResult | None = None, error: str = ""
    ) -> None:
        summary = {
            "tool_run_id": self._tool_run_id,
            "tool_name": self._tool_name,
            "status": status,
            "parent_run_id": self._parent_run_id,
            "datetime": datetime.now().isoformat(" "),
            "vimseo_version": vimseo.__version__,
        }
        if error != "":
            summary["error"] = error
        if result is not None:
            summary["result_class"] = type(result).__name__
            summary.update({
                field.name: getattr(result.metadata, field.name)
                for field in fields(result.metadata)
                if field.name not in ("generic", "model", "run_id", "parent_run_id")
            })
            model = result.metadata.model
            summary["model"] = (
                None
                if model is None
                else {"name": model.name, "load_case": model.load_case.name}
            )
        try:
            text = json.dumps(summary, indent=2, default=_to_json_value)
        except TypeError:
            # A key which is not a string, in the settings for example.
            text = json.dumps(summary, indent=2, default=_to_json_value, skipkeys=True)
        (self._job_directory / self.SUMMARY_FILE_NAME).write_text(text)

    def _find_run_directory(self, tool_run_id: str, tool_name: str = "") -> Path:
        pattern = f"{tool_name or '*'}/{tool_run_id}"
        directories = list(self._tools_directory.glob(pattern))
        if len(directories) == 0:
            msg = (
                f"No archived tool run {tool_run_id}"
                f"{f' of tool {tool_name}' if tool_name else ''} "
                f"in {self._tools_directory}."
            )
            raise KeyError(msg)
        return directories[0]

    def get_tool_result(self, tool_run_id: str, tool_name: str = "") -> BaseResult:
        from vimseo.tools.base_tool import BaseTool

        directory = self._find_run_directory(tool_run_id, tool_name)
        path = directory / self.RESULT_FILE_NAME
        if not path.is_file():
            msg = (
                f"The tool run {tool_run_id} has no result: its status is "
                f"{self._read_summary(directory)['status']}."
            )
            raise KeyError(msg)
        return BaseTool.load_results(path)

    @staticmethod
    def _read_summary(directory: Path) -> dict[str, object]:
        return json.loads(
            (directory / DirectoryToolArchive.SUMMARY_FILE_NAME).read_text()
        )

    def search_tool_runs(
        self, tool_name: str = "", status: str = ""
    ) -> list[dict[str, object]]:
        summaries = []
        for path in sorted(
            self._tools_directory.glob(f"{tool_name or '*'}/*/{self.SUMMARY_FILE_NAME}")
        ):
            summary = json.loads(path.read_text())
            if status == "" or summary["status"] == status:
                summaries.append({**summary, "directory": str(path.parent)})
        return summaries

    def find_tool_runs_of_simulation(self, simulation_run_id: str) -> list[str]:
        return [
            summary["tool_run_id"]
            for summary in self.search_tool_runs()
            if simulation_run_id in summary.get("simulation_run_ids", ())
        ]
