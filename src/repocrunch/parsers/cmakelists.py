"""Parse CMakeLists.txt for C/C++ dependencies."""

from __future__ import annotations

import re


# Match: find_package(PackageName ...) — extract the first argument
_FIND_PACKAGE_RE = re.compile(
    r"""find_package\s*\(\s*(\w+)""", re.IGNORECASE
)


def parse_cmakelists(content: str) -> list[str]:
    """Parse CMakeLists.txt, return list of package names from find_package calls."""
    deps: list[str] = []
    seen: set[str] = set()

    for match in _FIND_PACKAGE_RE.finditer(content):
        name = match.group(1)
        name_lower = name.lower()
        if name_lower not in seen:
            seen.add(name_lower)
            deps.append(name)

    return deps
