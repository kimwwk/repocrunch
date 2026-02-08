"""Pydantic output models — the schema contract."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


SCHEMA_VERSION = "1"


class CommitFrequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    sporadic = "sporadic"
    inactive = "inactive"


class MaintenanceStatus(str, Enum):
    actively_maintained = "actively_maintained"
    maintained = "maintained"
    lightly_maintained = "lightly_maintained"
    inactive = "inactive"
    archived = "archived"


class RepoSummary(BaseModel):
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    last_commit: datetime | None = None
    age_days: int = 0
    license: str | None = None
    primary_language: str | None = None
    languages: dict[str, float] = Field(default_factory=dict)


class TechStack(BaseModel):
    runtime: str | None = None
    framework: str | None = None
    package_manager: str | None = None
    dependencies: dict[str, int] = Field(default_factory=lambda: {"direct": 0, "dev": 0})
    key_deps: list[str] = Field(default_factory=list)


class Architecture(BaseModel):
    monorepo: bool = False
    docker: bool = False
    ci_cd: list[str] = Field(default_factory=list)
    test_framework: str | None = None
    has_tests: bool = False


class Health(BaseModel):
    open_issues: int = 0
    open_prs: int = 0
    contributors: int = 0
    commit_frequency: CommitFrequency = CommitFrequency.inactive
    maintenance_status: MaintenanceStatus = MaintenanceStatus.inactive


class Security(BaseModel):
    has_env_file: bool = False
    dependabot_enabled: bool = False
    branch_protection: bool = False
    security_policy: bool = False


class RepoAnalysis(BaseModel):
    schema_version: str = SCHEMA_VERSION
    repo: str
    url: str
    analyzed_at: datetime
    summary: RepoSummary = Field(default_factory=RepoSummary)
    tech_stack: TechStack = Field(default_factory=TechStack)
    architecture: Architecture = Field(default_factory=Architecture)
    health: Health = Field(default_factory=Health)
    security: Security = Field(default_factory=Security)
    warnings: list[str] = Field(default_factory=list)
