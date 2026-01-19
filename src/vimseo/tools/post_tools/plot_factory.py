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

from __future__ import annotations

import logging

from gemseo.core.base_factory import BaseFactory

from vimseo.tools.post_tools.verification_plots import Plotter

LOGGER = logging.getLogger(__name__)


class PlotFactory(BaseFactory):
    """Plot factory to create a :class:`~.Plotter` from a name or a class."""

    _CLASS = Plotter
    _PACKAGE_NAMES = ("vimseo.tools.post_tools",)

    def create(
        self,
        plot_name: str,
        **options,
    ) -> Plotter:
        """Create a validation plot.

        Args:
            plot_name: The name of the validation plot (its class name).
            **options: The options of the validation plot.
        """
        return super().create(plot_name, **options)

    @property
    def plots(self) -> list[str]:
        """The names of the available validation plots."""
        return self.class_names
