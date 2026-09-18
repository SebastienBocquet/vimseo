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

from gemseo.disciplines.analytic import AnalyticDiscipline

from vimseo.api import create_model
from vimseo.core.components.discipline_wrapper_component import (
    DisciplineWrapperComponent,
)
from vimseo.core.load_case import LoadCase


def test_job_executor_is_none_for_a_plain_discipline():
    """A wrapped plain GEMSEO discipline has no job executor of its own."""
    discipline = AnalyticDiscipline({"y": "x+1"})
    component = DisciplineWrapperComponent(LoadCase(name="LC1"), discipline)

    assert component.job_executor is None


def test_job_executor_forwards_the_wrapped_models_one(tmp_wd):
    """Wrapping an integrated model forwards its own job executor."""
    inner_model = create_model("MockModel", "LC1")
    component = DisciplineWrapperComponent(LoadCase(name="LC1"), inner_model)

    assert component.job_executor is inner_model.job_executor
