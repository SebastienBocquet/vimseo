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

from gemseo.core.grammars.json_grammar import JSONGrammar

from vimseo.utilities.json_grammar_utils import EnhancedJSONEncoder


def test_enhanced_json_encoder_serializes_grammar_defaults():
    """A grammar's ``Defaults`` mapping is serialized as a plain dict."""
    grammar = JSONGrammar("test")
    grammar.update_from_data({"x": 1.0})
    grammar.defaults["x"] = 1.0

    text = json.dumps(grammar.defaults, cls=EnhancedJSONEncoder)

    assert json.loads(text) == {"x": 1.0}
