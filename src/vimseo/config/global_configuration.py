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

"""Global VIMSEO configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import PydanticBaseSettingsSource
from pydantic_settings import SettingsConfigDict

from vimseo.job_executor.job_executor_factory import JobExecutorFactory

# from vimseo.storage_management import ArchiveManager

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo

ENV_PREFIX = "VIMSEO_"


class DatabaseConfiguration(BaseModel):
    mode: str = Field(default="Local")
    local_uri: str = Field(
        default="",
    )
    team_uri: str = Field(default="https://mlflow.irt-aese.local/")
    username: str = Field(default="")
    password: str = Field(default="")
    experiment_name: str = Field(default="")
    use_insecure_tls: bool = Field(default=False)
    ssl_certificate_file: str = Field(default="")


class Solver(BaseModel):
    job_executor: str | None = Field(
        default=None, description="The job executor to use."
    )
    command_run: str = Field(default="")
    command_pre: str = Field(default="")
    command_post: str = Field(default="")


class VimseoSettings(
    BaseSettings,
    validate_assignment=True,
    env_nested_delimiter="__",
    env_prefix=ENV_PREFIX,
    env_file=".env",
    extra="forbid",
):  # noqa: N801
    """Global configuration."""

    logging: str = Field(default="info")

    solver: dict[str, Solver] = Field(
        default={"dummy": Solver()}, description="The solver command."
    )

    root_directory: str = Field(
        default="", description="The root directory where tool results are written."
    )

    working_directory: str = Field(
        default="",
        description="The working directory where "
        "tool results are written. If left to empty string, results are exported in "
        "unique directories created under the root directory. If a path is prescribed, "
        "results are exported under this path.",
    )

    archive_manager: str = Field(
        default="DirectoryArchive", description="The archive manager"
    )

    database: DatabaseConfiguration = Field(
        default=DatabaseConfiguration(), description=""
    )

    @field_validator("solver")
    @classmethod
    def __validate_solver(cls, v: dict[str, Solver]) -> dict[str, Solver]:
        for solver in v.values():
            if (
                solver.job_executor
                and solver.job_executor not in JobExecutorFactory().class_names
            ):
                msg = (
                    f"{solver.job_executor} does not exist. Available job executors "
                    f"{JobExecutorFactory().class_names}."
                )
                raise ValueError(msg)
        return v


# Detect plugins to agregate the config from plugins with the vimseo config
# Temporary done with try.except of plugin imports,
# until done better with entry points:
try:
    # Plugin config:

    import vimseo_abaqus as plugin_pkg
    from vimseo_abaqus.config.global_configuration import VimseoAbaqusSettings

    plugin_settings = VimseoAbaqusSettings
    plugin_filename = "vimseo_abaqus.json"
    local_path = Path.cwd() / plugin_filename
    pkg_path = Path(plugin_pkg.__path__[0]) / plugin_filename

    class JsonConfigSettingsSource(PydanticBaseSettingsSource):
        """
        A simple settings source class that loads variables from a JSON file
        at the project's root.

        Here we happen to choose to use the `env_file_encoding` from Config
        when reading `config.json`
        """

        def get_field_value(
            self, field: FieldInfo, field_name: str
        ) -> tuple[Any, str, bool]:
            encoding = self.config.get("env_file_encoding")
            file_content_json = json.loads(
                local_path if local_path.exists() else pkg_path.read_text(encoding)
            )
            field_value = file_content_json.get(field_name)
            return field_value, field_name, False

        def prepare_field_value(
            self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
        ) -> Any:
            return value

        def __call__(self) -> dict[str, Any]:
            d: dict[str, Any] = {}

            for field_name, field in self.settings_cls.model_fields.items():
                field_value, field_key, value_is_complex = self.get_field_value(
                    field, field_name
                )
                field_value = self.prepare_field_value(
                    field_name, field, field_value, value_is_complex
                )
                if field_value is not None:
                    d[field_key] = field_value

            return d

    class Settings(plugin_settings, VimseoSettings):
        model_config = SettingsConfigDict(env_file_encoding="utf-8")

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            return (
                init_settings,
                JsonConfigSettingsSource(settings_cls),
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )

    _configuration = Settings()
except ImportError:
    _configuration = VimseoSettings()

"""The global VIMSEO configuration.

The feature is described
on the page [TODO] of the documentation.
"""
