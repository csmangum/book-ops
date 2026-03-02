from __future__ import annotations

import subprocess
from pathlib import Path


def changed_paths_since(project_root: Path, since_ref: str) -> list[str]:
    """
    Return changed paths (repo-relative) since git ref.
    Returns empty list on errors.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", since_ref, "--"],
            cwd=str(project_root),
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return []

    if result.returncode != 0:
        return []
    paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return paths
