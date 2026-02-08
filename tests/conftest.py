"""Shared fixtures for tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def repo_data() -> dict:
    return json.loads((FIXTURES / "repo_data.json").read_text())


@pytest.fixture
def tree_data() -> dict:
    return json.loads((FIXTURES / "tree_data.json").read_text())


@pytest.fixture
def sample_package_json() -> str:
    return json.dumps({
        "name": "my-app",
        "version": "1.0.0",
        "packageManager": "pnpm@8.0.0",
        "dependencies": {
            "react": "^18.0.0",
            "next": "^14.0.0",
            "axios": "^1.0.0",
        },
        "devDependencies": {
            "typescript": "^5.0.0",
            "jest": "^29.0.0",
        },
    })


@pytest.fixture
def sample_pyproject_toml() -> str:
    return """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-project"
version = "0.1.0"
dependencies = [
    "fastapi>=0.100",
    "httpx>=0.27",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.1",
]
"""


@pytest.fixture
def sample_requirements_txt() -> str:
    return """
# Core deps
flask>=2.0
requests>=2.28
sqlalchemy>=2.0

# Pinned
jinja2==3.1.2

-e .
--find-links /local/wheels
"""


@pytest.fixture
def sample_cargo_toml() -> str:
    return """
[package]
name = "my-app"
version = "0.1.0"

[dependencies]
actix-web = "4"
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
criterion = "0.5"

[workspace]
members = ["crate-a", "crate-b"]
"""


@pytest.fixture
def sample_go_mod() -> str:
    return """module github.com/myorg/myapp

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/go-sql-driver/mysql v1.7.1
    github.com/redis/go-redis/v9 v9.0.5
)

require (
    // indirect
    github.com/bytedance/sonic v1.9.1
)
"""
