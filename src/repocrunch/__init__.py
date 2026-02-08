"""RepoCrunch — Analyze GitHub repos into structured JSON."""

from __future__ import annotations

import asyncio

from repocrunch.analyzer import analyze_repo
from repocrunch.models import SCHEMA_VERSION, RepoAnalysis

__version__ = "0.1.0"
__all__ = ["analyze", "analyze_sync", "RepoAnalysis", "SCHEMA_VERSION", "__version__"]


async def analyze(
    repo: str,
    token: str | None = None,
) -> RepoAnalysis:
    """Analyze a GitHub repo asynchronously."""
    return await analyze_repo(repo, token=token)


def analyze_sync(
    repo: str,
    token: str | None = None,
) -> RepoAnalysis:
    """Analyze a GitHub repo synchronously."""
    return asyncio.run(analyze_repo(repo, token=token))
