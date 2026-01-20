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

from typing import TYPE_CHECKING
from typing import Any

from vimseo.io.io_factory import IOFactory
from vimseo.tools.base_tool import BaseTool
from vimseo.tools.io.base_reader_file import BaseReaderFile
from vimseo.tools.io.base_reader_file import BaseReaderFileSettings
from vimseo.tools.io.base_reader_file import StreamlitBaseReaderFileSettings
from vimseo.tools.tool_results_factory import ToolResultsFactory

if TYPE_CHECKING:
    from vimseo.tools.base_result import BaseResult


class ReaderFileToolResult(BaseReaderFile):
    results: BaseResult

    _SETTINGS = BaseReaderFileSettings

    _STREAMLIT_SETTINGS = StreamlitBaseReaderFileSettings

    def __init__(
        self,
        tool_name: str,
    ):
        super().__init__()
        self.__tool_name = tool_name
        self.__io = IOFactory().create(f"{tool_name}FileIO")
        self.result = ToolResultsFactory().create(tool_name)

    def get_file_extension(self):
        return self.__io._EXTENSION

    @property
    def io(self):
        return self.__io

    # TODO not necessary, since all tools are supported. Use AnalysisToolsFactory instead
    @classmethod
    def get_tool_names(cls):
        tmp = [
            name.split("FileIO")[0]
            for name in IOFactory().class_names
            if "FileIO" in name
        ]
        tmp.remove("BaseTool")
        return tmp

    @BaseTool.validate
    def execute(
        self,
        settings: BaseReaderFileSettings | None = None,
        **options,
    ) -> Any:
        self.result = self.__io.read(
            file_name=options["file_name"],
            directory_path=options["directory_path"],
        )
