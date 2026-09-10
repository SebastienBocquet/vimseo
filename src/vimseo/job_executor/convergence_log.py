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

"""Incremental tailing of solver convergence files (e.g. Abaqus ``.sta`` / ``.msg``)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

MSG_FILTER_MARKERS: tuple[str, ...] = (
    "WARNING",
    "ERROR",
    "HAS NOT CONVERGED",
    "HAS NOT BEEN COMPLETED",
    "CUT BACK",
    "CUTBACK",
    "ATTEMPT",
)
"""Upper-case substrings that mark a significant line of an Abaqus ``.msg`` file."""

CONVERGENCE_MARKER: str = "▓▓"
"""Bold, grep-friendly bracket wrapped around the highlighted convergence lines."""

HIGHLIGHTED_CONVERGENCE_SOURCES: tuple[str, ...] = ("sta",)
"""Convergence-file extensions whose lines get the bold marker. Other sources
(e.g. the far more verbose ``.msg``) get a plain, low-key tag instead."""


def format_convergence_line(ext: str, line: str) -> str:
    """Tag a solver convergence line so it is identifiable in the log stream.

    Lines from a source in :data:`HIGHLIGHTED_CONVERGENCE_SOURCES` are wrapped in
    :data:`CONVERGENCE_MARKER` bars so they stand out from the solver's stdout;
    every other source gets a plain ``"[solver <ext>] "`` prefix.

    Args:
        ext: The convergence-file extension the line came from (e.g. ``"sta"``).
        line: A single, already newline-stripped line of that file.

    Returns:
        The tagged line.
    """
    if ext in HIGHLIGHTED_CONVERGENCE_SOURCES:
        return f"{CONVERGENCE_MARKER} SOLVER[{ext}] {CONVERGENCE_MARKER} {line}"
    return f"[solver {ext}] {line}"


def is_significant_msg_line(line: str) -> bool:
    """Whether an Abaqus ``.msg`` line is worth surfacing when filtering is enabled.

    Args:
        line: A single line of a ``.msg`` file.

    Returns:
        Whether the line contains one of :data:`MSG_FILTER_MARKERS`.
    """
    upper = line.upper()
    return any(marker in upper for marker in MSG_FILTER_MARKERS)


def tail_new_lines(path: Path, cursor: int) -> tuple[list[str], int]:
    """Return the complete lines of ``path`` located after ``cursor``.

    The cursor is a line count: the number of complete lines already consumed on a
    previous call. A trailing line that is not yet terminated by a newline is held
    back (not returned) until it is complete, so half-flushed lines are never emitted.

    Missing, empty or unreadable files yield no new lines. If the file is shorter
    than ``cursor`` (it was truncated or recreated in place), the cursor is reset
    and the file is re-read from the start.

    Args:
        path: The file to read.
        cursor: The number of complete lines already consumed.

    Returns:
        The new complete lines (without trailing newlines) and the updated cursor.
    """
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return [], cursor

    if not text:
        return [], 0

    lines = text.splitlines(keepends=True)
    # Hold back a trailing partial line (no newline yet).
    if lines and not lines[-1].endswith(("\n", "\r")):
        lines = lines[:-1]

    if cursor > len(lines):
        cursor = 0

    new_lines = [line.rstrip("\r\n") for line in lines[cursor:]]
    return new_lines, len(lines)
