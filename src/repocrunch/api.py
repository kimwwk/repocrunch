"""FastAPI REST API for RepoCrunch."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from repocrunch import __version__
from repocrunch.analyzer import analyze_repo
from repocrunch.client import RateLimitError

app = FastAPI(
    title="RepoCrunch",
    version=__version__,
    description="Analyze GitHub repos into structured JSON.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/analyze")
async def analyze(
    repo: str = Query(description="GitHub repo as 'owner/repo' or URL"),
    github_token: str | None = Query(None, description="GitHub token for higher rate limits"),
):
    try:
        result = await analyze_repo(repo, token=github_token)
        return result.model_dump(mode="json")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RateLimitError:
        raise HTTPException(status_code=429, detail="GitHub API rate limit exhausted")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "version": __version__}
