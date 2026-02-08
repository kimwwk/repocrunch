"""FastMCP server for RepoCrunch."""

from __future__ import annotations

from fastmcp import FastMCP

from repocrunch.analyzer import analyze_repo

mcp = FastMCP("RepoCrunch", description="Analyze GitHub repos into structured JSON.")


@mcp.tool()
async def analyze_repo_tool(
    repo: str,
    github_token: str | None = None,
) -> dict:
    """Analyze a public GitHub repository and return structured JSON with tech stack, dependencies, architecture, health, and security signals.

    Args:
        repo: GitHub repo as 'owner/repo' or full URL
        github_token: Optional GitHub token for higher rate limits
    """
    result = await analyze_repo(repo, token=github_token)
    return result.model_dump(mode="json")


if __name__ == "__main__":
    mcp.run()
