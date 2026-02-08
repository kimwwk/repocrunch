"""Extract architecture signals from the file tree."""

from __future__ import annotations

from typing import Any

from repocrunch.detection import TEST_FILE_PATTERNS, TEST_FRAMEWORK_MAP
from repocrunch.models import Architecture


def _get_tree_paths(tree_data: dict[str, Any]) -> set[str]:
    return {item["path"] for item in tree_data.get("tree", []) if item.get("type") == "blob"}


def _detect_monorepo(paths: set[str], tree_data: dict[str, Any]) -> bool:
    dirs = {item["path"] for item in tree_data.get("tree", []) if item.get("type") == "tree"}

    # Workspace indicators
    if "lerna.json" in paths or "pnpm-workspace.yaml" in paths:
        return True

    # Multiple package.json at different levels
    pkg_jsons = [p for p in paths if p.endswith("package.json") and "/" in p]
    if len(pkg_jsons) >= 2:
        return True

    # packages/ or apps/ directories
    if any(d.startswith("packages/") for d in dirs) or any(d.startswith("apps/") for d in dirs):
        return True

    return False


def _detect_docker(paths: set[str]) -> bool:
    return any(
        p == "Dockerfile" or p == "docker-compose.yml" or p == "docker-compose.yaml"
        or p.endswith("/Dockerfile") or p == "compose.yml" or p == "compose.yaml"
        for p in paths
    )


def _detect_ci_cd(paths: set[str]) -> list[str]:
    ci: list[str] = []
    if any(p.startswith(".github/workflows/") for p in paths):
        ci.append("GitHub Actions")
    if ".gitlab-ci.yml" in paths:
        ci.append("GitLab CI")
    if "Jenkinsfile" in paths:
        ci.append("Jenkins")
    if ".circleci/config.yml" in paths or ".circleci/config.yaml" in paths:
        ci.append("CircleCI")
    if ".travis.yml" in paths:
        ci.append("Travis CI")
    if any(p.startswith("azure-pipelines") for p in paths):
        ci.append("Azure Pipelines")
    if "bitbucket-pipelines.yml" in paths:
        ci.append("Bitbucket Pipelines")
    return ci


def _detect_test_framework(paths: set[str], deps: list[str] | None = None) -> tuple[str | None, bool]:
    """Detect test framework and whether tests exist. Returns (framework, has_tests)."""
    framework = None

    # Check deps first
    if deps:
        for dep in deps:
            dep_lower = dep.lower()
            if dep_lower in TEST_FRAMEWORK_MAP:
                framework = TEST_FRAMEWORK_MAP[dep_lower]
                break

    # Check config files in tree
    if not framework:
        for filename, fw in TEST_FILE_PATTERNS.items():
            if any(p.endswith(filename) or p == filename for p in paths):
                framework = fw
                break

    # Check for test directories
    has_tests = any(
        p.startswith("tests/") or p.startswith("test/") or p.startswith("__tests__/")
        or "/tests/" in p or "/test/" in p or "/__tests__/" in p
        or p.endswith("_test.py") or p.endswith("_test.go") or p.endswith("_test.rs")
        or p.endswith(".test.js") or p.endswith(".test.ts") or p.endswith(".test.tsx")
        or p.endswith(".spec.js") or p.endswith(".spec.ts") or p.endswith(".spec.tsx")
        for p in paths
    )

    # Rust/Go have built-in test frameworks
    if has_tests and not framework:
        if any(p.endswith("_test.go") for p in paths):
            framework = "go test"
        elif any(p.endswith("_test.rs") or p.endswith("/tests/") for p in paths):
            framework = "cargo test"

    return framework, has_tests


def extract_architecture(
    tree_data: dict[str, Any],
    deps: list[str] | None = None,
) -> Architecture:
    paths = _get_tree_paths(tree_data)
    test_framework, has_tests = _detect_test_framework(paths, deps)

    return Architecture(
        monorepo=_detect_monorepo(paths, tree_data),
        docker=_detect_docker(paths),
        ci_cd=_detect_ci_cd(paths),
        test_framework=test_framework,
        has_tests=has_tests,
    )
