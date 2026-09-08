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

from typing import TYPE_CHECKING

from vimseo.utilities.distribution import InterfacedDistributionSettings

if TYPE_CHECKING:
    from gemseo.algos.parameter_space import ParameterSpace

    from vimseo.utilities.distribution import DistributionParameters

OPTIONS_PER_DISTRIBUTION = {
    "OTUniformDistribution": ("lower", "upper"),
    "OTNormalDistribution": ("mu", "sigma"),
    "OTTriangularDistribution": ("lower", "upper", "mode"),
    "OTWeibullDistribution": ("location", "scale", "shape"),
    "OTExponentialDistribution": ("loc", "rate"),
    "SPUniformDistribution": ("lower", "upper"),
    "SPNormalDistribution": ("mu", "sigma"),
    "SPTriangularDistribution": ("lower", "upper", "mode"),
}

# Stock gemseo's per-distribution settings classes use their own field names for
# some parameters (e.g. ``minimum``/``maximum`` instead of vimseo's generic
# ``lower``/``upper``). Only the names that differ need an entry here.
_NATIVE_FIELD_NAMES = {
    "lower": "minimum",
    "upper": "maximum",
}


def _to_native_parameters(
    distribution_name: str, settings: DistributionParameters
) -> dict:
    """Convert vimseo's generic distribution settings to gemseo's native kwargs."""
    dumped = settings.model_dump()
    parameters = {
        _NATIVE_FIELD_NAMES.get(name, name): dumped[name]
        for name in OPTIONS_PER_DISTRIBUTION[distribution_name]
    }
    for bound in ("lower_bound", "upper_bound"):
        if dumped.get(bound) is not None:
            parameters[bound] = dumped[bound]
    return parameters


def _attach_settings(
    parameter_space: ParameterSpace,
    variable_name: str,
    settings: DistributionParameters | InterfacedDistributionSettings,
) -> None:
    """Keep the vimseo settings alongside each marginal of the built variable.

    Stock gemseo distribution objects no longer expose the settings they were
    built from (unlike the private fork this used to rely on), so vimseo
    attaches them itself in order to be able to serialize them back later
    (see :class:`~.SpaceToolFileIO`). For a vector variable, each marginal gets
    its own component of any per-component (list-valued) field, matching the
    per-marginal settings the fork used to expose.
    """
    marginals = parameter_space.distributions[variable_name].marginals
    dumped = settings.model_dump()
    for index, marginal in enumerate(marginals):
        component_values = {
            name: value[index] if isinstance(value, list) else value
            for name, value in dumped.items()
        }
        marginal.vimseo_settings = type(settings)(**component_values)


def add_random_variable_interface(
    parameter_space: ParameterSpace,
    variable_name: str,
    settings: DistributionParameters | InterfacedDistributionSettings,
    size: int = 1,
):
    """An interface to handle seamlessly the interfaces to
    :meth:`gemseo.algos.parameter_space.add_random_variable` for an OT distribution."""
    if isinstance(settings, InterfacedDistributionSettings):
        if size != 1:
            msg = (
                f"Only scalars are handled for an "
                f"``InterfaceDistribution``. But variable {variable_name} "
                f"has dimension {size}."
            )
            raise ValueError(msg)
        parameter_space.add_random_variable(
            variable_name,
            "OTDistribution",
            size=size,
            interfaced_distribution=settings.name,
            interfaced_distribution_parameters=settings.parameters,
            lower_bound=settings.lower_bound,
            upper_bound=settings.upper_bound,
        )
    else:
        distribution_name = f"OT{settings.name}Distribution"
        parameters = _to_native_parameters(distribution_name, settings)
        if size == 1:
            parameter_space.add_random_variable(
                variable_name,
                distribution_name,
                size=size,
                **parameters,
            )
        else:
            parameter_space.add_random_vector(
                variable_name,
                size=size,
                distribution=distribution_name,
                **parameters,
            )
        if settings.name == "Weibull":
            # gemseo's ``OTWeibullDistribution`` always builds a WeibullMin (or
            # WeibullMax) OpenTURNS distribution under the hood; canonicalize the
            # attached name to match, as vimseo's own serialization/tests expect.
            settings = settings.model_copy(update={"name": "WeibullMin"})

    _attach_settings(parameter_space, variable_name, settings)
