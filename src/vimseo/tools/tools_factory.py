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

from gemseo.core.base_factory import BaseFactory

from vimseo.tools.base_analysis_tool import BaseAnalysisTool
from vimseo.tools.base_tool import BaseTool

LOGGER = logging.getLogger(__name__)


class ToolsFactory(BaseFactory):
    """A factory to create a tools from a name or a class."""

    _CLASS = BaseTool
    _PACKAGE_NAMES = ("vimseo.tools",)

    def create(
        self,
        name: str,
        **options,
    ) -> BaseTool:
        """Create an analysis tool.

        Args:
            name: The name of the analysis tool (its class name).
            **options: The options of the analysis tool.
        """
        return super().create(name, **options)


class AnalysisToolsFactory(ToolsFactory):
    """A factory to create analysis tools from a name or a class."""

    _CLASS = BaseAnalysisTool
    _PACKAGE_NAMES = ("vimseo.tools",)

    def create(
        self,
        name: str,
        **options,
    ) -> BaseAnalysisTool:
        """Create an analysis tool.

        Args:
            name: The name of the analysis tool (its class name).
            **options: The options of the analysis tool.
        """
        return super().create(name, **options)
