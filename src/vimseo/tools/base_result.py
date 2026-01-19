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

import json
import logging
import pickle
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path

from docstring_inheritance import GoogleDocstringInheritanceMeta

from vimseo.tools.metadata import ToolResultMetadata

LOGGER = logging.getLogger(__name__)


@dataclass
class BaseResult(metaclass=GoogleDocstringInheritanceMeta):
    """A result of a tool (:class:`.BaseTool`).

    This result is the object that flows through a workflow of tools.
    It is self-supporting and carries information on how to process it through the
    :attr:`.ToolResultMetadata.settings`. The result can be written on disk in binary format
    (``pickle``) and its metadata can also be written on disk in a readable format
    (``json``).
    """

    metadata: ToolResultMetadata | None = None
    """ToolResultMetadata attached to a result."""

    def to_pickle(self, file_path):
        """Save result instance to disk."""
        file_path = f"{file_path}.pickle"
        with Path(file_path).open("wb") as f:
            pickle.dump(self, f)

    # TODO move to BaseTool such that it can be exported to the working directory
    def save_metadata_to_disk(self, file_path: Path | str = ""):
        """Save metadata to disk in a readable format."""
        file_path = Path.cwd() if file_path == "" else Path(file_path)
        with Path(file_path / f"{self.__class__.__name__}_metadata.json").open(
            "w"
        ) as f:
            json.dump(asdict(self.metadata), f, indent=4, ensure_ascii=True)

    def __post_init__(self):
        self.metadata = ToolResultMetadata()
