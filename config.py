"""Configuration helpers for path and small environment utilities.

Provides `get_data_dir()` and `get_db_path()` used by the local
JSON-backed store and tests. The location can be overridden by
setting the `SCHOOL_DATA_DIR` environment variable.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def get_data_dir() -> Path:
	"""Return the Path to the data directory.

	Priority:
	- `SCHOOL_DATA_DIR` environment variable (if set)
	- a `data/` directory next to the project root
	"""
	env = os.getenv("SCHOOL_DATA_DIR")
	if env:
		return Path(env)
	# default to `data` folder next to this file
	project_root = Path(__file__).resolve().parent
	return project_root / "data"


def get_db_path(filename: Optional[str] = None) -> Path:
	"""Return the Path to the JSON DB file inside the data directory.

	Defaults to `db.json` unless `filename` is provided.
	"""
	filename = filename or "db.json"
	return get_data_dir() / filename
