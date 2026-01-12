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

import json
from os import environ
from os import path
from pathlib import Path

import vimseo
from vimseo.config.config_manager import ConfigManager

DIRNAME = path.dirname(__file__)


def test_config():
    environ["VIMS_PROJECT_DIRECTORY"] = DIRNAME

    config = ConfigManager()

    assert config.project_config_file.name == "VIMS_TEST_CONFIG.config"
    # check base variables are loaded:
    assert config.VIMS_PROJECT_DIRECTORY == DIRNAME
    assert config.N_CPUS == "4"
    # check default value is loaded:
    assert config.LOGGER_MODE == "info"
    # check that the variable added in config file is loaded:
    assert config.TEST_VARIABLE == 10


def test_config_wo_config_file(tmp_wd):
    """The default configuration should be read."""

    environ["VIMS_PROJECT_DIRECTORY"] = str(Path.cwd())

    config = ConfigManager()
    default_config = config.get_config_as_dict()

    default_config_file = Path(vimseo.__path__[0]) / "VIMS_DEFAULT_CONFIG.config"
    config_from_default_file = json.loads(default_config_file.read_text())

    for k, v in config_from_default_file.items():
        assert default_config[k] == v

    assert config.project_config_file is None
    assert environ.get("VIMS_PROJECT_DIRECTORY") == config.VIMS_PROJECT_DIRECTORY
