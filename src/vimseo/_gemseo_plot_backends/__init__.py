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
"""Dataset plot backends missing from stock gemseo.

The private gemseo fork vimseo used to depend on added plotly rendering
backends for a few dataset plot classes (e.g. ``ScatterMatrix``) directly
inside the ``gemseo`` package; stock gemseo only ships their matplotlib
backends. gemseo's plot factories also scan every package registered under
the ``gemseo_plugins`` entry point (vimseo is one), so classes defined here
are picked up the same way, without needing a gemseo fork.
"""

from __future__ import annotations
