# Copyright (c) 2019 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: XXXXXXXXXXX
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
from __future__ import annotations

import pathlib

if __name__ == "__main__":
    content = pathlib.Path("README.md").read_text()
    content = content.replace("/docs/images", "images")
    pathlib.Path("README_tmp.md").write_text(content)
