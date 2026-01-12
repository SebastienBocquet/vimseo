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
import pprint
from copy import copy
from logging import getLogger
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar

from gemseo.utils.string_tools import MultiLineString

import vimseo

if TYPE_CHECKING:
    from collections.abc import Mapping

LOGGER = getLogger(__name__)


class ConfigManager:
    """This class initialize configuration variables from environment variables and
    .config file.

    User can define an environment variable called VIMS_PROJECT_DIRECTORY to setup the
    working directory. If not defined, it is created with current working directory as
    default value.

    if no .config file exists in the working directory, the default file
    VIMS_DEFAULT_CONFIG.config is used (located at vims/)
    """

    BASE_CONFIG_VAR_LIST: ClassVar[str] = [
        "VIMS_PROJECT_DIRECTORY",
        "N_CPUS",
        "JOB_EXECUTOR",
        "CMD_ABAQUS_CAE",
        "CMD_ABAQUS_CAE_POST",
        "CMD_ABAQUS_RUN",
        "CMD_PAOLO_MODEL",
        "VIMS_TEST_DIR",
        "LOGGER_MODE",
        "ROOT_DIRECTORY",
        "WORKING_DIRECTORY",
        "TEST_LOGGER_MODE",
        "ARCHIVE_MANAGER",
        "DB_MODE",
        "DB_URI_TEAM",
        "DB_URI_LOCAL",
        "DB_USERNAME",
        "DB_PASSWORD",
        "USE_INSECURE_TLS",
        "SSL_CERTIFICATE_FILE",
        "EXPERIMENT_NAME",
    ]
    """The configuration variables."""

    DEFAULT_ENV_FILE: ClassVar[Path] = (
        Path(vimseo.__file__).parent / "VIMS_DEFAULT_CONFIG.config"
    )
    """The default configuration file."""

    _VAR_LIST_HELP: ClassVar[Mapping[str, str]] = {
        "N_CPUS": "Not used at the moment",
        "JOB_EXECUTOR": "The job executor of the model run processor.",
        "VIMS_TEST_DIR": "Not used at the moment.",
        "LOGGER_MODE": "Level of the logger. It can be 'info', 'warn', 'error'",
        "TEST_LOGGER_MODE": "Level of the logger for the tests.",
        "ROOT_DIRECTORY": "The root directory of the unique directories",
        "WORKING_DIRECTORY": "The working directory. If left to empty string, results"
        "are exported in unique directories created under the root"
        "directory. If a path is prescribed, results are exported under this path.",
        "ARCHIVE_MANAGER": "The manager of archive data.",
        "DB_MODE": "The type of database, either ``Local`` or ``Team``.",
        "DB_URI_TEAM": "The database URI for Team mode.",
        "DB_URI_LOCAL": "The database URI in Local mode. It can be set to "
        "empty string and a default path is used.",
        "DB_USERNAME": "The database username.",
        "DB_PASSWORD": "The database password.",
        "USE_INSECURE_TLS": "Whether to use insecure TLS or not.",
        "SSL_CERTIFICATE_FILE": "The path to an SSL certificate file.",
        "EXPERIMENT_NAME": "The name of the experiment under which to store the runs.",
    }

    def __init__(self, env=environ):
        # initialisation of the list of config variables
        self.config_var_list = copy(self.BASE_CONFIG_VAR_LIST)
        # for var in self.BASE_CONFIG_VAR_LIST:
        #     if var in env.keys():
        #         self.config_var_list.remove(var)

        with Path(self.DEFAULT_ENV_FILE).open() as default_file:
            self.default_values = json.load(default_file)

        project_dir_env_var = env.get("VIMS_PROJECT_DIRECTORY")

        project_dir_path = None
        if not project_dir_env_var:
            project_dir_path = Path.cwd()
            env["VIMS_PROJECT_DIRECTORY"] = str(project_dir_path)
        else:
            project_dir_path = Path(project_dir_env_var)

        self.default_values.update({"VIMS_PROJECT_DIRECTORY": str(project_dir_path)})

        self.project_config_file = None
        config_var = {}
        # load the first .config file in project directory
        for file in project_dir_path.iterdir():
            if file.is_file() and file.suffix == ".config":
                self.project_config_file = project_dir_path / file
                LOGGER.info(f"Current config file: {self.project_config_file}")
                with Path(self.project_config_file).open() as project_file:
                    config_var = json.load(project_file)

        if self.project_config_file is None:
            LOGGER.info("No config file found")

        self.config_var_list.extend(
            key for key in config_var if key not in self.config_var_list
        )

        for var in self.config_var_list:
            try:  # update attribute from config file
                self.__setattr__(var, config_var[var])
                use_default = False
            except KeyError:  # if not in config file use default value
                use_default = True

            # overwrite with environment variable if it exists
            try:
                self.__setattr__(var, env[var])
            except KeyError:
                if use_default:
                    try:
                        self.__setattr__(var, self.default_values[var])
                    except KeyError:
                        LOGGER.warning(
                            f"Config variable {var} is not defined. "
                            "Use vimseo.api.set_config(), or add it to the "
                            f".config file: {self.project_config_file}"
                        )

    def get_available_config_variables(self):
        return self.config_var_list

    def __str__(self):
        msg = MultiLineString()

        msg.add("----- VIMS current configuration ---------")
        for var in self.config_var_list:
            config_value = config.__getattribute__(var)
            if type(config_value) is str:
                config_value = config_value.replace("{", "(")
                config_value = config_value.replace("}", ")")
            msg.add(f"{var} -> {config_value}")
        msg.add("------------------------------------------")

        return str(msg)

    def get_help(self):
        pprint.pprint(self._VAR_LIST_HELP)

    def get_config_as_dict(self):
        config = {}
        for var in self.config_var_list:
            config[var] = self.__getattribute__(var)

        return config


config = ConfigManager()
