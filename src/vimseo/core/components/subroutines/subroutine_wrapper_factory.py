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

from gemseo.core.base_factory import BaseFactory

from vimseo.core.components.subroutines.subroutine_wrapper import SubroutineWrapper


class SubroutineWrapperFactory(BaseFactory):
    """SubroutineWrapper factory to create a subroutine wrapper from a name or a
    class."""

    _CLASS = SubroutineWrapper
    _PACKAGE_NAMES = ("vims.core", "vims.wrapper", "vims.problems")

    def create(
        self,
        subroutine_wrapper_name: str,
        **options,
    ) -> SubroutineWrapper:
        """Create a subroutine wrapper.

        Args:
            subroutine_wrapper_name: The name of the subroutine wrappers (its class name).
            **options: The options of the subroutine wrappers.
        """
        return super().create(subroutine_wrapper_name, **options)

    @property
    def subroutine_wrappers(self) -> list[str]:
        """The names of the available subroutine wrappers."""
        return self.class_names
