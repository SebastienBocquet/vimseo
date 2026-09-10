<!--
 Copyright 2021 IRT Saint Exupery, https://www.irt-saintexupery.com

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

## How to write logs to a file with VIMSEO

To redirect VIMSEO logs to a file, call `vimseo.api.activate_logger` with a `filename`.
A timestamped file name avoids overwriting previous runs.

```python
import logging
from datetime import datetime
from pathlib import Path
from vimseo.api import activate_logger

# Define your working directory
working_directory = Path("path/to/output")
working_directory.mkdir(parents=True, exist_ok=True)

# Generate a unique timestamp down to the millisecond
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S-") + f"{now.microsecond // 1000:03d}"

# Activate the logger
activate_logger(
    level=logging.INFO,
    filename=working_directory / f"log_{timestamp}.txt",
    filemode="w",
)
```

This will create a log file such as `log_2026-06-11_14-32-45-123.txt` in the specified directory.

**Parameters:**

| Parameter | Description | Default |
|---|---|---|
| `level` | Logging verbosity as a `logging` level value. If not provided, the level from the VIMSEO configuration is used | `None` |
| `filename` | Path to the log file. If empty, logs go to the console only | `""` |
| `filemode` | `"w"` to overwrite, `"a"` to append | `"a"` |

> **Note:** By default (`filename=""`), logs are printed to the console only. Providing a
> `filename` adds a file handler; the console output is kept as well. When an Abaqus job
> runs, its convergence files (`.sta`, `.msg`) are surfaced through the same logger, so
> they end up in this file too. The `.sta` progress lines are prefixed with
> `▓▓ SOLVER[sta] ▓▓` so they pop out of the solver's stdout (and are easy to `grep`);
> the more verbose `.msg` lines carry a plain `[solver msg]` tag.
