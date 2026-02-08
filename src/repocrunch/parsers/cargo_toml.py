"""Parse Cargo.toml for Rust dependencies."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass


@dataclass
class CargoResult:
    direct: list[str]
    dev: list[str]
    is_workspace: bool


def parse_cargo_toml(content: str) -> CargoResult:
    data = tomllib.loads(content)
    direct = list((data.get("dependencies") or {}).keys())
    dev = list((data.get("dev-dependencies") or {}).keys())
    is_workspace = "workspace" in data
    return CargoResult(direct=direct, dev=dev, is_workspace=is_workspace)
