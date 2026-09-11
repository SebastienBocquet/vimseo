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

from vimseo.job_executor.job_scheduler.base_job_scheduler_executor import (
    BaseJobSchedulerExecutor,
)


@pytest.fixture
def executor(tmp_path):
    """A job-scheduler executor pointed at a temporary job directory."""
    job_executor = BaseJobSchedulerExecutor("cmd")
    job_executor._job_directory = tmp_path
    job_executor._job_name = "job"
    return job_executor


def test_convergence_source_directory_falls_back_before_scheduler_directory_is_set(
    executor, tmp_path
):
    """Before the scheduler directory is known, convergence reads the job directory."""
    assert executor._convergence_source_directory() == tmp_path


def test_convergence_source_directory_prefers_scheduler_directory_once_set(
    executor, tmp_path
):
    """Once the scheduler-side directory is known, convergence reads it instead."""
    scheduler_dir = tmp_path / "scheduler_side"
    executor._job_scheduler_job_directory = scheduler_dir

    assert executor._convergence_source_directory() == scheduler_dir
