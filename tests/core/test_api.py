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

from vimseo.api import create_model
from vimseo.api import get_available_load_cases
from vimseo.api import get_available_models
from vimseo.core.model_settings import IntegratedModelSettings


def _check_subprocess_flags(model):
    """The ``check_subprocess`` flag as seen by the model components."""
    return [
        d._check_subprocess
        for d in model._chain.disciplines
        if hasattr(d, "_check_subprocess")
    ]


def test_create_model_merges_model_options_and_kwargs(tmp_wd):
    """``model_options`` and loose keyword options are merged, not rejected."""
    cache_path = tmp_wd / "merged_cache.hdf"
    model = create_model(
        "MockModel",
        "LC1",
        check_subprocess=True,
        model_options=IntegratedModelSettings(cache_file_path=cache_path),
    )

    # the field from ``model_options`` is applied ...
    assert model._cache_file_path == cache_path
    # ... and so is the loose keyword option
    flags = _check_subprocess_flags(model)
    assert flags
    assert all(flags)


def test_create_model_kwarg_overrides_model_options(tmp_wd):
    """A loose keyword option wins over the same field of ``model_options``."""
    model = create_model(
        "MockModel",
        "LC1",
        check_subprocess=False,
        model_options=IntegratedModelSettings(
            check_subprocess=True, cache_file_path=tmp_wd / "c.hdf"
        ),
    )

    assert not any(_check_subprocess_flags(model))


def test_available_load_cases(tmp_wd):
    """Check the load cases available for a model."""
    assert get_available_load_cases("MockModel") == ["LC1", "LC2"]
    assert get_available_load_cases("BendingTestAnalytical") == [
        "Cantilever",
        "ThreePoints",
    ]


def test_available_models(tmp_wd):
    """Check that the models associated with a given load case are correctly found."""
    assert set(get_available_models("LC1")) == {
        "MockModel",
        "MockModelFields",
        "MockModelPersistent",
        "MockModelWithMaterial",
        "MockExternalSoftware",
        "MockModelLongRun",
        "MockModelSleep",
    }
