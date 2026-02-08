"""Typer CLI for RepoCrunch."""

from __future__ import annotations

import json

import typer

from repocrunch import __version__, analyze_sync

app = typer.Typer(
    name="repocrunch",
    help="Analyze GitHub repos into structured JSON.",
    no_args_is_help=True,
)


@app.command()
def analyze(
    repo: str = typer.Argument(help="GitHub repo as 'owner/repo' or URL"),
    pretty: bool = typer.Option(False, "--pretty", "-p", help="Pretty-print JSON output"),
    field: str | None = typer.Option(None, "--field", "-f", help="Extract a single top-level field"),
    token: str | None = typer.Option(None, "--token", "-t", help="GitHub token (or set GITHUB_TOKEN)"),
) -> None:
    """Analyze a GitHub repository."""
    try:
        result = analyze_sync(repo, token=token)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    data = result.model_dump(mode="json")

    if field:
        if field not in data:
            typer.echo(f"Unknown field: {field}. Available: {', '.join(data.keys())}", err=True)
            raise typer.Exit(1)
        data = data[field]

    indent = 2 if pretty else None
    typer.echo(json.dumps(data, indent=indent, default=str))


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
) -> None:
    """Start the REST API server."""
    try:
        import uvicorn

        from repocrunch.api import app as fastapi_app
    except ImportError:
        typer.echo("Install API extras: pip install repocrunch[api]", err=True)
        raise typer.Exit(1)

    uvicorn.run(fastapi_app, host=host, port=port)


@app.command()
def mcp() -> None:
    """Start the MCP server (STDIO transport)."""
    try:
        from repocrunch.mcp_server import mcp as mcp_app
    except ImportError:
        typer.echo("Install MCP extras: pip install repocrunch[mcp]", err=True)
        raise typer.Exit(1)

    mcp_app.run()


@app.command()
def version() -> None:
    """Print version information."""
    typer.echo(f"repocrunch {__version__}")


if __name__ == "__main__":
    app()
