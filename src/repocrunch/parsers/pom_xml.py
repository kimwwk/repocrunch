"""Parse Maven pom.xml for Java dependencies."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class PomXmlResult:
    direct: list[str]
    test: list[str]


def parse_pom_xml(content: str) -> PomXmlResult:
    """Parse pom.xml, return direct and test-scoped dependencies."""
    direct: list[str] = []
    test: list[str] = []

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return PomXmlResult(direct=direct, test=test)

    # Detect Maven namespace (e.g., xmlns="http://maven.apache.org/POM/4.0.0")
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    deps_tag = f"{ns}dependencies"
    dep_tag = f"{ns}dependency"
    group_tag = f"{ns}groupId"
    artifact_tag = f"{ns}artifactId"
    scope_tag = f"{ns}scope"

    deps_element = root.find(deps_tag)
    if deps_element is None:
        return PomXmlResult(direct=direct, test=test)

    for dep in deps_element.findall(dep_tag):
        group_el = dep.find(group_tag)
        artifact_el = dep.find(artifact_tag)
        if group_el is None or artifact_el is None:
            continue
        group_id = group_el.text or ""
        artifact_id = artifact_el.text or ""
        if not group_id or not artifact_id:
            continue

        name = f"{group_id}:{artifact_id}"
        scope_el = dep.find(scope_tag)
        scope = (scope_el.text or "").strip().lower() if scope_el is not None else ""

        if scope == "test":
            test.append(name)
        else:
            direct.append(name)

    return PomXmlResult(direct=direct, test=test)
