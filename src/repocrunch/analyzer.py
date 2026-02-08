"""Orchestrator: parse input → gather data → run extractors → assemble result."""

from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone

from repocrunch.client import GitHubClient
from repocrunch.extractors.architecture import extract_architecture
from repocrunch.extractors.health import extract_health
from repocrunch.extractors.metadata import extract_metadata
from repocrunch.extractors.security import extract_security
from repocrunch.extractors.tech_stack import extract_tech_stack
from repocrunch.models import RepoAnalysis


def parse_repo_input(raw: str) -> tuple[str, str]:
    """Parse 'owner/repo' or a GitHub URL into (owner, repo)."""
    raw = raw.strip().rstrip("/")

    # Full URL
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?$", raw)
    if match:
        return match.group(1), match.group(2)

    # owner/repo shorthand
    match = re.match(r"^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)$", raw)
    if match:
        return match.group(1), match.group(2)

    raise ValueError(f"Cannot parse repo input: {raw!r}. Use 'owner/repo' or a GitHub URL.")


async def analyze_repo(
    repo_input: str,
    token: str | None = None,
    client: GitHubClient | None = None,
) -> RepoAnalysis:
    """Analyze a GitHub repo and return structured results."""
    owner, repo = parse_repo_input(repo_input)
    warnings: list[str] = []

    owns_client = client is None
    if owns_client:
        client = GitHubClient(token=token)

    try:
        # Phase 1: parallel fetch of repo metadata, languages, and file tree
        repo_data, languages, tree_data = await asyncio.gather(
            client.get(f"/repos/{owner}/{repo}"),
            client.get(f"/repos/{owner}/{repo}/languages"),
            client.get(f"/repos/{owner}/{repo}/git/trees/HEAD", params={"recursive": "1"}),
        )

        if repo_data is None:
            raise ValueError(f"Repository not found: {owner}/{repo}")

        tree_data = tree_data or {"tree": []}
        languages = languages or {}
        primary_language = repo_data.get("language")

        # Phase 2: parallel extraction (async extractors run concurrently)
        summary = extract_metadata(repo_data, languages)

        tech_stack, health, security = await asyncio.gather(
            extract_tech_stack(client, owner, repo, tree_data, primary_language),
            extract_health(client, owner, repo, repo_data),
            extract_security(client, owner, repo, tree_data, repo_data, warnings),
        )

        # Architecture is sync — run after tech_stack so we have deps for test detection
        architecture = extract_architecture(tree_data, tech_stack.key_deps)

        # Collect client warnings
        warnings.extend(client.warnings)

        return RepoAnalysis(
            repo=f"{owner}/{repo}",
            url=f"https://github.com/{owner}/{repo}",
            analyzed_at=datetime.now(timezone.utc),
            summary=summary,
            tech_stack=tech_stack,
            architecture=architecture,
            health=health,
            security=security,
            warnings=warnings,
        )
    finally:
        if owns_client:
            await client.close()
