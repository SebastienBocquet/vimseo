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
import subprocess

import pytest

from vimseo.job_executor.base_executor import JobExecutor

_LOGGER_NAME = "vimseo.job_executor.base_executor"

pytestmark = pytest.mark.skip_under_windows


class _StubExecutor(JobExecutor):
    """A non-blocking executor that counts its convergence fetches."""

    _IS_BLOCKING_SUBPROCESS = False
    _CONVERGENCE_SOURCES = ("sta",)
    _CONVERGENCE_POLL_INTERVAL = 0.1

    def __init__(self, command_template: str = ""):
        super().__init__(command_template)
        self.fetch_calls = 0

    def _fetch_convergence(self) -> None:
        self.fetch_calls += 1
        super()._fetch_convergence()


@pytest.fixture
def executor(tmp_path):
    """A stub executor whose job directory is a temporary directory."""
    job_executor = _StubExecutor()
    job_executor._job_directory = tmp_path
    job_executor._job_name = "job"
    return job_executor


def test_post_mortem_fetch_always_runs(executor, tmp_path, caplog):
    """Convergence is fetched once the subprocess exits, without live tailing."""
    cmd = ["sh", "-c", "echo inc 1 >> job.sta"]

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        returncode = executor._execute_external_software(cmd, check_subprocess=False)

    assert returncode == 0
    assert executor.fetch_calls == 1
    assert "SOLVER[sta] ▓▓ inc 1" in caplog.text


def test_live_tail_emits_during_the_run(executor, caplog):
    """With ``convergence_live_tail`` the file is read several times during the solve."""
    executor._user_job_options["convergence_live_tail"] = True
    cmd = ["sh", "-c", "for i in 1 2 3 4 5; do echo inc $i >> job.sta; sleep 0.2; done"]

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        executor._execute_external_software(cmd, check_subprocess=False)

    # one call per poll interval during the ~1s run, plus the final post-exit call
    assert executor.fetch_calls > 1
    assert "SOLVER[sta] ▓▓ inc 1" in caplog.text
    assert "SOLVER[sta] ▓▓ inc 5" in caplog.text


def test_convergence_fetching_can_be_disabled(executor):
    """``activate_convergence_fetching=False`` skips every fetch."""
    executor._user_job_options["convergence_live_tail"] = True
    cmd = ["sh", "-c", "echo inc 1 >> job.sta"]

    executor._execute_external_software(
        cmd, check_subprocess=False, activate_convergence_fetching=False
    )

    assert executor.fetch_calls == 0


def test_a_failing_fetch_does_not_break_the_loop(executor, tmp_path, caplog):
    """An exception raised by the fetch is swallowed; stdout is still logged."""

    def boom() -> None:
        msg = "boom"
        raise RuntimeError(msg)

    executor._fetch_convergence = boom
    cmd = ["sh", "-c", "echo hello world"]

    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        returncode = executor._execute_external_software(cmd, check_subprocess=False)

    assert returncode == 0
    assert "hello world" in caplog.text


def test_returncode_is_propagated(executor):
    """The subprocess return code is returned when it is not checked."""
    cmd = ["sh", "-c", "exit 3"]

    assert executor._execute_external_software(cmd, check_subprocess=False) == 3


def test_returncode_check_raises(executor):
    """A non-zero return code raises when ``check_subprocess`` is set."""
    cmd = ["sh", "-c", "exit 3"]

    with pytest.raises(subprocess.CalledProcessError):
        executor._execute_external_software(cmd, check_subprocess=True)
