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

import pytest

from vimseo.tools.calibration.calibration_step import _normalize_weights


def _normalized(weights: dict[str, float | None]) -> dict[str, float | None]:
    """Normalize ``{namespaced output: weight}`` and return the resulting weights."""
    control_outputs = {name: {"weight": weight} for name, weight in weights.items()}
    _normalize_weights(control_outputs)
    return {name: settings["weight"] for name, settings in control_outputs.items()}


@pytest.mark.parametrize(
    ("weights", "expected"),
    [
        # No weight given: gemseo-calibration's equal split is kept.
        ({"A:a": None, "A:b": None}, {"A:a": None, "A:b": None}),
        # Relative weights; the last one is left to the remainder (1/3).
        ({"A:a": 2.0, "A:b": 1.0}, {"A:a": 2 / 3, "A:b": None}),
        # Equal weights fall back to the equal split.
        ({"A:a": 0.7, "A:b": 0.7}, {"A:a": None, "A:b": None}),
        # A single weight would be 1, which gemseo-calibration rejects.
        ({"A:a": 1.0}, {"A:a": None}),
        # A missing weight counts as 1 once another one is given.
        ({"A:a": 3.0, "A:b": None}, {"A:a": 0.75, "A:b": None}),
        # A flat {a: 2, b: 1} copied over two load cases: each output keeps its
        # share (2/3, 1/3), split evenly between the load cases.
        (
            {"A:a": 2.0, "A:b": 1.0, "B:a": 2.0, "B:b": 1.0},
            {"A:a": 1 / 3, "A:b": 1 / 6, "B:a": 1 / 3, "B:b": None},
        ),
        # Weights given per load case weight one load case against the other.
        ({"A:o": 3.0, "B:o": 1.0}, {"A:o": 0.75, "B:o": None}),
    ],
)
def test_normalize_weights(weights, expected):
    """Check that relative weights are normalized over all the load cases."""
    assert _normalized(weights) == pytest.approx(expected)


def test_normalized_weights_are_accepted_by_gemseo_calibration():
    """Check that the explicit weights lie in ]0, 1[ and leave a positive remainder."""
    weights = _normalized({"A:a": 5.0, "A:b": 1.0, "B:a": 5.0, "B:b": 1.0})
    explicit = [weight for weight in weights.values() if weight is not None]
    assert all(0 < weight < 1 for weight in explicit)
    assert sum(explicit) < 1
