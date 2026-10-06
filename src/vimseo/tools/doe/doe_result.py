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

from dataclasses import dataclass
from json import dumps
from typing import TYPE_CHECKING
from typing import ClassVar

from gemseo.datasets.dataset import Dataset
from gemseo.datasets.io_dataset import IODataset
from gemseo.utils.string_tools import MultiLineString
from pydantic import Field

from vimseo.core.model_metadata import MetaDataNames
from vimseo.tools.base_tool import BaseResult
from vimseo.tools.doe.doe_plots import create_curve_figures
from vimseo.tools.doe.doe_plots import create_scalar_outputs_figure
from vimseo.tools.doe.doe_plots import create_scatter_matrix
from vimseo.tools.doe.doe_plots import get_scalar_names
from vimseo.tools.doe.doe_plots import get_varying_names
from vimseo.tools.result_visualization import BaseVisualizationSettings
from vimseo.utilities.json_grammar_utils import EnhancedJSONEncoder

if TYPE_CHECKING:
    from vimseo.tools.result_visualization import Figure


class DOEVisualizationSettings(BaseVisualizationSettings):
    abscissa_name: str = Field(
        default="",
        description="The name of the input used as abscissa of the parametric study. "
        "If empty, use the only input varying from a sample to another, if any.",
    )
    output_names: tuple[str, ...] = Field(
        default=(),
        description="The names of the outputs to visualize. "
        "If empty, use all the outputs.",
    )


@dataclass
class DOEResult(BaseResult):
    """The result of a DOE."""

    _VISUALIZATION_SETTINGS: ClassVar[type[DOEVisualizationSettings]] = (
        DOEVisualizationSettings
    )

    dataset: Dataset | None = None
    """The dataset resulting from the DOE."""

    def __str__(self):
        msg = MultiLineString()
        msg.add(dumps(self.metadata, sort_keys=True, indent=4, cls=EnhancedJSONEncoder))
        msg.add("")
        msg.add(
            "============================= DOE Tool Results ========================="
        )
        msg.add(str(self.dataset))
        return str(msg)

    def _create_figures(self, settings: DOEVisualizationSettings) -> dict[str, Figure]:
        if self.dataset is None or self.dataset.empty:
            return {}

        from vimseo.tools.post_tools.plot_parameters import create_plot

        data = self.dataset.to_dict_of_arrays(by_group=False)
        group_names = self.dataset.group_names
        input_names = (
            self.dataset.get_variable_names(IODataset.INPUT_GROUP)
            if IODataset.INPUT_GROUP in group_names
            else []
        )
        output_names = list(settings.output_names) or [
            name
            for name in self.dataset.variable_names
            if name not in input_names
            # The metadata of the model, except the CPU time, are not informative.
            and (name not in set(MetaDataNames) or name == MetaDataNames.cpu_time)
        ]

        figures = {}
        scatter_matrix = create_scatter_matrix(
            data, get_scalar_names(data, dict.fromkeys([*input_names, *output_names]))
        )
        if scatter_matrix is not None:
            figures["scatter_matrix"] = scatter_matrix

        abscissa_name = settings.abscissa_name
        if not abscissa_name:
            varying_names = get_varying_names(data, input_names)
            abscissa_name = varying_names[0] if len(varying_names) == 1 else ""

        model = self.metadata.model
        if abscissa_name:
            scalar_output_names = get_scalar_names(data, output_names)
            if scalar_output_names:
                title = f"{abscissa_name} study"
                if model is not None:
                    title = f"{model.name} / {model.load_case.name} - {title}"
                figures[f"scalar_outputs_vs_{abscissa_name}"] = (
                    create_scalar_outputs_figure(
                        data, abscissa_name, scalar_output_names, title
                    )
                )
            labels = [
                f"{abscissa_name} = {value:g}" for value in data[abscissa_name][:, 0]
            ]
        else:
            labels = [f"sample {i}" for i in range(len(self.dataset))]

        if model is not None and model.plots:
            figures.update(
                create_curve_figures(
                    {
                        name: values
                        for name, values in data.items()
                        if name in input_names or name in output_names
                    },
                    [create_plot(plot) for plot in model.plots],
                    labels,
                )
            )
        return figures
