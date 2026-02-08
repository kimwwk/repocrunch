"""Parse pyproject.toml for Python dependencies (PEP 621 + Poetry)."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass


@dataclass
class PyprojectResult:
    direct: list[str]
    dev: list[str]
    package_manager: str | None


def _extract_package_name(spec: str) -> str:
    """Strip PEP 508 version specifiers, extras, and markers."""
    name = re.split(r"[><=!~\[;\s@]", spec)[0]
    return name.strip().lower()


def parse_pyproject_toml(content: str) -> PyprojectResult:
    data = tomllib.loads(content)

    direct: list[str] = []
    dev: list[str] = []
    pm: str | None = None

    # PEP 621 format
    project = data.get("project", {})
    for dep in project.get("dependencies", []):
        name = _extract_package_name(dep)
        if name:
            direct.append(name)

    # PEP 621 optional-dependencies (look for dev/test groups)
    opt_deps = project.get("optional-dependencies", {})
    for group_name in ("dev", "test", "testing", "development"):
        for dep in opt_deps.get(group_name, []):
            name = _extract_package_name(dep)
            if name:
                dev.append(name)

    # Poetry format
    poetry = data.get("tool", {}).get("poetry", {})
    if poetry:
        for dep in poetry.get("dependencies", {}):
            if dep.lower() != "python":
                direct.append(dep.lower())
        for group_data in poetry.get("group", {}).values():
            for dep in group_data.get("dependencies", {}):
                dev.append(dep.lower())
        # Legacy poetry dev-dependencies
        for dep in poetry.get("dev-dependencies", {}):
            dev.append(dep.lower())

    # Detect package manager from build-system
    build_backend = data.get("build-system", {}).get("build-backend", "")
    if "poetry" in build_backend:
        pm = "poetry"
    elif "hatchling" in build_backend or "hatch" in build_backend:
        pm = "pip"
    elif "setuptools" in build_backend:
        pm = "pip"
    elif "flit" in build_backend:
        pm = "pip"
    elif "pdm" in build_backend:
        pm = "pdm"

    return PyprojectResult(direct=direct, dev=dev, package_manager=pm)
