"""Tests for GitHub API client."""

import pytest
import httpx
from pytest_httpx import HTTPXMock

from repocrunch.client import GitHubClient, RateLimitError


@pytest.fixture
def github_client(httpx_mock: HTTPXMock):
    client = GitHubClient(token="test-token")
    yield client


@pytest.mark.asyncio
async def test_get_success(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo",
        json={"name": "repo", "full_name": "test/repo"},
        headers={"X-RateLimit-Remaining": "4999", "X-RateLimit-Limit": "5000"},
    )
    async with GitHubClient(token="test") as client:
        data = await client.get("/repos/test/repo")
        assert data["name"] == "repo"
        assert client.rate_remaining == 4999


@pytest.mark.asyncio
async def test_get_404_returns_none(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/missing",
        status_code=404,
        headers={"X-RateLimit-Remaining": "4998", "X-RateLimit-Limit": "5000"},
    )
    async with GitHubClient(token="test") as client:
        data = await client.get("/repos/test/missing")
        assert data is None


@pytest.mark.asyncio
async def test_etag_caching(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo",
        json={"name": "repo"},
        headers={
            "ETag": '"abc123"',
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Limit": "5000",
        },
    )
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo",
        status_code=304,
        headers={"X-RateLimit-Remaining": "4998", "X-RateLimit-Limit": "5000"},
    )

    async with GitHubClient(token="test") as client:
        data1 = await client.get("/repos/test/repo")
        data2 = await client.get("/repos/test/repo")
        assert data1 == data2
        assert data2["name"] == "repo"


@pytest.mark.asyncio
async def test_rate_limit_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo",
        status_code=403,
        headers={
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Limit": "5000",
            "X-RateLimit-Reset": "1700000000",
        },
    )
    async with GitHubClient(token="test") as client:
        with pytest.raises(RateLimitError):
            await client.get("/repos/test/repo")


@pytest.mark.asyncio
async def test_get_file_content(httpx_mock: HTTPXMock):
    import base64
    content = base64.b64encode(b'{"name": "test"}').decode()
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo/contents/package.json",
        json={"content": content, "encoding": "base64"},
        headers={"X-RateLimit-Remaining": "4999", "X-RateLimit-Limit": "5000"},
    )
    async with GitHubClient(token="test") as client:
        data = await client.get_file_content("test", "repo", "package.json")
        assert data == '{"name": "test"}'


@pytest.mark.asyncio
async def test_low_rate_limit_warning(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo",
        json={"name": "repo"},
        headers={"X-RateLimit-Remaining": "3", "X-RateLimit-Limit": "5000"},
    )
    async with GitHubClient(token="test") as client:
        await client.get("/repos/test/repo")
        assert any("rate limit low" in w for w in client.warnings)
