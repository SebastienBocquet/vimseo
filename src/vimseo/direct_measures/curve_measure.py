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

from abc import abstractmethod
from typing import TYPE_CHECKING

from numpy import abs as np_abs
from numpy import max as np_max
from pydantic import BaseModel

from vimseo.direct_measures.direct_measure import BaseDirectMeasure
from vimseo.lib_vimseo.solver_utilities import local_slope_computation

if TYPE_CHECKING:
    from vimseo.utilities.curves import Curve


class DirectMeasureOnCurveSettings(BaseModel):
    x_name: str
    y_name: str
    measure_name: str


class BaseCurveMeasure(BaseDirectMeasure):
    _SETTINGS_MODEL = DirectMeasureOnCurveSettings

    @abstractmethod
    def compute(self, a: Curve) -> float:
        """An abstract method for computing a direct measure on a curve."""


class ModulusE005E025(BaseCurveMeasure):
    def compute(self, a: Curve) -> float:
        return local_slope_computation(
            a.x, a.y, x_min=0.0005, x_max=0.0025, method="average"
        )


class Modulus1050(BaseCurveMeasure):
    def compute(self, a: Curve) -> float:
        stress = a.y
        max_stress = np_max(np_abs(stress))
        return local_slope_computation(
            a.x,
            stress,
            y_min=0.10 * max_stress,
            y_max=0.50 * max_stress,
            method="regression",
        )


class MaxStrength(BaseCurveMeasure):
    def compute(self, a: Curve) -> float:
        return a.y[-1]


class DummyModulus(BaseCurveMeasure):
    IMPOSED_MODULUS = 2.1e5

    def compute(self, a: Curve) -> float:
        return self.IMPOSED_MODULUS
