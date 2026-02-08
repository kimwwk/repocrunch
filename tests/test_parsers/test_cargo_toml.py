"""Tests for Cargo.toml parser."""

from repocrunch.parsers.cargo_toml import parse_cargo_toml


def test_basic_parsing(sample_cargo_toml):
    result = parse_cargo_toml(sample_cargo_toml)
    assert "actix-web" in result.direct
    assert "serde" in result.direct
    assert "tokio" in result.direct
    assert len(result.direct) == 3
    assert "criterion" in result.dev
    assert len(result.dev) == 1


def test_workspace_detection(sample_cargo_toml):
    result = parse_cargo_toml(sample_cargo_toml)
    assert result.is_workspace is True


def test_no_workspace():
    content = """
[package]
name = "simple"

[dependencies]
serde = "1"
"""
    result = parse_cargo_toml(content)
    assert result.is_workspace is False
    assert result.direct == ["serde"]


def test_empty():
    result = parse_cargo_toml("[package]\nname = 'empty'\n")
    assert result.direct == []
    assert result.dev == []
