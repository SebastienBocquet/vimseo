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

# Copyright (c) 2019 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: XXXXXXXXXXX
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
from __future__ import annotations

from os import environ

from vimseo.config.global_configuration import VimseoSettings
from vimseo.config.global_configuration import _configuration as config


def test_config_from_env_var():
    job_executor = config.solver["dummy"].job_executor
    assert not job_executor
    environ["VIMSEO_SOLVER__DUMMY__JOB_EXECUTOR"] = "BaseInteractiveExecutor"
    config_ = VimseoSettings()
    assert (
        config_.model_dump()["solver"]["dummy"]["job_executor"]
        == "BaseInteractiveExecutor"
    )


def test_config_set_attr():
    job_executor = config.solver["dummy"].job_executor
    assert not job_executor
    config.solver["dummy"].job_executor = "BaseInteractiveExecutor"
    assert (
        config.model_dump()["solver"]["dummy"]["job_executor"]
        == "BaseInteractiveExecutor"
    )


def test_config_with_config_file(tmp_wd):
    with (tmp_wd / ".env").open("w") as f:
        f.write('VIMSEO_SOLVER__DUMMY2__JOB_EXECUTOR="BaseInteractiveExecutor"\n')

    config = VimseoSettings()
    assert {"dummy2", "abaqus"} == set(config.solver.keys())
    assert config.solver["dummy2"].job_executor == "BaseInteractiveExecutor"
