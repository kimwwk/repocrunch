"""Tests for CMakeLists.txt parser."""

from repocrunch.parsers.cmakelists import parse_cmakelists


def test_basic_parsing(sample_cmakelists):
    result = parse_cmakelists(sample_cmakelists)
    assert "Boost" in result
    assert "OpenSSL" in result
    assert "Qt6" in result
    assert "GTest" in result
    assert len(result) == 4


def test_case_insensitive():
    content = """
FIND_PACKAGE(Eigen3 REQUIRED)
find_package(OpenCV REQUIRED)
"""
    result = parse_cmakelists(content)
    assert "Eigen3" in result
    assert "OpenCV" in result


def test_empty():
    result = parse_cmakelists("cmake_minimum_required(VERSION 3.10)\nproject(Empty)\n")
    assert result == []


def test_no_duplicates():
    content = """
find_package(Boost REQUIRED)
find_package(Boost COMPONENTS filesystem)
"""
    result = parse_cmakelists(content)
    assert len(result) == 1
    assert "Boost" in result
