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

"""Tests for PostProcessor.

The check of the output keys against the output grammar uses a minimal fake
post-processor.

The generic PostProcessor._run logic (POSTPROCESS_DESPITE_FAULTY_RUN,
_is_run_faulty(), _can_postprocess(), _postprocess()), and the resulting
_generate_nan_outputs()/_generate_failed_output_data() behavior, are exercised
end-to-end through the MockFaultyRunPost mock model rather than by calling the
private methods directly.
"""

from __future__ import annotations

import numpy as np
import pytest
from gemseo.core.grammars.errors import InvalidDataError
from numpy import array
from numpy import atleast_1d

from vimseo.api import create_model
from vimseo.core.components.post.post_processor import PostProcessor
from vimseo.core.model_metadata import MetaDataNames
from vimseo.utilities.test_utils import check_model_outputs

MODEL_NAME = "MockFaultyRunPost"
LOAD_CASE_NAME = "LC1"


class _FakePostProcessor(PostProcessor):
    """A minimal PostProcessor whose ``_run`` output is set by the test."""

    auto_detect_grammar_files = False

    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.output_grammar.update_from_data({"y1": array([0.0])})
        self.returned_output_data = {"y1": array([1.0]), "error_code": array([0])}

    def _run(self, input_data):
        return self.returned_output_data


def test_execute_passes_when_output_matches_grammar(tmp_wd):
    """No extra keys: execution succeeds and outputs are unaffected."""
    post = _FakePostProcessor(check_subprocess=True)
    data = post.execute()
    assert data["y1"] == pytest.approx(1.0)


def test_execute_raises_on_extra_output_when_check_subprocess(tmp_wd):
    """An output key absent from the grammar must raise, not be silently dropped."""
    post = _FakePostProcessor(check_subprocess=True)
    post.returned_output_data = {
        "y1": array([1.0]),
        "error_code": array([0]),
        "extra_junk": array([1.0]),
    }
    with pytest.raises(InvalidDataError, match="extra_junk"):
        post.execute()


def test_execute_ignores_extra_output_without_check_subprocess(tmp_wd):
    """With check_subprocess=False, the extra key is silently dropped, as in GEMSEO."""
    post = _FakePostProcessor(check_subprocess=False)
    post.returned_output_data = {
        "y1": array([1.0]),
        "error_code": array([0]),
        "extra_junk": array([1.0]),
    }
    data = post.execute()
    assert data["y1"] == pytest.approx(1.0)
    assert "extra_junk" not in data


def test_successful_run_postprocesses_normally(tmp_wd):
    """With a successful run, all outputs are computed normally."""
    check_model_outputs(
        MODEL_NAME,
        LOAD_CASE_NAME,
        input_data={"x1": atleast_1d(3.0), "run_succeeds": atleast_1d(True)},
        expected_outputs={"y1": atleast_1d(6.0), "y2": atleast_1d(9.0)},
        relative_tolerance=1e-6,
    )


def test_faulty_run_without_opt_in_returns_nan_outputs(tmp_wd):
    """By default (``POSTPROCESS_DESPITE_FAULTY_RUN=False``), a faulty run falls
    back to NaN outputs without attempting to postprocess, even though the job
    directory actually holds a usable result file."""
    model = create_model(MODEL_NAME, LOAD_CASE_NAME)
    model.execute({
        "x1": atleast_1d(3.0),
        "run_succeeds": atleast_1d(False),
        "result_file_written": atleast_1d(True),
    })

    output_data = model.get_output_data()
    assert output_data[MetaDataNames.error_code][0] == 1
    assert np.isnan(output_data["y1"]).all()
    assert np.isnan(output_data["y2"]).all()


def test_faulty_run_with_opt_in_recovers_available_outputs(tmp_wd):
    """With ``POSTPROCESS_DESPITE_FAULTY_RUN=True`` and a usable job directory
    (``_can_postprocess()`` returns True), postprocessing is attempted: outputs
    that can be recovered are kept, others fall back to NaN via
    ``_generate_nan_outputs(existing_data=...)``, and the run is not reported as
    an error."""
    model = create_model(MODEL_NAME, LOAD_CASE_NAME)
    model._chain.disciplines[0].POSTPROCESS_DESPITE_FAULTY_RUN = True
    model.execute({
        "x1": atleast_1d(3.0),
        "run_succeeds": atleast_1d(False),
        "result_file_written": atleast_1d(True),
    })

    output_data = model.get_output_data()
    assert output_data[MetaDataNames.error_code][0] == 0
    assert output_data["y1"][0] == pytest.approx(6.0)
    assert np.isnan(output_data["y2"]).all()


def test_faulty_run_with_opt_in_but_unusable_job_directory_returns_nan_outputs(
    tmp_wd,
):
    """With ``POSTPROCESS_DESPITE_FAULTY_RUN=True`` but no usable job directory
    (``_can_postprocess()`` returns False), postprocessing still falls back to
    NaN outputs, via ``_generate_failed_output_data()``."""
    model = create_model(MODEL_NAME, LOAD_CASE_NAME)
    model._chain.disciplines[0].POSTPROCESS_DESPITE_FAULTY_RUN = True
    model.execute({
        "x1": atleast_1d(3.0),
        "run_succeeds": atleast_1d(False),
        "result_file_written": atleast_1d(False),
    })

    output_data = model.get_output_data()
    assert output_data[MetaDataNames.error_code][0] == 1
    assert np.isnan(output_data["y1"]).all()
    assert np.isnan(output_data["y2"]).all()


class _FakePostProcessorAfterRun(PostProcessor):
    """A minimal PostProcessor relying on the default ``_is_run_faulty``."""

    auto_detect_grammar_files = False

    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.output_grammar.update_from_data({"y1": array([0.0])})

    def _postprocess(self, input_data):
        return {"y1": array([1.0]), "error_code": array([0])}


@pytest.mark.parametrize(
    ("upstream_error_code", "is_run_faulty"),
    [(None, False), (0, False), (-1, False), (1, True)],
)
def test_faulty_run_is_read_from_upstream_error_code(
    tmp_wd, upstream_error_code, is_run_faulty
):
    """By default, the RUN stage is faulty when the upstream error code is positive,
    -1 meaning that no upstream component reported an error code."""
    post = _FakePostProcessorAfterRun()
    input_data = (
        {}
        if upstream_error_code is None
        else {"error_code": array([upstream_error_code])}
    )

    output_data = post.execute(input_data)

    assert output_data["error_code"][0] == int(is_run_faulty)
    assert bool(np.isnan(output_data["y1"][0])) is is_run_faulty
