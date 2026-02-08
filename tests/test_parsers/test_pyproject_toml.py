"""Tests for pyproject.toml parser."""

from repocrunch.parsers.pyproject_toml import parse_pyproject_toml


def test_pep621_parsing(sample_pyproject_toml):
    result = parse_pyproject_toml(sample_pyproject_toml)
    assert "fastapi" in result.direct
    assert "httpx" in result.direct
    assert "pydantic" in result.direct
    assert len(result.direct) == 3
    assert "pytest" in result.dev
    assert "ruff" in result.dev


def test_build_backend_detection(sample_pyproject_toml):
    result = parse_pyproject_toml(sample_pyproject_toml)
    assert result.package_manager == "pip"


def test_poetry_format():
    content = """
[tool.poetry]
name = "myproject"

[tool.poetry.dependencies]
python = "^3.11"
django = "^5.0"
celery = "^5.3"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"

[build-system]
build-backend = "poetry.core.masonry.api"
"""
    result = parse_pyproject_toml(content)
    assert "django" in result.direct
    assert "celery" in result.direct
    assert "python" not in result.direct
    assert "pytest" in result.dev
    assert result.package_manager == "poetry"


def test_version_spec_stripping():
    content = """
[project]
dependencies = [
    "requests>=2.28,<3.0",
    "click[extra]>=8.0",
    "boto3~=1.26",
]
"""
    result = parse_pyproject_toml(content)
    assert "requests" in result.direct
    assert "click" in result.direct
    assert "boto3" in result.direct


def test_empty_project():
    result = parse_pyproject_toml("[project]\nname = 'empty'\n")
    assert result.direct == []
    assert result.dev == []
