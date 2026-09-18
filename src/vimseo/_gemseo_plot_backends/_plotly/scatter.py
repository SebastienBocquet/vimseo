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
"""Scatter based on plotly.

Ported from the private gemseo fork this used to depend on (which added it
directly inside ``gemseo.post.dataset.plots._plotly``), since stock gemseo
only ships a matplotlib backend for :class:`~gemseo.post.dataset.scatter.Scatter`.
The fork's version colored points by an extra ``coloring_variable`` setting;
that setting no longer exists on :class:`~gemseo.post.dataset.scatter.Scatter`,
so this port follows the stock matplotlib backend instead, which only draws a
single-color scatter plot with an optional trend line.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from gemseo.post.dataset._trend import TREND_FUNCTIONS
from gemseo.post.dataset._trend import Trend
from gemseo.post.dataset.plots._plotly.plot import PlotlyPlot

if TYPE_CHECKING:
    from numpy.typing import ArrayLike
    from plotly.graph_objs import Figure


class Scatter(PlotlyPlot):
    """A scatter plot based on plotly."""

    def _create_figure(
        self,
        fig: Figure,
        x_values: ArrayLike,
        y_values: ArrayLike,
    ) -> Figure:
        """
        Args:
            x_values: The values of the points on the x-axis.
            y_values: The values of the points on the y-axis.
        """  # ruff: ignore[missing-blank-line-after-summary, multi-line-summary-first-line, missing-terminal-punctuation]
        fig.add_scatter(
            x=x_values.ravel(),
            y=y_values.ravel(),
            mode="markers",
            marker={"color": self._common_settings.color},
            showlegend=False,
        )

        trend_function_creator = self._specific_settings.trend
        if trend_function_creator != Trend.NONE:
            if not isinstance(trend_function_creator, Callable):
                trend_function_creator = TREND_FUNCTIONS[trend_function_creator]

            indices = x_values[:, 0].argsort()
            x_sorted = x_values[indices]
            y_sorted = y_values[indices]
            trend_function = trend_function_creator(x_sorted[:, 0], y_sorted[:, 0])
            fig.add_scatter(
                x=x_sorted.ravel(),
                y=trend_function(x_sorted).ravel(),
                mode="lines",
                line={"color": "gray", "dash": "dash"},
                showlegend=False,
            )

        fig.update_layout(
            title=self._common_settings.title,
            xaxis_title=self._common_settings.xlabel,
            yaxis_title=self._common_settings.ylabel,
        )
        return fig
