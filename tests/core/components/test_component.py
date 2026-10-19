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

import json

import vimseo.problems.mock.mock_component.mock_component as mc
from vimseo.core.components.base_component import BaseComponent
from vimseo.core.components.component_factory import ComponentFactory
from vimseo.core.model_metadata import MetaDataNames

JOB_NAME = "DummyJobDir"


def test_grammar_from_parent_class_inherit(tmp_wd):
    """Test case where the grammars are inherited from parent classes."""
    factory = ComponentFactory()
    mcc1 = factory.create("MockChildComponent1")
    assert list(mcc1.io.input_grammar.keys()) == ["x1", "x2", "x3"]
    assert list(mcc1.io.output_grammar.keys()) == [
        "y1",
        "y2",
        "y3",
        MetaDataNames.error_code.name,
    ]
    assert mcc1.default_input_data == {"x1": 0.0, "x2": 0.0, "x3": 0.0}


def test_error_code_declared_but_not_required(tmp_wd):
    """A component declares the error code as an optional output, so that an error
    code it returns reaches the model metadata, without forcing it to return one."""
    component = ComponentFactory().create("MockChildComponent1")
    assert MetaDataNames.error_code.name in component.output_grammar
    assert MetaDataNames.error_code.name not in component.output_grammar.required_names

    output_data = component.execute()

    assert MetaDataNames.error_code.name not in output_data


def test_error_code_declared_in_grammar_file_is_kept(tmp_wd, tmp_path):
    """An error code already declared by the grammar file of a component is not
    overridden, so that it stays required."""
    (tmp_path / "ComponentWithErrorCode_input.json").write_text(
        json.dumps({"type": "object", "properties": {}})
    )
    (tmp_path / "ComponentWithErrorCode_output.json").write_text(
        json.dumps({
            "type": "object",
            "required": [MetaDataNames.error_code.name],
            "properties": {
                MetaDataNames.error_code.name: {
                    "type": "array",
                    "items": {"type": "integer"},
                }
            },
        })
    )

    class ComponentWithErrorCode(BaseComponent):
        GRAMMAR_DIRECTORY = tmp_path

        def _run(self, input_data):
            return {}

    component = ComponentWithErrorCode()
    assert MetaDataNames.error_code.name in component.output_grammar.required_names


def test_required_input(tmp_wd):
    """Test case where the required input are checked."""
    mpc3 = mc.MockComponent()
    assert mpc3.input_grammar.required_names == {"x1", "x2", "x3"}
