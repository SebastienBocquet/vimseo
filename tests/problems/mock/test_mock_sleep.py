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
from numpy import atleast_1d

from vimseo.api import create_model

pytestmark = pytest.mark.fast


def test_mock_model_sleep_executes_with_overridden_durations(tmp_wd):
    """The pre/run/post chain sleeps for the given durations and computes y1.

    The default 30s-per-phase durations are overridden to 0 so the test stays fast.
    """
    model = create_model("MockModelSleep", "LC1")
    model.default_input_data["x1"] = atleast_1d(1.0)
    model.default_input_data["pre_duration"] = atleast_1d(0.0)
    model.default_input_data["run_duration"] = atleast_1d(0.0)
    model.default_input_data["post_duration"] = atleast_1d(0.0)
    model.EXTRA_INPUT_GRAMMAR_CHECK = True

    out = model.execute()

    # x2 = x1 + 2, y0 = x2 * 2, y1 = y0 + 1
    assert out["y1"][0] == pytest.approx(7.0)
    assert out["error_code"][0] == 0
