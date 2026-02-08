"""Extract repository metadata (stars, forks, license, languages, age)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from repocrunch.models import RepoSummary


def extract_metadata(
    repo_data: dict[str, Any],
    languages: dict[str, int] | None,
) -> RepoSummary:
    created_at = repo_data.get("created_at")
    age_days = 0
    if created_at:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - created).days

    pushed_at = repo_data.get("pushed_at")
    last_commit = None
    if pushed_at:
        last_commit = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))

    license_info = repo_data.get("license") or {}
    license_name = license_info.get("spdx_id") if isinstance(license_info, dict) else None
    if license_name == "NOASSERTION":
        license_name = None

    lang_pct: dict[str, float] = {}
    if languages:
        total = sum(languages.values())
        if total > 0:
            lang_pct = {
                lang: round(bytes_ / total * 100, 1)
                for lang, bytes_ in sorted(languages.items(), key=lambda x: -x[1])
            }

    return RepoSummary(
        stars=repo_data.get("stargazers_count", 0),
        forks=repo_data.get("forks_count", 0),
        watchers=repo_data.get("subscribers_count", 0),
        last_commit=last_commit,
        age_days=age_days,
        license=license_name,
        primary_language=repo_data.get("language"),
        languages=lang_pct,
    )
