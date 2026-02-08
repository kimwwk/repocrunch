"""Extract lightweight security signals from the file tree and API."""

from __future__ import annotations

from typing import Any

from repocrunch.client import GitHubClient
from repocrunch.models import Security


def _get_tree_paths(tree_data: dict[str, Any]) -> set[str]:
    return {item["path"] for item in tree_data.get("tree", []) if item.get("type") == "blob"}


async def extract_security(
    client: GitHubClient,
    owner: str,
    repo: str,
    tree_data: dict[str, Any],
    repo_data: dict[str, Any],
    warnings: list[str],
) -> Security:
    paths = _get_tree_paths(tree_data)

    has_env = ".env" in paths
    if has_env:
        warnings.append(".env file committed to repository")

    dependabot = (
        ".github/dependabot.yml" in paths
        or ".github/dependabot.yaml" in paths
    )

    security_policy = (
        "SECURITY.md" in paths
        or "security.md" in paths
        or ".github/SECURITY.md" in paths
    )

    # Branch protection — may 404 without admin access
    branch_protection = False
    default_branch = repo_data.get("default_branch", "main")
    protection_data = await client.get(
        f"/repos/{owner}/{repo}/branches/{default_branch}/protection"
    )
    if protection_data is not None:
        branch_protection = True
    else:
        warnings.append(
            "Branch protection status unknown (requires admin access or authenticated request)"
        )

    return Security(
        has_env_file=has_env,
        dependabot_enabled=dependabot,
        branch_protection=branch_protection,
        security_policy=security_policy,
    )
