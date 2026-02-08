"""Tests for FastAPI REST API."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from repocrunch.api import app
from repocrunch.models import RepoAnalysis, RepoSummary


def _mock_result():
    return RepoAnalysis(
        repo="test/repo",
        url="https://github.com/test/repo",
        analyzed_at=datetime(2026, 2, 7, 12, 0, 0, tzinfo=timezone.utc),
        summary=RepoSummary(stars=100),
    )


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
@patch("repocrunch.api.analyze_repo", new_callable=AsyncMock)
async def test_analyze_endpoint(mock_analyze):
    mock_analyze.return_value = _mock_result()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/analyze", params={"repo": "test/repo"})
        assert response.status_code == 200
        data = response.json()
        assert data["repo"] == "test/repo"
        assert data["summary"]["stars"] == 100


@pytest.mark.asyncio
@patch("repocrunch.api.analyze_repo", new_callable=AsyncMock)
async def test_analyze_not_found(mock_analyze):
    mock_analyze.side_effect = ValueError("Repository not found")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/analyze", params={"repo": "bad/repo"})
        assert response.status_code == 400
