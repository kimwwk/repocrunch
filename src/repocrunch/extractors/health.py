"""Extract repository health signals: commit frequency, maintenance status."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from repocrunch.client import GitHubClient
from repocrunch.models import CommitFrequency, Health, MaintenanceStatus


def _classify_commit_frequency(commits: list[dict[str, Any]]) -> CommitFrequency:
    """Classify based on median inter-commit interval from last 100 commits."""
    if not commits:
        return CommitFrequency.inactive

    dates: list[datetime] = []
    for c in commits:
        commit_data = c.get("commit", {}).get("committer", {})
        date_str = commit_data.get("date")
        if date_str:
            dates.append(datetime.fromisoformat(date_str.replace("Z", "+00:00")))

    if len(dates) < 2:
        # Single commit — check how recent
        if dates:
            age = (datetime.now(timezone.utc) - dates[0]).days
            if age < 35:
                return CommitFrequency.monthly
            if age < 180:
                return CommitFrequency.sporadic
        return CommitFrequency.inactive

    dates.sort(reverse=True)
    intervals = [(dates[i] - dates[i + 1]).days for i in range(len(dates) - 1)]
    intervals.sort()
    median = intervals[len(intervals) // 2]

    if median < 2:
        return CommitFrequency.daily
    if median < 8:
        return CommitFrequency.weekly
    if median < 35:
        return CommitFrequency.monthly
    if median < 180:
        return CommitFrequency.sporadic
    return CommitFrequency.inactive


def _classify_maintenance(
    freq: CommitFrequency,
    archived: bool,
    last_commit: datetime | None,
) -> MaintenanceStatus:
    if archived:
        return MaintenanceStatus.archived

    if last_commit:
        days_since = (datetime.now(timezone.utc) - last_commit).days
        if days_since > 365:
            return MaintenanceStatus.inactive

    if freq == CommitFrequency.daily:
        return MaintenanceStatus.actively_maintained
    if freq == CommitFrequency.weekly:
        return MaintenanceStatus.actively_maintained
    if freq == CommitFrequency.monthly:
        return MaintenanceStatus.maintained
    if freq == CommitFrequency.sporadic:
        return MaintenanceStatus.lightly_maintained
    return MaintenanceStatus.inactive


async def extract_health(
    client: GitHubClient,
    owner: str,
    repo: str,
    repo_data: dict[str, Any],
) -> Health:
    commits = await client.get(
        f"/repos/{owner}/{repo}/commits",
        params={"per_page": 100},
    )
    commits = commits or []

    contributor_count = await client.get_contributor_count(owner, repo)

    freq = _classify_commit_frequency(commits)

    pushed_at = repo_data.get("pushed_at")
    last_commit = None
    if pushed_at:
        last_commit = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))

    status = _classify_maintenance(
        freq,
        repo_data.get("archived", False),
        last_commit,
    )

    return Health(
        open_issues=repo_data.get("open_issues_count", 0),
        open_prs=0,  # open_issues_count includes PRs; we'd need separate API call
        contributors=contributor_count,
        commit_frequency=freq,
        maintenance_status=status,
    )
