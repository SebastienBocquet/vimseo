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

"""Tests of the error code of an external software component."""

from __future__ import annotations

from subprocess import CalledProcessError

import pytest

from vimseo.api import create_model
from vimseo.core.model_metadata import MetaDataNames


@pytest.mark.parametrize(
    ("return_code", "expected_error_code"),
    [(0, 0), (1, 1), (2, 1), (-15, 1)],
)
def test_error_code_from_return_code(tmp_wd, return_code, expected_error_code):
    """The error code reports whether the external software failed, whatever its
    non-zero return code, e.g. a negative one when it is killed by a signal."""
    model = create_model("MockExternalSoftware", "LC1")
    model.run.job_executor.execute = lambda check_subprocess: return_code

    output_data = model.execute()

    assert output_data[MetaDataNames.error_code][0] == expected_error_code


def test_failed_external_software_raises_when_checked(tmp_wd):
    """With ``check_subprocess=True``, a failed external software raises, with its
    original return code."""
    model = create_model("MockExternalSoftware", "LC1")
    model.run._check_subprocess = True
    model.run.job_executor.execute = lambda check_subprocess: -15

    with pytest.raises(CalledProcessError) as error:
        model.execute()

    assert error.value.returncode == -15
