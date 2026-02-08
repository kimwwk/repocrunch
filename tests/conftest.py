"""Shared fixtures for tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def repo_data() -> dict:
    return json.loads((FIXTURES / "repo_data.json").read_text())


@pytest.fixture
def tree_data() -> dict:
    return json.loads((FIXTURES / "tree_data.json").read_text())


@pytest.fixture
def sample_package_json() -> str:
    return json.dumps({
        "name": "my-app",
        "version": "1.0.0",
        "packageManager": "pnpm@8.0.0",
        "dependencies": {
            "react": "^18.0.0",
            "next": "^14.0.0",
            "axios": "^1.0.0",
        },
        "devDependencies": {
            "typescript": "^5.0.0",
            "jest": "^29.0.0",
        },
    })


@pytest.fixture
def sample_pyproject_toml() -> str:
    return """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-project"
version = "0.1.0"
dependencies = [
    "fastapi>=0.100",
    "httpx>=0.27",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.1",
]
"""


@pytest.fixture
def sample_requirements_txt() -> str:
    return """
# Core deps
flask>=2.0
requests>=2.28
sqlalchemy>=2.0

# Pinned
jinja2==3.1.2

-e .
--find-links /local/wheels
"""


@pytest.fixture
def sample_cargo_toml() -> str:
    return """
[package]
name = "my-app"
version = "0.1.0"

[dependencies]
actix-web = "4"
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
criterion = "0.5"

[workspace]
members = ["crate-a", "crate-b"]
"""


@pytest.fixture
def sample_go_mod() -> str:
    return """module github.com/myorg/myapp

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/go-sql-driver/mysql v1.7.1
    github.com/redis/go-redis/v9 v9.0.5
)

require (
    // indirect
    github.com/bytedance/sonic v1.9.1
)
"""


@pytest.fixture
def sample_pom_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>3.2.0</version>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <version>32.1.3-jre</version>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
"""


@pytest.fixture
def sample_gemfile() -> str:
    return """source 'https://rubygems.org'

gem 'rails', '~> 7.1'
gem 'pg', '~> 1.5'
gem 'puma', '>= 5.0'

group :development, :test do
  gem 'rspec-rails'
  gem 'factory_bot_rails'
end

group :development do
  gem 'web-console'
end

gem 'redis', '~> 5.0'
"""


@pytest.fixture
def sample_build_gradle() -> str:
    return """plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web:3.2.0'
    implementation 'com.google.guava:guava:32.1.3-jre'
    compileOnly 'org.projectlombok:lombok:1.18.30'
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
    testImplementation 'org.mockito:mockito-core:5.7.0'
}
"""


@pytest.fixture
def sample_build_gradle_kts() -> str:
    return """plugins {
    kotlin("jvm") version "1.9.20"
}

dependencies {
    implementation("io.ktor:ktor-server-core:2.3.6")
    implementation("io.ktor:ktor-server-netty:2.3.6")
    testImplementation("io.ktor:ktor-server-tests:2.3.6")
}
"""


@pytest.fixture
def sample_cmakelists() -> str:
    return """cmake_minimum_required(VERSION 3.20)
project(MyApp)

find_package(Boost REQUIRED COMPONENTS filesystem system)
find_package(OpenSSL REQUIRED)
find_package(Qt6 REQUIRED COMPONENTS Core Widgets)
find_package(GTest REQUIRED)

add_executable(myapp main.cpp)
target_link_libraries(myapp Boost::filesystem OpenSSL::SSL Qt6::Core)
"""
