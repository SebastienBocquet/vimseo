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


import numpy as np
import pytest
from composipy import LaminateProperty
from numpy.testing import assert_array_almost_equal

from vimseo.api import create_model
from vimseo.core.model_result import ModelResult
from vimseo.lib_vimseo import tan_lib
from vimseo.problems.tan_oh.tan_oht import NOMINAL_GRID_SIZE
from vimseo.problems.tan_oh.tan_oht import PLY_THICKNESS
from vimseo.problems.tan_oh.tan_oht import material

# The default stacking is quasi-isotropic, which drives ``tan_lib`` to its two
# degeneracies: the orthotropy axes are undefined (handled by the omega = 0
# short-circuit in ``Calc_S_matrix``) and the characteristic roots merge, s1 = s2
# (handled by the root-separation floor in ``Calc_S12_eff``). Both are needed for
# this reference value to be deterministic and reproducible across BLAS/platforms.
QUASI_ISOTROPIC_STACKING = np.array([0, 45, -45, 90, 90, -45, 45, 0])

# A strongly orthotropic (0-dominant) stacking. Its roots s1 and s2 are well
# separated (|s1 - s2| ~ 4.2), so the solution is well conditioned and
# reproducible across platforms (see the module docstring of ``tan_lib``).
ORTHOTROPIC_STACKING = np.array([0, 0, 90, 0, 0, 90, 0, 0])


def _build_c_strat(stacking: np.ndarray) -> tuple[np.ndarray, float]:
    """Build the effective membrane stiffness ``c_strat`` for a stacking.

    Mirrors the construction performed at import time in ``tan_oht`` for the
    default stacking.
    """
    laminate = LaminateProperty(
        stacking, material.name_to_material_relation["orthotropic"].get_relation()
    )
    total_thickness = len(stacking) * PLY_THICKNESS
    return np.array(laminate.A) / total_thickness, total_thickness


@pytest.mark.parametrize(
    ("stacking", "expected_sigma_xx_d0"),
    [
        pytest.param(QUASI_ISOTROPIC_STACKING, 2063.958, id="quasi_isotropic"),
        pytest.param(ORTHOTROPIC_STACKING, 1979.791, id="orthotropic"),
    ],
)
def test_tan_oh(tmp_wd, stacking, expected_sigma_xx_d0):
    """Run the Tension Tan model for a given laminate and check its outputs."""
    c_strat, thickness = _build_c_strat(stacking)

    model = create_model("TanOpenHole", "Tension")
    output_data = model.execute({
        "stacking_sequence": stacking,
        "c_strat": c_strat,
        "thickness": np.atleast_1d(thickness),
    })
    input_data = model.get_input_data()
    model_result = ModelResult.from_data(
        {"outputs": output_data, "inputs": input_data}, load_fields=True
    )

    # N_ij fields must equal sigma_ij / thickness on the whole grid.
    for n_name, sigma_name in zip(
        ["N_xx", "N_yy", "N_xy"], ["sigma_xx", "sigma_yy", "sigma_xy"], strict=False
    ):
        n_data = model_result.fields["flux"][0].point_data[n_name]
        sigma_data = model_result.fields["flux"][0].point_data[sigma_name]
        assert n_data.shape == ((NOMINAL_GRID_SIZE * NOMINAL_GRID_SIZE),)
        assert_array_almost_equal(n_data, sigma_data / thickness)

    sigma_xx_d0 = output_data["sigma_xx_d0"][0]
    # Physical sanity: finite, positive, and above the applied far-field stress
    # (there is a stress concentration next to the hole). ``load`` is the applied
    # stress, and sigma = N * thickness, so the far-field stress is ``load``.
    applied_stress = input_data["load"][0]
    assert np.isfinite(sigma_xx_d0)
    assert sigma_xx_d0 > applied_stress
    assert sigma_xx_d0 == pytest.approx(expected_sigma_xx_d0, rel=1e-2)

    assert (model.archive_manager.job_directory / "flux.vtk").exists()


def test_tan_solution_is_continuous_through_isotropy():
    """The Tan stress must vary continuously as a laminate approaches isotropy.

    The Tan potentials divide by (s1 - s2), which vanishes at the isotropic
    double root. Without regularisation the solution loses precision below
    |s1 - s2| ~ 1e-6 and returns NaN at exactly isotropy. Here a stiffness family
    is morphed from orthotropic down to perfectly isotropic; the stress must stay
    finite and must not jump. This is a fast, lib-level check (no full model run).
    """
    c_iso = np.array([[6e10, 2e10, 0.0], [2e10, 6e10, 0.0], [0.0, 0.0, 2e10]])
    # Breaks the C11 == C22 symmetry without adding coupling.
    breaker = np.array([[1e10, 0.0, 0.0], [0.0, -1e10, 0.0], [0.0, 0.0, 0.0]])
    r, theta = 8.37, 0.9123
    load = np.array([1e6, 0.0, 0.0])
    radius, width = 3.175, 32.0

    # Anisotropy amplitudes decreasing down to perfect isotropy (0.0). This range
    # crosses both the omega = 0 short-circuit and the root-separation floor.
    alphas = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-8, 1e-10, 0.0]
    stresses = np.array([
        tan_lib.tan_model(r, theta, load, c_iso + alpha * breaker, radius, width)[0]
        for alpha in alphas
    ])

    # No division-by-zero blow-up, even at exact isotropy.
    assert np.all(np.isfinite(stresses))

    # No brutal jump: the relative change between consecutive (increasingly
    # isotropic) laminates stays small over the whole sweep.
    relative_steps = np.abs(np.diff(stresses)) / np.abs(stresses[:-1])
    assert np.max(relative_steps) < 1e-2

    # The near-isotropic tail has settled: the solution converges to a limit
    # instead of oscillating or diverging.
    tail = stresses[-4:]
    assert np.ptp(tail) < 1e-4 * np.abs(stresses[-1])
