"""Extract tech stack: runtime, framework, package manager, dependencies."""

from __future__ import annotations

from typing import Any

from repocrunch.client import GitHubClient
from repocrunch.detection import FRAMEWORK_MAP
from repocrunch.models import TechStack
from repocrunch.parsers.cargo_toml import parse_cargo_toml
from repocrunch.parsers.go_mod import parse_go_mod
from repocrunch.parsers.package_json import parse_package_json
from repocrunch.parsers.pyproject_toml import parse_pyproject_toml
from repocrunch.parsers.requirements_txt import parse_requirements_txt

# Map primary language to runtime label
LANGUAGE_RUNTIME: dict[str, str] = {
    "Python": "Python",
    "JavaScript": "Node.js",
    "TypeScript": "Node.js",
    "Rust": "Rust",
    "Go": "Go",
    "Java": "Java",
    "Kotlin": "Kotlin",
    "Ruby": "Ruby",
    "PHP": "PHP",
    "C#": ".NET",
    "Swift": "Swift",
    "Dart": "Dart",
}


def _get_tree_paths(tree_data: dict[str, Any]) -> set[str]:
    return {item["path"] for item in tree_data.get("tree", []) if item.get("type") == "blob"}


def _detect_framework(deps: list[str]) -> str | None:
    for dep in deps:
        dep_lower = dep.lower()
        if dep_lower in FRAMEWORK_MAP:
            return FRAMEWORK_MAP[dep_lower]
        if dep in FRAMEWORK_MAP:
            return FRAMEWORK_MAP[dep]
    return None


def _detect_pm_from_tree(paths: set[str], language: str | None) -> str | None:
    """Detect package manager from lockfiles in the tree."""
    if "pnpm-lock.yaml" in paths:
        return "pnpm"
    if "yarn.lock" in paths:
        return "yarn"
    if "bun.lockb" in paths or "bun.lock" in paths:
        return "bun"
    if "package-lock.json" in paths:
        return "npm"
    if "poetry.lock" in paths:
        return "poetry"
    if "Pipfile.lock" in paths:
        return "pipenv"
    if "pdm.lock" in paths:
        return "pdm"
    if "uv.lock" in paths:
        return "uv"
    if "Cargo.lock" in paths:
        return "cargo"
    if "go.sum" in paths:
        return "go"
    return None


async def extract_tech_stack(
    client: GitHubClient,
    owner: str,
    repo: str,
    tree_data: dict[str, Any],
    primary_language: str | None,
) -> TechStack:
    paths = _get_tree_paths(tree_data)
    runtime = LANGUAGE_RUNTIME.get(primary_language or "")
    all_direct: list[str] = []
    all_dev: list[str] = []
    pm: str | None = None

    # Determine which manifest to parse based on primary language
    parsed = False

    if primary_language in ("JavaScript", "TypeScript") and "package.json" in paths:
        content = await client.get_file_content(owner, repo, "package.json")
        if content:
            result = parse_package_json(content)
            all_direct.extend(result.direct)
            all_dev.extend(result.dev)
            if result.package_manager:
                pm = result.package_manager
            parsed = True

    elif primary_language == "Python":
        if "pyproject.toml" in paths:
            content = await client.get_file_content(owner, repo, "pyproject.toml")
            if content:
                result = parse_pyproject_toml(content)
                all_direct.extend(result.direct)
                all_dev.extend(result.dev)
                if result.package_manager:
                    pm = result.package_manager
                parsed = True

        if "requirements.txt" in paths:
            content = await client.get_file_content(owner, repo, "requirements.txt")
            if content:
                req_deps = parse_requirements_txt(content)
                if not parsed:
                    all_direct.extend(req_deps)
                parsed = True

    elif primary_language == "Rust" and "Cargo.toml" in paths:
        content = await client.get_file_content(owner, repo, "Cargo.toml")
        if content:
            result = parse_cargo_toml(content)
            all_direct.extend(result.direct)
            all_dev.extend(result.dev)
            parsed = True

    elif primary_language == "Go" and "go.mod" in paths:
        content = await client.get_file_content(owner, repo, "go.mod")
        if content:
            all_direct.extend(parse_go_mod(content))
            parsed = True

    # Fallback: try all known manifests if nothing matched
    if not parsed:
        for manifest, parser_fn in [
            ("package.json", lambda c: (parse_package_json(c).direct, parse_package_json(c).dev)),
            ("pyproject.toml", lambda c: (parse_pyproject_toml(c).direct, parse_pyproject_toml(c).dev)),
            ("requirements.txt", lambda c: (parse_requirements_txt(c), [])),
            ("Cargo.toml", lambda c: (parse_cargo_toml(c).direct, parse_cargo_toml(c).dev)),
            ("go.mod", lambda c: (parse_go_mod(c), [])),
        ]:
            if manifest in paths:
                content = await client.get_file_content(owner, repo, manifest)
                if content:
                    direct, dev = parser_fn(content)
                    all_direct.extend(direct)
                    all_dev.extend(dev)
                    parsed = True
                    break

    if not pm:
        pm = _detect_pm_from_tree(paths, primary_language)

    framework = _detect_framework(all_direct)

    # Key deps: top direct deps (skip very common/boring ones)
    key_deps = all_direct[:10]

    return TechStack(
        runtime=runtime,
        framework=framework,
        package_manager=pm,
        dependencies={"direct": len(all_direct), "dev": len(all_dev)},
        key_deps=key_deps,
    )
