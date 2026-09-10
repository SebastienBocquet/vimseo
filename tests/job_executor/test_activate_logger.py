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

import pytest

from vimseo.api import activate_logger


@pytest.fixture(autouse=True)
def _restore_logging():
    """Restore the console-only logger configuration after each test."""
    yield
    activate_logger(logging.INFO)


def test_filename_adds_a_file_handler(tmp_path):
    """Passing a filename writes the VIMSEO log to that file as well."""
    log_file = tmp_path / "run.log"

    activate_logger(level=logging.INFO, filename=log_file, filemode="w")
    logging.getLogger("vimseo.test").info("hello from vimseo")

    logging.shutdown()
    assert "hello from vimseo" in log_file.read_text()


def test_no_filename_keeps_console_only():
    """Without a filename, the root logger has no file handler."""
    activate_logger(logging.INFO)

    handlers = logging.getLogger().handlers
    assert not any(isinstance(h, logging.FileHandler) for h in handlers)
