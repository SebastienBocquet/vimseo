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

import pytest
from gemseo.algos.design_space import DesignSpace
from gemseo.algos.opt.nlopt.settings.nlopt_cobyla_settings import NLOPT_COBYLA_Settings
from gemseo.datasets.io_dataset import IODataset
from gemseo_calibration.measures.integrated_measure import CurveScaling
from numpy import concatenate
from numpy import linspace

from vimseo.api import activate_logger
from vimseo.tools.calibration.calibration_step import CalibrationMetricSettings
from vimseo.tools.calibration.calibration_step import CalibrationStep
from vimseo.tools.calibration.calibration_step import CalibrationStepInputs
from vimseo.tools.calibration.calibration_step import CalibrationStepSettings
from vimseo.utilities.curves_generator import expressions_convexity
from vimseo.utilities.curves_generator import expressions_oscillate
from vimseo.utilities.curves_generator import get_history

activate_logger()

NB_REF_POINTS = 50


def create_reference_dataset(x_left: float, x_right: float, y_max: float):

    x_ref = get_history(support=linspace(x_left, x_right, NB_REF_POINTS))
    y_ref = get_history(
        list_expressions=[
            expressions_convexity["convex"],
            expressions_oscillate["half_drop"],
        ],
        support=x_ref,
    )
    reference_data = IODataset.from_array(
        data=[concatenate([x_ref, y_ref * y_max])],
        variable_names=["y_axis", "y"],
        variable_names_to_n_components={
            "y": NB_REF_POINTS,
            "y_axis": NB_REF_POINTS,
        },
    )
    reference_data.add_variable(
        variable_name="x_left", data=[x_left], group_name="outputs"
    )
    reference_data.add_variable(
        variable_name="x_right", data=[x_right], group_name="outputs"
    )
    return reference_data


@pytest.mark.slow
@pytest.mark.parametrize(
    ("x_ref_left", "x_ref_right", "y_ref_max"),
    [
        (-0.5, 0.5, 1.0),
        (-5e-4, 5e-4, 1.0),
        (-0.5, 0.5, 1e-3),
        (-5e-4, 5e-4, 1e-3),
    ],
)
@pytest.mark.parametrize(
    ("algo", "optimizer_settings", "delta_x_left", "delta_x_right"),
    [
        ("NLOPT_COBYLA", NLOPT_COBYLA_Settings(), 0.2, 0.2),
        ("NLOPT_COBYLA", NLOPT_COBYLA_Settings(), -0.2, 0.2),
        ("NLOPT_COBYLA", NLOPT_COBYLA_Settings(), -0.2, -0.2),
        ("NLOPT_COBYLA", NLOPT_COBYLA_Settings(), 0.2, -0.2),
    ],
)
def test_exceeding_abscissa_penalization(
    tmp_wd,
    algo,
    optimizer_settings,
    delta_x_left,
    delta_x_right,
    x_ref_left,
    x_ref_right,
    y_ref_max,
):
    pytest.skip(
        "TODO Sebastien review: pytests are long to execute, especially this test "
        "that is way too long"
    )
    reference_data = create_reference_dataset(x_ref_left, x_ref_right, y_ref_max)

    # The starting point of the model x left and x right:
    x_left = x_ref_left + delta_x_left * (x_ref_right - x_ref_left)
    x_right = x_ref_right + delta_x_right * (x_ref_right - x_ref_left)
    # The starting point for the max y of the model:
    y_max = 1.2 * y_ref_max

    design_space = DesignSpace()
    design_space.add_variable(
        "x_left", value=x_left, lower_bound=x_left * 2, upper_bound=-1e-6
    )
    design_space.add_variable(
        "x_right", value=x_right, lower_bound=1e-6, upper_bound=x_right * 2
    )
    design_space.add_variable(
        "y_max", value=y_max, lower_bound=0.0, upper_bound=10 * y_max
    )

    step = CalibrationStep()
    step.execute(
        inputs=CalibrationStepInputs(
            reference_data={
                "Dummy": reference_data,
            },
            starting_point={"x_left": x_left, "x_right": x_right, "y_max": y_max},
            design_space=design_space,
        ),
        settings=CalibrationStepSettings(
            model_name={"Dummy": "MockCurvesXRange"},
            control_outputs={
                "y": CalibrationMetricSettings(
                    measure="SBPISE",
                    mesh="y_axis",
                    scaling=CurveScaling.XYRange,
                    x_left_penalization_factor=1.0,
                    x_right_penalization_factor=1.0,
                ),
            },
            parameter_names=["x_left", "x_right", "y_max"],
            optimizer_name=algo,
            optimizer_settings=optimizer_settings,
        ),
    )
    step.plot_results(step.result, show=False, save=True)
    assert step.result.posterior_parameters["x_left"] == pytest.approx(
        x_ref_left, rel=5e-2
    )
    assert step.result.posterior_parameters["x_right"] == pytest.approx(
        x_ref_right, rel=5e-2
    )
    assert step.result.posterior_parameters["y_max"] == pytest.approx(
        y_ref_max, rel=5e-2
    )
