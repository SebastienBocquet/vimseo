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
from gemseo.datasets.dataset import Dataset
from numpy import concatenate
from numpy import linspace

from vimseo.tools.calibration.calibration_metrics import SBPISE
from vimseo.utilities.curves_generator import expressions_convexity
from vimseo.utilities.curves_generator import expressions_oscillate
from vimseo.utilities.curves_generator import get_history
from vimseo.utilities.curves_generator import n_points


@pytest.mark.parametrize(
    "is_last_x_less_than_first_x",
    [
        False,
        # True
    ],
)
@pytest.mark.parametrize(
    "is_decreasing_simulation",
    [
        False,
        # True
    ],
)
@pytest.mark.parametrize(
    "is_decreasing_reference",
    [False, True],
)
@pytest.mark.parametrize(
    ("x_left", "x_right"),
    [
        (0.1, 0.9),
        # (0.0, 1.0),
        # (0.0, 1.1),
        # (-0.1, 1.0),
        # (-0.1, 1.1),
    ],
)
def test_ise(
    x_left,
    x_right,
    is_decreasing_reference,
    is_decreasing_simulation,
    is_last_x_less_than_first_x,
):
    metric = SBPISE("y", "y_mesh", True, 1.0, 1.0)

    x_hist_exp = get_history(support=linspace(x_left, x_right, n_points))
    if is_last_x_less_than_first_x:
        x_hist_exp = -x_hist_exp
    y_hist_exp = get_history(
        [
            expressions_convexity["convex"],
            expressions_oscillate["half_drop"],
            "x*0.9",
        ],
        support=x_hist_exp,
    )

    # building a mock numerical curve
    x_hist_num = get_history()
    if is_last_x_less_than_first_x:
        x_hist_num = -x_hist_num
    y_hist_num = get_history(
        list_expressions=[
            expressions_convexity["concave"],
            expressions_oscillate["half_drop"],
        ],
        support=x_hist_num,
    )

    if is_decreasing_reference:
        x_hist_exp = x_hist_exp[::-1]
        y_hist_exp = y_hist_exp[::-1]
    if is_decreasing_simulation:
        x_hist_num = x_hist_num[::-1]
        y_hist_num = y_hist_num[::-1]

    reference_data = Dataset.from_array(
        data=[concatenate([x_hist_exp, y_hist_exp])],
        variable_names=["y_mesh", "y"],
        variable_names_to_n_components={
            "y": n_points,
            "y_mesh": n_points,
        },
    )
    model_dataset = Dataset.from_array(
        data=[concatenate([x_hist_num, y_hist_num])],
        variable_names=["y_mesh", "y"],
        variable_names_to_n_components={
            "y": n_points,
            "y_mesh": n_points,
        },
    )

    metric.set_reference_data(reference_data.to_dict_of_arrays(False))
    result = metric._evaluate_measure(model_dataset.to_dict_of_arrays(False))
    print(result)


@pytest.mark.parametrize(
    ("x_left", "x_right"),
    [
        (-0.2, -0.1),
        (1.1, 1.2),
    ],
)
def test_ise_disjoint_supports(x_left, x_right):
    metric = SBPISE("y", "y_mesh", True, 1.0, 1.0)

    x_hist_exp = get_history(support=linspace(x_left, x_right, n_points))
    y_hist_exp = get_history([
        expressions_convexity["convex"],
        expressions_oscillate["half_drop"],
        "x*0.9",
    ])

    # building a mock numerical curve
    x_hist_num = get_history()
    y_hist_num = get_history(
        list_expressions=[
            expressions_convexity["concave"],
            expressions_oscillate["half_drop"],
        ]
    )

    reference_data = Dataset.from_array(
        data=[concatenate([x_hist_exp, y_hist_exp])],
        variable_names=["y_mesh", "y"],
        variable_names_to_n_components={
            "y": n_points,
            "y_mesh": n_points,
        },
    )
    model_dataset = Dataset.from_array(
        data=[concatenate([x_hist_num, y_hist_num])],
        variable_names=["y_mesh", "y"],
        variable_names_to_n_components={
            "y": n_points,
            "y_mesh": n_points,
        },
    )

    metric.set_reference_data(reference_data.to_dict_of_arrays(False))

    with pytest.raises(ValueError):
        metric._evaluate_measure(model_dataset.to_dict_of_arrays(False))
