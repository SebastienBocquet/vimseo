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

import pytest

from vimseo.tools.post_tools.plot_parameters import ConstantTrace
from vimseo.tools.post_tools.plot_parameters import LineStyle
from vimseo.tools.post_tools.plot_parameters import Plot
from vimseo.tools.post_tools.plot_parameters import Trace
from vimseo.tools.post_tools.plot_parameters import create_plot
from vimseo.tools.post_tools.plot_parameters import create_trace

pytestmark = pytest.mark.fast


def test_line_style_defaults():
    """A line style left unset resolves everything at rendering time."""
    style = LineStyle()
    assert style.color is None
    assert style.dash is None
    assert style.width is None
    assert style.marker is None


def test_trace_get_label_defaults_to_ordinate_name():
    assert Trace(y="y0").get_label() == "y0"
    assert Trace(y="y0", label="custom").get_label() == "custom"


def test_constant_trace_get_label_defaults_to_value():
    assert ConstantTrace(value=0.5).get_label() == "0.5"
    assert ConstantTrace(value="x", label="lbl").get_label() == "lbl"


def test_plot_from_variable_names_builds_traces():
    plot = Plot.from_variable_names(("x", "y0", "y1"))
    assert plot.x == "x"
    assert plot.traces == [Trace(y="y0"), Trace(y="y1")]


@pytest.mark.parametrize("variable_names", [(), ("x",)])
def test_plot_from_variable_names_too_few_raises(variable_names):
    msg = "A plot shall be defined from at least an abscissa and an ordinate"
    with pytest.raises(ValueError, match=msg):
        Plot.from_variable_names(variable_names)


def test_plot_variable_traces_excludes_constants():
    plot = Plot(
        x="x",
        traces=[Trace(y="y0"), ConstantTrace(value="crit"), Trace(y="y1")],
    )
    assert plot.variable_traces == [Trace(y="y0"), Trace(y="y1")]


def test_plot_variable_names_dedupes_and_uses_trace_abscissa():
    plot = Plot(x="x", traces=[Trace(y="y0"), Trace(y="y1", x="x2")])
    assert plot.variable_names == ["x", "y0", "x2", "y1"]


def test_plot_variable_names_ignores_constant_traces():
    plot = Plot(x="x", traces=[Trace(y="y0"), ConstantTrace(value="crit")])
    assert plot.variable_names == ["x", "y0"]


def test_get_abscissa_name_falls_back_to_plot_x():
    plot = Plot(x="x", traces=[])
    assert plot.get_abscissa_name(Trace(y="y0")) == "x"
    assert plot.get_abscissa_name(Trace(y="y0", x="other")) == "other"


def test_get_name_uses_title_when_present():
    plot = Plot(x="x", traces=[Trace(y="y0")], title="My Title")
    assert plot.get_name() == "my_title"


def test_get_name_single_ordinate_without_title():
    plot = Plot(x="x", traces=[Trace(y="y0")])
    assert plot.get_name() == "y0_vs_x"


def test_get_name_multiple_ordinates_without_title():
    plot = Plot(x="x", traces=[Trace(y="y0"), Trace(y="y1")])
    assert plot.get_name() == "y0_and_1_more_vs_x"


def test_get_name_no_traces():
    plot = Plot(x="x")
    assert plot.get_name() == "_vs_x"


def test_get_file_name_defaults_and_override():
    plot = Plot(x="x", traces=[Trace(y="y0")])
    assert plot.get_file_name() == "y0_vs_x.html"
    assert plot.get_file_name("png") == "y0_vs_x.png"

    named = Plot(x="x", traces=[Trace(y="y0")], file_name="custom.htm")
    assert named.get_file_name("png") == "custom.htm"


def test_create_trace_passthrough():
    trace = Trace(y="y0")
    assert create_trace(trace) is trace
    constant_trace = ConstantTrace(value=1.0)
    assert create_trace(constant_trace) is constant_trace


def test_create_trace_from_mapping_without_value_is_trace():
    trace = create_trace({"y": "y0", "label": "l"})
    assert isinstance(trace, Trace)
    assert trace == Trace(y="y0", label="l")


def test_create_trace_from_mapping_with_value_is_constant_trace():
    trace = create_trace({"value": "x", "label": "l"})
    assert isinstance(trace, ConstantTrace)
    assert trace == ConstantTrace(value="x", label="l")


def test_create_trace_from_mapping_with_dict_style():
    trace = create_trace({"y": "y0", "style": {"color": "red"}})
    assert trace == Trace(y="y0", style=LineStyle(color="red"))


def test_create_trace_from_mapping_with_line_style_instance():
    style = LineStyle(color="blue")
    trace = create_trace({"y": "y0", "style": style})
    assert trace.style is style


def test_create_plot_passthrough():
    plot = Plot(x="x", traces=[Trace(y="y0")])
    assert create_plot(plot) is plot


@pytest.mark.parametrize("definition", [["x", "y0", "y1"], ("x", "y0", "y1")])
def test_create_plot_from_list_and_tuple(definition):
    assert create_plot(definition) == Plot.from_variable_names(("x", "y0", "y1"))


def test_create_plot_from_mapping():
    plot = create_plot({"x": "x", "traces": [{"y": "y0"}], "title": "t"})
    assert plot == Plot(x="x", traces=[Trace(y="y0")], title="t")


def test_create_plot_from_mapping_without_traces_key():
    assert create_plot({"x": "x"}) == Plot(x="x")
