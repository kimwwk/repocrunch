"""Tests for health extractor."""

from datetime import datetime, timedelta, timezone

from repocrunch.extractors.health import _classify_commit_frequency, _classify_maintenance
from repocrunch.models import CommitFrequency, MaintenanceStatus


def _make_commits(interval_days: int, count: int = 50):
    """Generate mock commit data with given interval."""
    now = datetime.now(timezone.utc)
    commits = []
    for i in range(count):
        date = now - timedelta(days=i * interval_days)
        commits.append({
            "commit": {
                "committer": {
                    "date": date.isoformat(),
                }
            }
        })
    return commits


def test_daily_frequency():
    commits = _make_commits(interval_days=1)
    assert _classify_commit_frequency(commits) == CommitFrequency.daily


def test_weekly_frequency():
    commits = _make_commits(interval_days=5)
    assert _classify_commit_frequency(commits) == CommitFrequency.weekly


def test_monthly_frequency():
    commits = _make_commits(interval_days=20)
    assert _classify_commit_frequency(commits) == CommitFrequency.monthly


def test_sporadic_frequency():
    commits = _make_commits(interval_days=90)
    assert _classify_commit_frequency(commits) == CommitFrequency.sporadic


def test_inactive_frequency():
    commits = _make_commits(interval_days=200)
    assert _classify_commit_frequency(commits) == CommitFrequency.inactive


def test_empty_commits():
    assert _classify_commit_frequency([]) == CommitFrequency.inactive


def test_maintenance_actively_maintained():
    result = _classify_maintenance(
        CommitFrequency.daily, False,
        datetime.now(timezone.utc) - timedelta(days=1),
    )
    assert result == MaintenanceStatus.actively_maintained


def test_maintenance_archived():
    result = _classify_maintenance(
        CommitFrequency.daily, True,
        datetime.now(timezone.utc),
    )
    assert result == MaintenanceStatus.archived


def test_maintenance_inactive_old_commit():
    result = _classify_maintenance(
        CommitFrequency.monthly, False,
        datetime.now(timezone.utc) - timedelta(days=400),
    )
    assert result == MaintenanceStatus.inactive
