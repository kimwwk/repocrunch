"""Tests for requirements.txt parser."""

from repocrunch.parsers.requirements_txt import parse_requirements_txt


def test_basic_parsing(sample_requirements_txt):
    result = parse_requirements_txt(sample_requirements_txt)
    assert "flask" in result
    assert "requests" in result
    assert "sqlalchemy" in result
    assert "jinja2" in result
    assert len(result) == 4


def test_skips_comments_and_flags(sample_requirements_txt):
    result = parse_requirements_txt(sample_requirements_txt)
    assert not any(r.startswith("#") for r in result)
    assert not any(r.startswith("-") for r in result)


def test_empty():
    assert parse_requirements_txt("") == []
    assert parse_requirements_txt("# just comments\n") == []


def test_pinned_versions():
    result = parse_requirements_txt("numpy==1.24.0\npandas>=2.0\nscipy~=1.11")
    assert result == ["numpy", "pandas", "scipy"]
