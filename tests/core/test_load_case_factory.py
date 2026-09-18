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

from vimseo.core.load_case import LoadCase
from vimseo.core.load_case_factory import LoadCaseFactory


def test_load_case_factory_rejects_legacy_curves_key(tmp_path, monkeypatch):
    """The renamed ``plot_parameters.curves`` JSON key is rejected, not silently used."""
    fake_json = tmp_path / "fake.json"
    fake_json.write_text("{}")
    monkeypatch.setattr(
        LoadCase, "auto_get_file", lambda self, suffix, raise_error=True: [fake_json]
    )
    monkeypatch.setattr(
        "vimseo.core.load_case_factory.json.load",
        lambda f: {"plot_parameters": {"curves": ["x", "y"]}},
    )

    with pytest.raises(ValueError, match="has been replaced by plots"):
        LoadCaseFactory().create("LC1")
