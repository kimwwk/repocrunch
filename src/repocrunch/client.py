"""GitHub API client with auth, rate limiting, ETag caching, and retries."""

from __future__ import annotations

import base64
import logging
import os
from collections import OrderedDict
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
CACHE_MAX = 200


class RateLimitError(Exception):
    def __init__(self, reset_at: int | None = None):
        self.reset_at = reset_at
        super().__init__("GitHub API rate limit exhausted")


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self._external_client = client is not None
        self._client = client or self._make_client()
        self._etag_cache: OrderedDict[str, tuple[str, Any]] = OrderedDict()
        self.rate_remaining: int | None = None
        self.rate_limit: int | None = None
        self.warnings: list[str] = []

    def _make_client(self) -> httpx.AsyncClient:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return httpx.AsyncClient(
            base_url=GITHUB_API,
            headers=headers,
            timeout=30.0,
        )

    def _update_rate_info(self, response: httpx.Response) -> None:
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining is not None:
            self.rate_remaining = int(remaining)
        limit = response.headers.get("X-RateLimit-Limit")
        if limit is not None:
            self.rate_limit = int(limit)
        if self.rate_remaining is not None and self.rate_remaining < 5:
            self.warnings.append(
                f"GitHub API rate limit low: {self.rate_remaining}/{self.rate_limit} remaining"
            )

    def _cache_set(self, url: str, etag: str, data: Any) -> None:
        if len(self._etag_cache) >= CACHE_MAX:
            self._etag_cache.popitem(last=False)
        self._etag_cache[url] = (etag, data)

    async def get(self, path: str, params: dict | None = None) -> Any:
        """GET a GitHub API endpoint. Returns parsed JSON or None on 404."""
        if self.rate_remaining is not None and self.rate_remaining <= 0:
            raise RateLimitError()

        url = path
        headers: dict[str, str] = {}

        cache_key = f"{path}?{params}" if params else path
        if cache_key in self._etag_cache:
            etag, cached_data = self._etag_cache[cache_key]
            headers["If-None-Match"] = etag

        retries = 2
        for attempt in range(retries + 1):
            try:
                response = await self._client.get(url, params=params, headers=headers)
                break
            except httpx.TransportError:
                if attempt == retries:
                    raise
                continue

        self._update_rate_info(response)

        if response.status_code == 304:
            self._etag_cache.move_to_end(cache_key)
            return self._etag_cache[cache_key][1]

        if response.status_code in (401, 404):
            return None

        if response.status_code == 403:
            if self.rate_remaining is not None and self.rate_remaining <= 0:
                reset = response.headers.get("X-RateLimit-Reset")
                raise RateLimitError(int(reset) if reset else None)
            # Permission denied (e.g. branch protection without admin access)
            return None

        response.raise_for_status()

        data = response.json()
        etag = response.headers.get("ETag")
        if etag:
            self._cache_set(cache_key, etag, data)

        return data

    async def get_file_content(self, owner: str, repo: str, path: str) -> str | None:
        """Get decoded file content from a repo. Returns None if not found."""
        data = await self.get(f"/repos/{owner}/{repo}/contents/{path}")
        if data is None:
            return None
        if isinstance(data, dict) and data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return None

    async def get_contributor_count(self, owner: str, repo: str) -> int:
        """Get total contributor count using the Link header pagination trick."""
        response = await self._client.get(
            f"/repos/{owner}/{repo}/contributors",
            params={"per_page": 1, "anon": "true"},
        )
        self._update_rate_info(response)
        if response.status_code != 200:
            return 0

        link = response.headers.get("Link", "")
        if 'rel="last"' in link:
            for part in link.split(","):
                if 'rel="last"' in part:
                    url_part = part.split(";")[0].strip().strip("<>")
                    if "page=" in url_part:
                        page = url_part.split("page=")[-1].split("&")[0]
                        return int(page)
        return len(response.json()) if isinstance(response.json(), list) else 0

    async def close(self) -> None:
        if not self._external_client:
            await self._client.aclose()

    async def __aenter__(self) -> GitHubClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
