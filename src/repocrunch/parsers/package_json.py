"""Parse package.json for Node.js/TypeScript dependencies."""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class PackageJsonResult:
    direct: list[str]
    dev: list[str]
    package_manager: str | None


def parse_package_json(content: str) -> PackageJsonResult:
    data = json.loads(content)
    direct = list((data.get("dependencies") or {}).keys())
    dev = list((data.get("devDependencies") or {}).keys())

    pm = None
    pm_field = data.get("packageManager", "")
    if pm_field:
        name = pm_field.split("@")[0].lower()
        if name in ("npm", "yarn", "pnpm", "bun"):
            pm = name

    return PackageJsonResult(direct=direct, dev=dev, package_manager=pm)
