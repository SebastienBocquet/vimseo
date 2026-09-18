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

from vimseo.job_executor.base_executor import JobExecutor


class _TemplateExecutor(JobExecutor):
    """An executor whose command line is rendered from a jinja template."""

    _COMMAND_TEMPLATE = "run {{ executable }}"


def test_execute_renders_the_template_and_delegates(monkeypatch):
    """``execute`` renders the command template, then hands it to the subprocess."""
    executor = _TemplateExecutor("")
    executor._job_options = {"executable": "solver.exe"}
    calls = []
    monkeypatch.setattr(
        executor,
        "_execute_external_software",
        lambda cmd, check_subprocess: calls.append((cmd, check_subprocess)) or 0,
    )

    result = executor.execute(check_subprocess=True)

    assert executor.command_line == "run solver.exe"
    assert calls == [(["run", "solver.exe"], True)]
    assert result == 0


def test_fetch_convergence_safely_swallows_errors():
    """A failure in ``_fetch_convergence`` never propagates out."""
    executor = JobExecutor("")

    def boom() -> None:
        msg = "boom"
        raise RuntimeError(msg)

    executor._fetch_convergence = boom

    executor._fetch_convergence_safely()  # must not raise


@pytest.mark.skip_under_windows
def test_execute_runs_a_real_subprocess(tmp_path):
    """End-to-end smoke test: ``execute`` actually runs the rendered command."""
    executor = _TemplateExecutor("")
    executor._job_options = {"executable": f"echo hi > {tmp_path / 'out.txt'}"}
    executor._COMMAND_TEMPLATE = "sh -c '{{ executable }}'"

    executor.execute(check_subprocess=True)

    assert (tmp_path / "out.txt").read_text().strip() == "hi"
