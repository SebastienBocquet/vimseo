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

from json import dumps

from gemseo.utils.string_tools import MultiLineString
from pydantic import BaseModel
from pydantic import ConfigDict

from vimseo.utilities.json_grammar_utils import EnhancedJSONEncoder

DEFAULT_MIN_MAX = 1e12


class DistributionSettings(BaseModel):
    """Generic settings shared across the distribution kinds handled by vimseo.

    Stock gemseo (>=6.2) only ships one pydantic settings model per distribution
    class (e.g. ``OTNormalDistribution_Settings``); this generic model lets
    vimseo's UI/JSON space definitions stay distribution-agnostic, as it used to
    be with the private gemseo fork this class was ported from.
    """

    ConfigDict(extra="forbid")

    name: str
    mode: float | list[float] = 0.0
    lower: float | list[float] = -DEFAULT_MIN_MAX
    upper: float | list[float] = DEFAULT_MIN_MAX
    sigma: float | list[float] = 0.0
    mu: float | list[float] = 1.0
    mean: float | list[float] = 0.0
    loc: float | list[float] = 0.0
    location: float | list[float] = 0.0
    shape: float | list[float] = 1.0
    scale: float | list[float] = 1.0
    rate: float | list[float] = 1.0
    lower_bound: float | list[float] | None = None
    upper_bound: float | list[float] | None = None


class InterfacedDistributionSettings(BaseModel):
    """Settings to define a distribution interfaced from a third-party library."""

    ConfigDict(extra="forbid")

    name: str
    parameters: tuple = ()
    lower_bound: float | None = None
    upper_bound: float | None = None


class DistributionParameters(DistributionSettings):
    """Parameters representing a distribution."""

    ConfigDict(extra="forbid")

    name: str = ""

    def __str__(self):
        text = MultiLineString()
        text.indent()
        text.add(self.name)
        text.indent()
        text.indent()
        text.add("Parameters:")
        text.add(
            dumps(self.model_dump(), sort_keys=True, indent=10, cls=EnhancedJSONEncoder)
        )
        text.dedent()
        text.dedent()
        text.dedent()
        return str(text)
