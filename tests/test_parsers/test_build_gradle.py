"""Tests for build.gradle parser."""

from repocrunch.parsers.build_gradle import parse_build_gradle


def test_groovy_parsing(sample_build_gradle):
    result = parse_build_gradle(sample_build_gradle)
    assert "org.springframework.boot:spring-boot-starter-web" in result.direct
    assert "com.google.guava:guava" in result.direct
    assert "org.projectlombok:lombok" in result.direct
    assert len(result.direct) == 3


def test_groovy_test_deps(sample_build_gradle):
    result = parse_build_gradle(sample_build_gradle)
    assert "org.junit.jupiter:junit-jupiter" in result.test
    assert "org.mockito:mockito-core" in result.test
    assert len(result.test) == 2


def test_kotlin_dsl(sample_build_gradle_kts):
    result = parse_build_gradle(sample_build_gradle_kts)
    assert "io.ktor:ktor-server-core" in result.direct
    assert "io.ktor:ktor-server-netty" in result.direct
    assert len(result.direct) == 2
    assert "io.ktor:ktor-server-tests" in result.test
    assert len(result.test) == 1


def test_empty():
    result = parse_build_gradle("plugins { id 'java' }")
    assert result.direct == []
    assert result.test == []


def test_no_duplicates():
    content = """
    implementation 'com.example:lib:1.0'
    implementation 'com.example:lib:1.0'
"""
    result = parse_build_gradle(content)
    assert len(result.direct) == 1
