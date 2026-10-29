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

"""Tests of the error code of a model, as returned by the chain of its components."""

from __future__ import annotations

import pytest
from gemseo.disciplines.analytic import AnalyticDiscipline
from numpy import array
from numpy import atleast_1d

from vimseo.api import create_model
from vimseo.core.base_integrated_model import IntegratedModel
from vimseo.core.components.base_component import BaseComponent
from vimseo.core.model_composition import ModelComposition
from vimseo.core.model_metadata import MetaDataNames

ERROR_CODE = MetaDataNames.error_code.name


class _PostReadingErrorCode(BaseComponent):
    """A post component reading the upstream error code, and possibly recovering from
    an upstream error."""

    auto_detect_grammar_files = False

    def __init__(self, recovers: bool = False) -> None:
        super().__init__()
        self.output_grammar.update_from_data({"upstream_error_code": atleast_1d(0)})
        self._recovers = recovers

    def _run(self, input_data):
        output_data = {
            "upstream_error_code": atleast_1d(self._get_upstream_error_code(input_data))
        }
        if self._recovers:
            output_data[ERROR_CODE] = array([0])
        return output_data


def test_error_code_is_not_a_model_input(tmp_wd):
    """The components read the upstream error code, but it is not a model input."""
    model = create_model("MockModel", "LC1")

    assert ERROR_CODE in model._chain.disciplines[0].input_grammar
    for names in (
        model.input_grammar,
        model.default_input_data,
        model.input_space,
        model.lower_bounds,
        model.upper_bounds,
    ):
        assert ERROR_CODE not in names


def test_last_component_must_declare_error_code(tmp_wd):
    """A model whose last component cannot return an error code is rejected, since
    the model could not report its error code."""
    with pytest.raises(TypeError, match="does not declare the output 'error_code'"):
        IntegratedModel("LC1", [AnalyticDiscipline({"y": "2*x"})])


def test_composition_reports_error_code_of_base_model(tmp_wd):
    """A model composition reports the error code of its base model, without changing
    the one of the base model."""
    base_model = create_model("MockFaultyRunPost", "LC1")
    model = ModelComposition("LC1", base_model=base_model)

    model.execute({"run_succeeds": atleast_1d(False)})

    assert model.get_output_data()[ERROR_CODE][0] == 1
    assert base_model.get_output_data()[ERROR_CODE][0] == 1


@pytest.mark.parametrize(("recovers", "expected_error_code"), [(False, 1), (True, 0)])
def test_composition_post_reads_and_overrides_error_code(
    tmp_wd, recovers, expected_error_code
):
    """A post component added to a model reads the error code of the base model, and
    the error code of the composition is the last one returned along the chain."""
    model = ModelComposition(
        "LC1",
        base_model=create_model("MockFaultyRunPost", "LC1"),
        post_components=[_PostReadingErrorCode(recovers=recovers)],
    )

    model.execute({"run_succeeds": atleast_1d(False)})

    output_data = model.get_output_data()
    assert output_data["upstream_error_code"][0] == 1
    assert output_data[ERROR_CODE][0] == expected_error_code
