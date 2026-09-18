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
from gemseo.core.discipline.base_discipline import BaseDiscipline
from gemseo.core.grammars.factory import GrammarFactory

from vimseo._gemseo_grammar_compat import _search_file_via_mro
from vimseo._gemseo_grammar_compat import apply


class _GrandParent(BaseDiscipline):
    pass


class _Parent(_GrandParent):
    pass


class _Child(_Parent):
    pass


def test_search_file_via_mro_climbs_mro_with_default_directory():
    """With no directory given, the module directory of each MRO class is used.

    ``MockPre_LC1`` has no grammar file of its own: only its parent ``MockPre``
    does, next to the ``mock_components_lc1`` module.
    """
    from vimseo.problems.mock.mock_pre_run_post.mock_components_lc1 import MockPre_LC1

    result = _search_file_via_mro(MockPre_LC1, "input", "")

    assert result.name == "MockPre_input.json"


def test_search_file_via_mro_uses_explicit_directory(tmp_path):
    """When a directory is given, it is used as is instead of the module one."""
    (tmp_path / "_GrandParent_grammar.json").write_text("{}")

    result = _search_file_via_mro(_Child, "grammar", tmp_path)

    assert result == tmp_path / "_GrandParent_grammar.json"


def test_search_file_via_mro_raises_when_not_found(tmp_path):
    with pytest.raises(FileNotFoundError, match=r"_Child_grammar\.json is missing"):
        _search_file_via_mro(_Child, "grammar", tmp_path)


def test_apply_patches_grammar_factory():
    """``apply`` replaces the private search method with the MRO-walking one."""
    apply()

    patched = GrammarFactory.__dict__["_GrammarFactory__search_file"]
    assert patched.__func__ is _search_file_via_mro
