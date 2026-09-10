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

from vimseo.job_executor.convergence_log import CONVERGENCE_MARKER
from vimseo.job_executor.convergence_log import format_convergence_line
from vimseo.job_executor.convergence_log import is_significant_msg_line
from vimseo.job_executor.convergence_log import tail_new_lines


def test_returns_all_lines_on_first_call(tmp_path):
    """The first call returns every complete line and the matching cursor."""
    path = tmp_path / "job.sta"
    path.write_text("inc 1\ninc 2\ninc 3\n")

    lines, cursor = tail_new_lines(path, 0)

    assert lines == ["inc 1", "inc 2", "inc 3"]
    assert cursor == 3


def test_is_incremental(tmp_path):
    """A second call only returns the lines appended since the previous cursor."""
    path = tmp_path / "job.sta"
    path.write_text("inc 1\ninc 2\n")
    _, cursor = tail_new_lines(path, 0)

    path.write_text("inc 1\ninc 2\ninc 3\ninc 4\n")
    lines, cursor = tail_new_lines(path, cursor)

    assert lines == ["inc 3", "inc 4"]
    assert cursor == 4


def test_missing_file_is_silent(tmp_path):
    """A missing file yields no line and leaves the cursor untouched."""
    lines, cursor = tail_new_lines(tmp_path / "absent.sta", 5)

    assert lines == []
    assert cursor == 5


def test_empty_file_resets_cursor(tmp_path):
    """An empty file yields no line and a zero cursor."""
    path = tmp_path / "job.sta"
    path.write_text("")

    lines, cursor = tail_new_lines(path, 3)

    assert lines == []
    assert cursor == 0


def test_truncation_resets_cursor(tmp_path):
    """A file shorter than the cursor is re-read from the start."""
    path = tmp_path / "job.sta"
    path.write_text("only one line\n")

    lines, cursor = tail_new_lines(path, 10)

    assert lines == ["only one line"]
    assert cursor == 1


def test_partial_last_line_is_held_back(tmp_path):
    """A trailing line without a newline is not emitted until it is complete."""
    path = tmp_path / "job.sta"
    path.write_text("inc 1\ninc 2\ninc 3")

    lines, cursor = tail_new_lines(path, 0)

    assert lines == ["inc 1", "inc 2"]
    assert cursor == 2

    path.write_text("inc 1\ninc 2\ninc 3\ninc 4\n")
    lines, cursor = tail_new_lines(path, cursor)

    assert lines == ["inc 3", "inc 4"]
    assert cursor == 4


def test_format_convergence_line_bars_the_highlighted_source():
    """A ``.sta`` line is wrapped in the marker bars and kept verbatim."""
    formatted = format_convergence_line("sta", "     1     2   1  0.300")

    assert (
        formatted
        == f"{CONVERGENCE_MARKER} SOLVER[sta] {CONVERGENCE_MARKER}      1     2   1  0.300"
    )
    assert formatted.endswith("     1     2   1  0.300")


def test_format_convergence_line_plain_tag_for_other_sources():
    """A ``.msg`` line gets the low-key ``[solver msg]`` tag, no marker bars."""
    formatted = format_convergence_line("msg", " ***WARNING: distortion")

    assert formatted == "[solver msg]  ***WARNING: distortion"
    assert CONVERGENCE_MARKER not in formatted


@pytest.mark.parametrize(
    "line",
    [
        " ***WARNING: SOLVER PROBLEM.",
        " ***ERROR: TOO MANY ATTEMPTS",
        " THE ANALYSIS HAS NOT CONVERGED",
        " TIME INCREMENT WILL BE CUT BACK",
        "   INCREMENT     3 STARTS. ATTEMPT NUMBER  2",
    ],
)
def test_is_significant_msg_line_keeps_markers(line):
    """Warning / error / non-convergence / cut-back / attempt lines are kept."""
    assert is_significant_msg_line(line)


@pytest.mark.parametrize(
    "line",
    [
        "  AVERAGE FORCE                       65.7",
        "  LARGEST RESIDUAL FORCE            -2.9E-08   AT NODE 13424",
        "      LINEAR EQUATION SOLVER TYPE         DIRECT SPARSE",
    ],
)
def test_is_significant_msg_line_drops_routine_lines(line):
    """Ordinary residual / parameter lines are dropped."""
    assert not is_significant_msg_line(line)
