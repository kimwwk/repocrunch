"""Extractors that transform raw GitHub API data into structured models."""

from repocrunch.extractors.architecture import extract_architecture
from repocrunch.extractors.health import extract_health
from repocrunch.extractors.metadata import extract_metadata
from repocrunch.extractors.security import extract_security
from repocrunch.extractors.tech_stack import extract_tech_stack

__all__ = [
    "extract_metadata",
    "extract_tech_stack",
    "extract_architecture",
    "extract_health",
    "extract_security",
]
