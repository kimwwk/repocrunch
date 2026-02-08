"""Tests for Gemfile parser."""

from repocrunch.parsers.gemfile import parse_gemfile


def test_basic_parsing(sample_gemfile):
    result = parse_gemfile(sample_gemfile)
    assert "rails" in result.direct
    assert "pg" in result.direct
    assert "puma" in result.direct
    assert "redis" in result.direct
    assert len(result.direct) == 4


def test_dev_groups(sample_gemfile):
    result = parse_gemfile(sample_gemfile)
    assert "rspec-rails" in result.dev
    assert "factory_bot_rails" in result.dev
    assert "web-console" in result.dev
    assert len(result.dev) == 3


def test_double_quotes():
    content = """
gem "sinatra", "~> 3.0"
gem "puma"
"""
    result = parse_gemfile(content)
    assert "sinatra" in result.direct
    assert "puma" in result.direct
    assert len(result.direct) == 2


def test_empty():
    result = parse_gemfile("")
    assert result.direct == []
    assert result.dev == []


def test_comments_skipped():
    content = """
# This is a comment
gem 'rails'
# gem 'unused'
"""
    result = parse_gemfile(content)
    assert result.direct == ["rails"]
