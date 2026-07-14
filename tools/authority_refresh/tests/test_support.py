from __future__ import annotations

import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path


RUNTIME_DIR = Path(__file__).resolve().parent / "runtime"


@contextmanager
def workspace_temp_directory():
    """Create test scratch space without tempfile's restricted Windows ACL."""
    path = RUNTIME_DIR / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield str(path)
    finally:
        shutil.rmtree(path)
