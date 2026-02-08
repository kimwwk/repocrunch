"""Parse Ruby Gemfile for dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class GemfileResult:
    direct: list[str]
    dev: list[str]


# Match: gem 'name' or gem "name" (with optional version/options after)
_GEM_RE = re.compile(r"""^\s*gem\s+['"]([^'"]+)['"]""")

# Match: group :development, :test do  (or any group block)
_GROUP_START_RE = re.compile(r"""^\s*group\s+(.+?)\s+do\s*$""")

_DEV_GROUPS = {"development", "test", "dev"}


def parse_gemfile(content: str) -> GemfileResult:
    """Parse Gemfile, return direct and dev dependencies."""
    direct: list[str] = []
    dev: list[str] = []
    in_dev_group = False
    group_depth = 0

    for line in content.splitlines():
        stripped = line.strip()

        # Skip comments and blank lines
        if not stripped or stripped.startswith("#"):
            continue

        # Check for group block start
        group_match = _GROUP_START_RE.match(stripped)
        if group_match:
            group_depth += 1
            # Parse group symbols like :development, :test
            symbols = re.findall(r":(\w+)", group_match.group(1))
            if any(s in _DEV_GROUPS for s in symbols):
                in_dev_group = True
            continue

        # Check for block end
        if stripped == "end" and group_depth > 0:
            group_depth -= 1
            if group_depth == 0:
                in_dev_group = False
            continue

        # Match gem declaration
        gem_match = _GEM_RE.match(stripped)
        if gem_match:
            name = gem_match.group(1)
            if in_dev_group:
                dev.append(name)
            else:
                direct.append(name)

    return GemfileResult(direct=direct, dev=dev)
