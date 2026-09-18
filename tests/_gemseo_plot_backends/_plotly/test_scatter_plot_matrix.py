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

from types import SimpleNamespace

from gemseo.datasets.dataset import Dataset
from gemseo.post.dataset.dataset_plot import PlotSettings
from pandas import DataFrame
from plotly.graph_objs import Figure

from vimseo._gemseo_plot_backends._plotly.scatter_plot_matrix import ScatterMatrix


def _make_dataset() -> Dataset:
    df = DataFrame({"x": [0.0, 1.0, 2.0], "y": [1.0, 2.0, 3.0], "c": [0, 1, 0]})
    return Dataset.from_dataframe(df)


def _make_plot(
    dataset, variable_names=(), classifier="", classifier_column=None
) -> ScatterMatrix:
    # ``PlotlyPlot.__init__`` calls ``_create_figure`` itself with ``*specific_data``,
    # so ``classifier_column`` is passed as extra constructor data, not to a method.
    return ScatterMatrix(
        dataset,
        PlotSettings(title="My title"),
        SimpleNamespace(variable_names=variable_names, classifier=classifier),
        classifier_column,
    )


def test_create_figure_defaults_to_all_variables_without_classifier():
    """No ``variable_names`` falls back to every dataset variable; no classifier."""
    plot = _make_plot(_make_dataset())

    (fig,) = plot.figures

    assert isinstance(fig, Figure)
    assert fig.layout.title.text == "My title"


def test_create_figure_with_explicit_variable_names():
    plot = _make_plot(_make_dataset(), variable_names=["x", "y"])

    (fig,) = plot.figures

    assert isinstance(fig, Figure)


def test_create_figure_classifier_already_in_variable_names():
    """The classifier column is reused as is when already among the plotted ones."""
    plot = _make_plot(
        _make_dataset(),
        variable_names=["x", "y", "c"],
        classifier="c",
        classifier_column=("parameters", "c", 0),
    )

    (fig,) = plot.figures

    assert isinstance(fig, Figure)


def test_create_figure_classifier_pulled_from_dataset():
    """A classifier excluded from ``variable_names`` is fetched from the dataset."""
    plot = _make_plot(
        _make_dataset(),
        variable_names=["x", "y"],
        classifier="c",
        classifier_column=("parameters", "c", 0),
    )

    (fig,) = plot.figures

    assert isinstance(fig, Figure)
