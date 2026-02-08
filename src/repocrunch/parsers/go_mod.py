"""Parse go.mod for Go dependencies."""

from __future__ import annotations


def parse_go_mod(content: str) -> list[str]:
    """Parse go.mod, return list of module paths."""
    deps: list[str] = []
    in_require = False

    for line in content.splitlines():
        line = line.strip()

        if line.startswith("require ("):
            in_require = True
            continue
        if in_require and line == ")":
            in_require = False
            continue

        if in_require:
            parts = line.split()
            if parts and not parts[0].startswith("//"):
                deps.append(parts[0])
        elif line.startswith("require "):
            parts = line.split()
            if len(parts) >= 2:
                deps.append(parts[1])

    return deps
