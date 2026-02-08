"""Parse build.gradle / build.gradle.kts for Java/Kotlin dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class GradleResult:
    direct: list[str]
    test: list[str]


# Configuration names that indicate test scope
_TEST_CONFIGS = {"testImplementation", "testCompileOnly", "testRuntimeOnly", "androidTestImplementation"}

# Configuration names for direct dependencies
_DIRECT_CONFIGS = {
    "implementation", "api", "compileOnly", "runtimeOnly",
    "compile", "runtime",  # legacy Gradle configs
    "kapt", "ksp",  # annotation processors
}

# Pattern for Groovy-style: implementation 'group:artifact:version'
# or: implementation "group:artifact:version"
_GROOVY_RE = re.compile(
    r"""(\w+)\s+['"]([^'"]+:[^'"]+)['"]"""
)

# Pattern for Kotlin DSL: implementation("group:artifact:version")
_KTS_RE = re.compile(
    r"""(\w+)\s*\(\s*['"]([^'"]+:[^'"]+)['"]\s*\)"""
)


def parse_build_gradle(content: str) -> GradleResult:
    """Parse build.gradle or build.gradle.kts, return direct and test deps."""
    direct: list[str] = []
    test: list[str] = []
    seen: set[str] = set()

    for pattern in (_GROOVY_RE, _KTS_RE):
        for match in pattern.finditer(content):
            config = match.group(1)
            coord = match.group(2)

            # Extract group:artifact (drop version if present)
            parts = coord.split(":")
            if len(parts) >= 2:
                name = f"{parts[0]}:{parts[1]}"
            else:
                name = coord

            if name in seen:
                continue
            seen.add(name)

            if config in _TEST_CONFIGS:
                test.append(name)
            elif config in _DIRECT_CONFIGS:
                direct.append(name)

    return GradleResult(direct=direct, test=test)
