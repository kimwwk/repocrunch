"""Tests for package.json parser."""

from repocrunch.parsers.package_json import parse_package_json


def test_basic_parsing(sample_package_json):
    result = parse_package_json(sample_package_json)
    assert "react" in result.direct
    assert "next" in result.direct
    assert "axios" in result.direct
    assert len(result.direct) == 3
    assert "jest" in result.dev
    assert "typescript" in result.dev
    assert len(result.dev) == 2


def test_package_manager_detection(sample_package_json):
    result = parse_package_json(sample_package_json)
    assert result.package_manager == "pnpm"


def test_no_package_manager():
    result = parse_package_json('{"dependencies": {"express": "^4.0"}}')
    assert result.package_manager is None
    assert result.direct == ["express"]


def test_empty_deps():
    result = parse_package_json('{"name": "empty"}')
    assert result.direct == []
    assert result.dev == []


def test_yarn_package_manager():
    result = parse_package_json('{"packageManager": "yarn@4.1.0"}')
    assert result.package_manager == "yarn"
