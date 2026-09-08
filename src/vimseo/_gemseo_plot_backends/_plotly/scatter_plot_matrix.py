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
"""Scatter matrix based on plotly.

Ported from the private gemseo fork this used to depend on (which added it
directly inside ``gemseo.post.dataset.plots._plotly``), since stock gemseo
only ships a matplotlib backend for :class:`~gemseo.post.dataset.scatter_plot_matrix.ScatterMatrix`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import plotly.figure_factory as ff
from gemseo.post.dataset.plots._plotly.plot import PlotlyPlot

if TYPE_CHECKING:
    from plotly.graph_objs import Figure


class ScatterMatrix(PlotlyPlot):
    """Scatter matrix based on plotly."""

    def _create_figure(
        self,
        fig: Figure,
        classifier_column: tuple[str, str, int] | None,
    ) -> Figure:
        """
        Args:
            classifier_column: The column of the dataset used for classification,
                if any.
        """  # ruff: ignore[missing-blank-line-after-summary, multi-line-summary-first-line, missing-terminal-punctuation]
        variable_names = self._specific_settings.variable_names
        if not variable_names:
            variable_names = self._common_dataset.variable_names

        dataframe = self._common_dataset.get_view(variable_names=variable_names).copy()
        dataframe.columns = self._get_variable_names(dataframe.columns)

        index = None
        if classifier_column is not None:
            index = self._get_variable_names([classifier_column])[0]
            if index not in dataframe.columns:
                dataframe[index] = self._common_dataset.get_view(
                    variable_names=[self._specific_settings.classifier]
                ).to_numpy()[:, 0]

        return ff.create_scatterplotmatrix(
            dataframe,
            diag="histogram",
            index=index,
            height=800,
            width=800,
            title=self._common_settings.title,
        )
