"""Parse requirements.txt for Python dependencies."""

from __future__ import annotations

import re


def parse_requirements_txt(content: str) -> list[str]:
    """Parse requirements.txt, return list of package names."""
    deps: list[str] = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[><=!~\[;\s@]", line)[0].strip().lower()
        if name:
            deps.append(name)
    return deps
