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

"""Fail a pull request that touches the public API without a changelog fragment.

This is a heuristic safety net, not the primary mechanism: ``CLAUDE.md`` instructs
contributors (humans and agents alike) to add the fragment as part of the change
itself. See ``changelog/fragments/README.md`` for the fragment naming convention.
"""

from __future__ import annotations

import re
import subprocess
import sys

_PUBLIC_DEF_PATTERN = re.compile(r"^[+-]\s*(?:def|class)\s+[A-Za-z]")


def _git_diff_lines(base_sha: str, head_sha: str, *pathspecs: str) -> list[str]:
    return subprocess.run(
        ["git", "diff", "--unified=0", base_sha, head_sha, "--", *pathspecs],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()


def _touches_public_api(base_sha: str, head_sha: str) -> bool:
    lines = _git_diff_lines(base_sha, head_sha, "src/vimseo/*.py", "src/vimseo/**/*.py")
    return any(_PUBLIC_DEF_PATTERN.match(line) for line in lines)


def _has_new_fragment(base_sha: str, head_sha: str) -> bool:
    lines = subprocess.run(
        [
            "git",
            "diff",
            "--name-status",
            base_sha,
            head_sha,
            "--",
            "changelog/fragments/",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return any(
        line.startswith("A") and not line.endswith("README.md") for line in lines
    )


def main(base_sha: str, head_sha: str) -> int:
    """Return 0 if ``head_sha`` needs no changelog fragment relative to ``base_sha``."""
    if not _touches_public_api(base_sha, head_sha):
        print("No public API change detected; no changelog fragment required.")
        return 0

    if _has_new_fragment(base_sha, head_sha):
        print("Public API change detected, and a changelog fragment was added.")
        return 0

    print(
        "This pull request appears to add, remove, or rename a public class, "
        "method, or function in `src/vimseo/` (no leading underscore), but adds "
        "no file under `changelog/fragments/`.\n"
        "Add one -- see `changelog/fragments/README.md` -- or, if this is a false "
        "positive (e.g. the symbol is actually internal), rename it with a "
        "leading underscore instead.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
