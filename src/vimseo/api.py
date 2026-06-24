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

# Copyright (c) 2020 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: Ludovic BARRIERE
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
from __future__ import annotations

import logging
import warnings
warnings.filterwarnings(
    "ignore",
    message="No runtime found",
    category=UserWarning,
)

import logging
from logging import _nameToLevel
from typing import TYPE_CHECKING

from gemseo import configure_logger
from gemseo.utils.metrics.metric_factory import MetricFactory

from vimseo.config.global_configuration import _configuration as configuration
from vimseo.core.load_case_factory import LoadCaseFactory
from vimseo.core.model_factory import ModelFactory
from vimseo.core.model_settings import IntegratedModelSettings
from vimseo.problems.load_cases import DUMMY_LOAD_CASE_NAME
from vimseo.tools.post_tools.plot_factory import PlotFactory
from vimseo.tools.tools_factory import ToolsFactory

if TYPE_CHECKING:
    from vimseo.core.base_integrated_model import IntegratedModel

LOGGER = logging.getLogger(__name__)


def activate_logger(**options):
    level = options.get("level", _nameToLevel[configuration.logging.upper()])
    options["level"] = level
    configure_logger(**options)


def create_model(
    model_name,
    load_case_name=DUMMY_LOAD_CASE_NAME,
    model_options: IntegratedModelSettings | None = None,
    **options,
) -> IntegratedModel:
    """Create a model from its name.

    Args:
        model_name: string, name of the model to create
            (see :meth:`~vimseo.api.get_available_models` for valid names)
        load_case_name: The name of the load case that the model will execute.
        options: The options of the model.

    Returns: An instance of an :class:`.IntegratedModel`.
    """
    if model_options:
        options.update(model_options.model_dump())
    return ModelFactory().create(model_name, load_case_name, **options)


def get_available_load_cases(model_name: str) -> list[str]:
    """Find the load cases available for this model.

    Args:
        model_name: The model name.

    Returns:
        The load cases associated with the specified model.
    """
    lc_factory = LoadCaseFactory()
    model_class = ModelFactory().get_class(model_name)
    domain = model_class._LOAD_CASE_DOMAIN
    all_load_case_names = []
    for class_name in lc_factory.class_names:
        if domain != "" and class_name.startswith(domain):
            class_name = class_name.removeprefix(f"{domain}_")
        try:
            lc = lc_factory.create(class_name, domain=domain)
            all_load_case_names.append(lc.name)
        except ImportError:
            continue

    if model_name != "PreRunPostModel" and issubclass(model_class, PreRunPostModel):
        all_component_names = ComponentFactory().class_names
        matching_load_case_names = []
        for c in all_component_names:
            candidate_load_case_name = c.removeprefix(model_class.PRE_PROC_FAMILY + "_")
            if c.startswith(model_class.PRE_PROC_FAMILY) and candidate_load_case_name in all_load_case_names:
                matching_load_case_names.append(candidate_load_case_name)
    else:
        # TODO: for non PreRunPostModel, define the load cases used by a model explicitely (as class attribute).
        load_case_names = list(set(all_load_case_names))
        matching_load_case_names = []
        for load_case_name in load_case_names:
            if load_case_name == DUMMY_LOAD_CASE_NAME:
                continue
            try:
                create_model(
                    model_name,
                    load_case_name,
                    archive_manager="DirectoryArchive",
                )
                matching_load_case_names.append(load_case_name)
            except (ImportError, AttributeError):
                continue

    return sorted(matching_load_case_names)


def get_available_models(load_case: str = "") -> list[str]:
    """Returns the list of the available models.

    Args:
        load_case: The considered load case. If specified, only the models
            using this load case are returned.

    Returns:
        The list of names of the available models.
    """
    mf = ModelFactory()
    model_names = mf.class_names
    if load_case == "":
        model_names.remove("PreRunPostModel")
        model_names.remove("ModelComposition")
        return model_names
    model_to_lc = {}
    for model_name in model_names:
        model_to_lc[model_name] = get_available_load_cases(model_name)
    models = []
    for model, load_cases in model_to_lc.items():
        if load_case in load_cases:
            models.append(model)
    return sorted(models)


def get_available_plots():
    """The available plots, deriving from ``Plotter``."""
    class_names = PlotFactory().class_names
    class_names.remove("Plotter")
    return class_names


def get_available_metrics():
    """The available comparison metrics."""
    return MetricFactory().class_names
    # class_names.remove("BaseMetrics")


def get_available_tools():
    """The available tools."""
    class_names = ToolsFactory().class_names
    class_names.remove("BaseTool")
    return class_names


def print_config():
    """Returns: representation of the current configuration variables."""
    LOGGER.info(configuration.model_dump())


def print_config_help():
    """Return the help about configuration file."""
    LOGGER.info(configuration.model_fields)


activate_logger()