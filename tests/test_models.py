"""Tests for Pydantic output models."""

from datetime import datetime, timezone

from repocrunch.models import (
    Architecture,
    CommitFrequency,
    Health,
    MaintenanceStatus,
    RepoAnalysis,
    RepoSummary,
    Security,
    TechStack,
)


def test_repo_analysis_defaults():
    result = RepoAnalysis(
        repo="test/repo",
        url="https://github.com/test/repo",
        analyzed_at=datetime.now(timezone.utc),
    )
    assert result.schema_version == "1"
    assert result.summary.stars == 0
    assert result.tech_stack.dependencies == {"direct": 0, "dev": 0}
    assert result.architecture.monorepo is False
    assert result.health.commit_frequency == CommitFrequency.inactive
    assert result.security.has_env_file is False
    assert result.warnings == []


def test_repo_analysis_serialization():
    result = RepoAnalysis(
        repo="test/repo",
        url="https://github.com/test/repo",
        analyzed_at=datetime(2026, 2, 7, 12, 0, 0, tzinfo=timezone.utc),
        summary=RepoSummary(stars=100, forks=10),
        tech_stack=TechStack(runtime="Python", framework="FastAPI"),
    )
    data = result.model_dump(mode="json")
    assert data["repo"] == "test/repo"
    assert data["summary"]["stars"] == 100
    assert data["tech_stack"]["framework"] == "FastAPI"
    assert data["analyzed_at"] == "2026-02-07T12:00:00Z"


def test_commit_frequency_values():
    assert CommitFrequency.daily.value == "daily"
    assert CommitFrequency.weekly.value == "weekly"
    assert CommitFrequency.inactive.value == "inactive"


def test_maintenance_status_values():
    assert MaintenanceStatus.actively_maintained.value == "actively_maintained"
    assert MaintenanceStatus.archived.value == "archived"
