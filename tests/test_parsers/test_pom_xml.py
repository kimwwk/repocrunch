"""Tests for pom.xml parser."""

from repocrunch.parsers.pom_xml import parse_pom_xml


def test_basic_parsing(sample_pom_xml):
    result = parse_pom_xml(sample_pom_xml)
    assert "org.springframework.boot:spring-boot-starter-web" in result.direct
    assert "com.google.guava:guava" in result.direct
    assert len(result.direct) == 2


def test_test_scope(sample_pom_xml):
    result = parse_pom_xml(sample_pom_xml)
    assert "org.junit.jupiter:junit-jupiter" in result.test
    assert len(result.test) == 1


def test_no_namespace():
    content = """<?xml version="1.0"?>
<project>
    <dependencies>
        <dependency>
            <groupId>commons-io</groupId>
            <artifactId>commons-io</artifactId>
            <version>2.15.0</version>
        </dependency>
    </dependencies>
</project>
"""
    result = parse_pom_xml(content)
    assert "commons-io:commons-io" in result.direct
    assert len(result.direct) == 1


def test_empty():
    content = """<?xml version="1.0"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>empty</artifactId>
</project>
"""
    result = parse_pom_xml(content)
    assert result.direct == []
    assert result.test == []


def test_invalid_xml():
    result = parse_pom_xml("not xml at all")
    assert result.direct == []
    assert result.test == []
