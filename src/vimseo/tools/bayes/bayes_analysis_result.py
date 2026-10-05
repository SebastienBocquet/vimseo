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

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from gemseo.utils.string_tools import MultiLineString
from numpy import array
from numpy import linspace
from numpy import ndarray
from numpy import percentile
from openturns import DeconditionedDistribution
from openturns import Sample
from openturns import dist
from pandas import DataFrame
from prettytable import PrettyTable
from pydantic import Field
from pydantic import PositiveInt

from vimseo.tools.base_tool import BaseResult
from vimseo.tools.result_visualization import BaseVisualizationSettings

if TYPE_CHECKING:
    from matplotlib.figure import Figure

LOGGER = logging.getLogger(__name__)


class BayesVisualizationSettings(BaseVisualizationSettings):
    n_disc: PositiveInt = Field(
        default=100,
        description="The number of points discretizing the observed variable "
        "to plot the posterior predictive distribution.",
    )
    variable_name: str = Field(
        default="",
        description="The name of the observed variable, used as axis label.",
    )


@dataclass
class BayesAnalysisResult(BaseResult):
    """The result of a Bayesian inference."""

    _VISUALIZATION_SETTINGS: ClassVar[type[BayesVisualizationSettings]] = (
        BayesVisualizationSettings
    )

    data: ndarray | None = None
    """The data from which the inference is carried out."""

    raw_samples: ndarray | None = None
    """The MCMC samples without burnin or thining."""

    thin_number: int | None = None
    """The thining number to ensure independency between the posterior samples."""

    ndim: int | None = None
    """The dimension of the calibration problem."""

    processed_samples: ndarray | None = None
    """The MCMC samples after burnin or thining."""

    posterior_predictive: DeconditionedDistribution | None = None
    """The posterior predictive distribution useful to perform uncertainty
    propagation."""

    lppd: float = None
    """Twice the opposite of the lppd, a Bayesian validation criterion."""

    ml: float = None
    """Twice the opposite of the log marginal likelihood, a Bayesian validation
    criterion."""

    def _get_likelihood_distribution(self):
        """Return the probabilistic model which is calibrated."""
        return getattr(dist, self.metadata.settings["likelihood_dist"])()

    def get_parameter_names(self) -> list[str]:
        """Return the names of the parameters of the probabilistic model."""
        return list(self._get_likelihood_distribution().getParameterDescription())

    def plot_posterior_distribution(self) -> Figure:
        """Plot the posterior distribution of the parameters.

        Returns:
            The histograms of the parameters and their pairwise scatter plots.
        """
        from matplotlib.pyplot import subplots

        ndim = self.ndim
        parameter_names = self.get_parameter_names()
        fig, axes = subplots(ndim, ndim, squeeze=False)
        for i in range(ndim):
            for j in range(ndim):
                if i == j:
                    axes[i, i].hist(self.processed_samples[:, i])
                    axes[i, i].set_xlabel(parameter_names[i])
                elif i > j:
                    axes[i, j].scatter(
                        self.processed_samples[:, i], self.processed_samples[:, j]
                    )
                    axes[i, j].set_xlabel(parameter_names[i])
                    axes[i, j].set_ylabel(parameter_names[j])
                else:
                    axes[i, j].set_axis_off()
        return fig

    def plot_predictive_distribution(
        self, n_disc: int = 100, variable_name: str = "", **options: Any
    ) -> Figure:
        """Plot the posterior predictive distribution versus the data.

        Args:
            n_disc: The number of points discretizing the observed variable.
            variable_name: The name of the observed variable, used as axis label.
            **options: The options of the plot of the distribution.

        Returns:
            The histogram of the data and the posterior predictive distribution.
        """
        from matplotlib.pyplot import subplots

        data = array(self.data).ravel()
        x_disc = linspace(0.1 * min(data), 2 * max(data), num=n_disc)
        pdf = array(
            self.posterior_predictive.computePDF(Sample(x_disc.reshape(-1, 1)))
        ).ravel()

        fig, ax = subplots()
        ax1 = ax.twinx()
        ax.hist(data, label="Experimental data")
        ax1.plot(
            x_disc,
            pdf / max(pdf),
            label="posterior predictive distribution for "
            + self._get_likelihood_distribution().getName()
            + " model.",
            **options,
        )
        ax1.set_ylabel("PDF")
        ax1.set_xlabel(variable_name)
        ax1.legend()
        return fig

    def _create_figures(
        self, settings: BayesVisualizationSettings
    ) -> dict[str, Figure]:
        figures = {}
        if self.processed_samples is not None and self.ndim:
            figures["posterior_samples"] = self.plot_posterior_distribution()
        if self.posterior_predictive is not None and self.data is not None:
            figures["posterior_predictive"] = self.plot_predictive_distribution(
                settings.n_disc, settings.variable_name
            )
        return figures

    def _create_tables(self) -> dict[str, DataFrame]:
        tables = {}
        criteria = {
            name: value
            for name, value in (("lppd", self.lppd), ("ml", self.ml))
            if value is not None
        }
        if criteria:
            tables["criteria"] = DataFrame(
                {"value": list(criteria.values())}, index=list(criteria)
            )
        if self.processed_samples is not None and self.processed_samples.size:
            samples = self.processed_samples.reshape(len(self.processed_samples), -1)
            try:
                index = self.get_parameter_names()
            except (KeyError, AttributeError, TypeError):
                index = None
            if index is None or len(index) != samples.shape[1]:
                index = [f"parameter_{i}" for i in range(samples.shape[1])]
            tables["posterior"] = DataFrame(
                {
                    "mean": samples.mean(axis=0),
                    "std": samples.std(axis=0),
                    "percentile_5": percentile(samples, 5, axis=0),
                    "median": percentile(samples, 50, axis=0),
                    "percentile_95": percentile(samples, 95, axis=0),
                },
                index=index,
            )
        return tables


@dataclass
class PosteriorChecks:
    lppd: float
    """Twice the opposite of the lppd, a Bayesian validation criterion."""

    ml: float
    """Twice the opposite of the log marginal likelihood, a Bayesian validation
    criterion."""

    model: str
    """The model whose results are to be plotted."""

    posterior_predictive: DeconditionedDistribution
    """The posterior predictive distribution useful to perform uncertainty
    propagation."""

    def __init__(self, result: BayesAnalysisResult) -> None:

        self.ml = result.ml

        self.lppd = result.lppd

        self.posterior_predictive = result.posterior_predictive

        self.model = result.metadata.settings["likelihood_dist"]

    def __str__(self):
        text = MultiLineString()
        text.add("Bayesian verification indices for " + self.model + " model.")

        table = PrettyTable(["lppd", "ml"])

        table.add_row([
            self.lppd,
            self.ml,
        ])
        text.add(table.get_string())
        return str(text)
