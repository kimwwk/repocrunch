# RepoCrunch

Analyze any public GitHub repository into structured JSON. No AI, no LLMs — fully deterministic.

Give it a repo, get back tech stack, dependencies, architecture, health metrics, and security signals in clean, consistent JSON. Use it as a Python library, CLI tool, REST API, or MCP server.

## Quick Start

Requires **Python 3.11+** and [uv](https://github.com/astral-sh/uv).

```bash
# Install
git clone https://github.com/kimwwk/repocrunch.git
cd repocrunch
uv venv && uv pip install -e ".[all]"

# Analyze a repo
repocrunch analyze astral-sh/uv --pretty
```

Or install just what you need:

```bash
uv pip install -e "."          # Library only (httpx + pydantic)
uv pip install -e ".[cli]"     # + CLI
uv pip install -e ".[api]"     # + REST API
uv pip install -e ".[mcp]"     # + MCP server
uv pip install -e ".[all]"     # Everything
```

### Set a GitHub Token (optional)

Without a token you get 60 API calls/hour. With one, 5,000/hour.

```bash
export GITHUB_TOKEN=ghp_...
```

## Usage

### CLI

```bash
repocrunch analyze fastapi/fastapi --pretty          # Full analysis, pretty JSON
repocrunch analyze facebook/react -f tech_stack       # Single field
repocrunch analyze https://github.com/gin-gonic/gin   # Full URL works too
repocrunch serve                                       # Start REST API on :8000
repocrunch mcp                                         # Start MCP server (STDIO)
```

### Python Library

```python
from repocrunch import analyze, analyze_sync

# Async
result = await analyze("fastapi/fastapi")

# Sync
result = analyze_sync("pallets/flask")

print(result.summary.stars)
print(result.tech_stack.framework)
print(result.model_dump_json(indent=2))
```

### REST API

```bash
repocrunch serve

# Then:
curl "http://localhost:8000/analyze?repo=fastapi/fastapi" | python -m json.tool
curl "http://localhost:8000/health"
curl "http://localhost:8000/docs"    # OpenAPI docs
```

### MCP Server (for Claude, Cursor, etc.)

```bash
repocrunch mcp    # Starts STDIO transport
```

## Sample Output

```bash
$ repocrunch analyze pallets/flask --pretty
```

```json
{
  "schema_version": "1",
  "repo": "pallets/flask",
  "url": "https://github.com/pallets/flask",
  "analyzed_at": "2026-02-08T19:07:31Z",
  "summary": {
    "stars": 71143,
    "forks": 16697,
    "watchers": 2092,
    "last_commit": "2026-02-06T21:23:01Z",
    "age_days": 5787,
    "license": "BSD-3-Clause",
    "primary_language": "Python",
    "languages": { "Python": 99.9, "HTML": 0.1 }
  },
  "tech_stack": {
    "runtime": "Python",
    "framework": null,
    "package_manager": "pip",
    "dependencies": { "direct": 6, "dev": 0 },
    "key_deps": ["blinker", "click", "itsdangerous", "jinja2", "markupsafe", "werkzeug"]
  },
  "architecture": {
    "monorepo": false,
    "docker": false,
    "ci_cd": ["GitHub Actions"],
    "test_framework": "pytest",
    "has_tests": true
  },
  "health": {
    "open_issues": 2,
    "open_prs": 0,
    "contributors": 862,
    "commit_frequency": "daily",
    "maintenance_status": "actively_maintained"
  },
  "security": {
    "has_env_file": false,
    "dependabot_enabled": false,
    "branch_protection": false,
    "security_policy": false
  },
  "warnings": [
    "Branch protection status unknown (requires admin access or authenticated request)"
  ]
}
```

## Supported Ecosystems

| Language | Manifest Files | Package Manager Detection |
|----------|---------------|--------------------------|
| JavaScript / TypeScript | `package.json` | npm, yarn, pnpm, bun (from lockfiles) |
| Python | `pyproject.toml`, `requirements.txt` | pip, poetry, uv, pdm, pipenv |
| Rust | `Cargo.toml` | cargo |
| Go | `go.mod` | go |
| Java / Kotlin | `pom.xml`, `build.gradle`, `build.gradle.kts` | maven, gradle |
| Ruby | `Gemfile` | bundler |
| C / C++ | `CMakeLists.txt` | cmake |

Framework detection covers 40+ frameworks across all supported ecosystems (FastAPI, Django, React, Next.js, Spring Boot, Rails, Gin, Actix, and many more).

## What It Detects

| Category | Signals |
|----------|---------|
| **Summary** | Stars, forks, watchers, age, license, languages |
| **Tech Stack** | Runtime, framework, package manager, direct/dev dependency count, key deps |
| **Architecture** | Monorepo, Docker, CI/CD platform, test framework |
| **Health** | Commit frequency (daily/weekly/monthly/sporadic/inactive), maintenance status, contributors, open issues |
| **Security** | `.env` file committed, Dependabot enabled, branch protection, SECURITY.md present |

## Roadmap

Not yet implemented, but planned:

- **Secrets regex scanning** — detect leaked API keys, tokens, passwords in the file tree
- **Architecture type classification** — library vs. application vs. framework
- **API rate limiting** — per-key throttling for the REST API
- **Private repo support** — authenticated analysis of private repositories
- **npm/npx package** — `npx repocrunch analyze owner/repo`
- **Vulnerability scanning** — known CVE detection in dependencies
- **Comparison mode** — side-by-side analysis of multiple repos
- **Historical tracking** — track how a repo's health changes over time
- **PyPI / npm publishing** — `pip install repocrunch` / `npm install repocrunch`
- **Platform deployments** — Apify Store, Smithery, mcp.so, RapidAPI

## License

MIT
