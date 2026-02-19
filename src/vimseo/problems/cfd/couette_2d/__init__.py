from pathlib import Path

import vimseo.problems.cfd.couette_2d as couette_2d_pkg

COUETTE_2D_DIR = Path(couette_2d_pkg.__path__[0]).resolve()
