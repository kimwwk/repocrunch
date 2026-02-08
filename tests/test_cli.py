"""Tests for CLI."""

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from typer.testing import CliRunner

from repocrunch.cli import app
from repocrunch.models import RepoAnalysis, RepoSummary, TechStack

runner = CliRunner()


def _mock_result():
    return RepoAnalysis(
        repo="test/repo",
        url="https://github.com/test/repo",
        analyzed_at=datetime(2026, 2, 7, 12, 0, 0, tzinfo=timezone.utc),
        summary=RepoSummary(stars=100),
        tech_stack=TechStack(runtime="Python"),
    )


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "repocrunch" in result.stdout


@patch("repocrunch.cli.analyze_sync")
def test_analyze_compact(mock_analyze):
    mock_analyze.return_value = _mock_result()
    result = runner.invoke(app, ["analyze", "test/repo"])
    assert result.exit_code == 0
    assert '"repo": "test/repo"' in result.stdout


@patch("repocrunch.cli.analyze_sync")
def test_analyze_pretty(mock_analyze):
    mock_analyze.return_value = _mock_result()
    result = runner.invoke(app, ["analyze", "test/repo", "--pretty"])
    assert result.exit_code == 0
    assert "  " in result.stdout  # indented


@patch("repocrunch.cli.analyze_sync")
def test_analyze_field(mock_analyze):
    mock_analyze.return_value = _mock_result()
    result = runner.invoke(app, ["analyze", "test/repo", "-f", "tech_stack"])
    assert result.exit_code == 0
    assert '"runtime": "Python"' in result.stdout
    assert '"repo"' not in result.stdout


@patch("repocrunch.cli.analyze_sync")
def test_analyze_invalid_field(mock_analyze):
    mock_analyze.return_value = _mock_result()
    result = runner.invoke(app, ["analyze", "test/repo", "-f", "nonexistent"])
    assert result.exit_code == 1


@patch("repocrunch.cli.analyze_sync")
def test_analyze_error(mock_analyze):
    mock_analyze.side_effect = ValueError("Repository not found")
    result = runner.invoke(app, ["analyze", "bad/repo"])
    assert result.exit_code == 1
    assert "not found" in (result.stdout + result.stderr)
