"""Tests for go.mod parser."""

from repocrunch.parsers.go_mod import parse_go_mod


def test_basic_parsing(sample_go_mod):
    result = parse_go_mod(sample_go_mod)
    assert "github.com/gin-gonic/gin" in result
    assert "github.com/go-sql-driver/mysql" in result
    assert "github.com/redis/go-redis/v9" in result


def test_indirect_deps(sample_go_mod):
    result = parse_go_mod(sample_go_mod)
    assert "github.com/bytedance/sonic" in result


def test_single_require():
    content = "module myapp\ngo 1.21\nrequire github.com/labstack/echo/v4 v4.11.0\n"
    result = parse_go_mod(content)
    assert "github.com/labstack/echo/v4" in result


def test_empty():
    result = parse_go_mod("module myapp\ngo 1.21\n")
    assert result == []
