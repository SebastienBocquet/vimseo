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

from vimseo.core.base_integrated_model import IntegratedModel
from vimseo.core.load_case import LoadCase
from vimseo.core.model_description import ModelDescription
from vimseo.tools.post_tools.plot_parameters import Plot


def _make_description(**kwargs) -> ModelDescription:
    group_names = IntegratedModel.InputGroupNames
    return ModelDescription(
        name="MyModel",
        summary="A model.",
        load_case=LoadCase(name="LC1"),
        dataflow={"model_inputs": ["x"], "model_outputs": ["y"]},
        default_inputs={
            group_names.NUMERICAL_VARS: {"x": 1.0},
            group_names.GEOMETRICAL_VARS: {},
            group_names.BC_VARS: {},
            group_names.MATERIAL_VARS: {},
        },
        **kwargs,
    )


def test_model_description_default_rendering():
    """The default (non-verbose) rendering has no dataflow or plots section."""
    description = _make_description()

    text = str(description)

    assert text.startswith("Model MyModel: A model.")
    assert "x = 1.0" in text
    assert "Model inputs: x" in text
    assert "Model outputs: y" in text
    assert "Dataflow:" not in text
    assert "Plots:" not in text


def test_model_description_verbose_rendering_includes_dataflow_and_plots():
    """Verbose rendering adds the dataflow (JSON) and the plots repr."""
    description = _make_description(
        plots=[Plot.from_variable_names(("x", "y"))], verbose=True
    )

    text = str(description)

    assert "Dataflow:" in text
    assert "Plots:" in text
