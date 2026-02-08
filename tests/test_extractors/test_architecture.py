"""Tests for architecture extractor."""

from repocrunch.extractors.architecture import extract_architecture


def test_basic_extraction(tree_data):
    result = extract_architecture(tree_data)
    assert result.docker is True
    assert "GitHub Actions" in result.ci_cd
    assert result.has_tests is True


def test_monorepo_detection():
    tree = {"tree": [
        {"path": "lerna.json", "type": "blob"},
        {"path": "packages/a/package.json", "type": "blob"},
        {"path": "packages/b/package.json", "type": "blob"},
        {"path": "packages", "type": "tree"},
    ]}
    result = extract_architecture(tree)
    assert result.monorepo is True


def test_no_docker():
    tree = {"tree": [
        {"path": "src/main.py", "type": "blob"},
    ]}
    result = extract_architecture(tree)
    assert result.docker is False
    assert result.ci_cd == []


def test_test_framework_from_deps():
    tree = {"tree": [
        {"path": "tests/test_main.py", "type": "blob"},
    ]}
    result = extract_architecture(tree, deps=["pytest", "httpx"])
    assert result.test_framework == "pytest"
    assert result.has_tests is True


def test_gitlab_ci():
    tree = {"tree": [
        {"path": ".gitlab-ci.yml", "type": "blob"},
    ]}
    result = extract_architecture(tree)
    assert "GitLab CI" in result.ci_cd


def test_multiple_ci():
    tree = {"tree": [
        {"path": ".github/workflows/test.yml", "type": "blob"},
        {"path": ".travis.yml", "type": "blob"},
    ]}
    result = extract_architecture(tree)
    assert "GitHub Actions" in result.ci_cd
    assert "Travis CI" in result.ci_cd
