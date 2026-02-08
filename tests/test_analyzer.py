"""Tests for the analyzer orchestrator."""

import base64

import httpx
import pytest
from pytest_httpx import HTTPXMock

from repocrunch.analyzer import analyze_repo, parse_repo_input


def test_parse_owner_repo():
    assert parse_repo_input("fastapi/fastapi") == ("fastapi", "fastapi")
    assert parse_repo_input("astral-sh/uv") == ("astral-sh", "uv")


def test_parse_github_url():
    assert parse_repo_input("https://github.com/fastapi/fastapi") == ("fastapi", "fastapi")
    assert parse_repo_input("https://github.com/astral-sh/uv/") == ("astral-sh", "uv")
    assert parse_repo_input("https://github.com/rust-lang/rust.git") == ("rust-lang", "rust")


def test_parse_invalid():
    with pytest.raises(ValueError):
        parse_repo_input("not-valid")
    with pytest.raises(ValueError):
        parse_repo_input("https://gitlab.com/foo/bar")


RATE_HEADERS = {"X-RateLimit-Remaining": "4990", "X-RateLimit-Limit": "5000"}


@pytest.mark.asyncio
async def test_full_analysis(httpx_mock: HTTPXMock, repo_data, tree_data):
    owner, repo_name = "testowner", "test-repo"
    base = f"https://api.github.com/repos/{owner}/{repo_name}"

    httpx_mock.add_response(url=base, json=repo_data, headers=RATE_HEADERS)
    httpx_mock.add_response(url=f"{base}/languages", json={"Python": 50000, "Shell": 2000}, headers=RATE_HEADERS)

    # Tree endpoint has ?recursive=1 query param
    httpx_mock.add_response(
        url=httpx.URL(f"{base}/git/trees/HEAD", params={"recursive": "1"}),
        json=tree_data,
        headers=RATE_HEADERS,
    )

    pyproject_content = base64.b64encode(b"""
[build-system]
build-backend = "hatchling.build"

[project]
dependencies = ["fastapi", "httpx"]

[project.optional-dependencies]
dev = ["pytest"]
""").decode()
    httpx_mock.add_response(
        url=f"{base}/contents/pyproject.toml",
        json={"content": pyproject_content, "encoding": "base64"},
        headers=RATE_HEADERS,
    )

    # requirements.txt is in the tree, so extractor tries to read it too
    req_content = base64.b64encode(b"flask>=2.0\nrequests>=2.28\n").decode()
    httpx_mock.add_response(
        url=f"{base}/contents/requirements.txt",
        json={"content": req_content, "encoding": "base64"},
        headers=RATE_HEADERS,
    )

    # Commits has ?per_page=100
    httpx_mock.add_response(
        url=httpx.URL(f"{base}/commits", params={"per_page": "100"}),
        json=[{"commit": {"committer": {"date": "2026-02-01T10:00:00Z"}}}],
        headers=RATE_HEADERS,
    )

    # Contributors has ?per_page=1&anon=true
    httpx_mock.add_response(
        url=httpx.URL(f"{base}/contributors", params={"per_page": "1", "anon": "true"}),
        json=[{"login": "user1"}],
        headers=RATE_HEADERS,
    )

    httpx_mock.add_response(
        url=f"{base}/branches/main/protection",
        status_code=404,
        headers=RATE_HEADERS,
    )

    result = await analyze_repo(f"{owner}/{repo_name}", token="test-token")

    assert result.repo == f"{owner}/{repo_name}"
    assert result.summary.stars == 1500
    assert result.summary.license == "MIT"
    assert result.summary.primary_language == "Python"
    assert result.tech_stack.runtime == "Python"
    assert result.tech_stack.framework == "FastAPI"
    assert result.architecture.docker is True
    assert result.architecture.has_tests is True
    assert "GitHub Actions" in result.architecture.ci_cd
    assert result.security.dependabot_enabled is True
    assert result.security.security_policy is True


@pytest.mark.asyncio
async def test_repo_not_found(httpx_mock: HTTPXMock):
    base = "https://api.github.com/repos/no/exist"
    httpx_mock.add_response(url=base, status_code=404, headers=RATE_HEADERS)
    httpx_mock.add_response(url=f"{base}/languages", status_code=404, headers=RATE_HEADERS)
    httpx_mock.add_response(
        url=httpx.URL(f"{base}/git/trees/HEAD", params={"recursive": "1"}),
        status_code=404,
        headers=RATE_HEADERS,
    )

    with pytest.raises(ValueError, match="not found"):
        await analyze_repo("no/exist", token="test-token")
