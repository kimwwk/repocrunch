"""Framework and test framework detection maps."""

from __future__ import annotations

# dependency name → framework label
FRAMEWORK_MAP: dict[str, str] = {
    # Python
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "starlette": "Starlette",
    "tornado": "Tornado",
    "sanic": "Sanic",
    "litestar": "Litestar",
    "aiohttp": "aiohttp",
    "bottle": "Bottle",
    "falcon": "Falcon",
    "quart": "Quart",
    "streamlit": "Streamlit",
    "gradio": "Gradio",
    # Node.js / TypeScript
    "next": "Next.js",
    "react": "React",
    "vue": "Vue.js",
    "angular": "Angular",
    "@angular/core": "Angular",
    "svelte": "Svelte",
    "express": "Express",
    "nestjs": "NestJS",
    "@nestjs/core": "NestJS",
    "nuxt": "Nuxt",
    "remix": "Remix",
    "@remix-run/react": "Remix",
    "gatsby": "Gatsby",
    "astro": "Astro",
    "hono": "Hono",
    "fastify": "Fastify",
    "koa": "Koa",
    "solid-js": "SolidJS",
    "preact": "Preact",
    # Rust
    "actix-web": "Actix Web",
    "axum": "Axum",
    "rocket": "Rocket",
    "warp": "Warp",
    "tide": "Tide",
    "leptos": "Leptos",
    "yew": "Yew",
    "tauri": "Tauri",
    # Go (module paths)
    "github.com/gin-gonic/gin": "Gin",
    "github.com/gofiber/fiber": "Fiber",
    "github.com/labstack/echo": "Echo",
    "github.com/gorilla/mux": "Gorilla Mux",
    "github.com/go-chi/chi": "Chi",
    "github.com/beego/beego": "Beego",
    # Java / Kotlin
    "org.springframework.boot:spring-boot-starter-web": "Spring Boot",
    "io.quarkus:quarkus-core": "Quarkus",
    "io.micronaut:micronaut-core": "Micronaut",
    "io.vertx:vertx-core": "Vert.x",
    "com.typesafe.play:play_2.13": "Play Framework",
    "com.typesafe.play:play_3": "Play Framework",
    "io.ktor:ktor-server-core": "Ktor",
    # Ruby
    "rails": "Rails",
    "sinatra": "Sinatra",
    "hanami": "Hanami",
    # C / C++
    "Boost": "Boost",
    "Qt5": "Qt",
    "Qt6": "Qt",
    "OpenCV": "OpenCV",
    "SFML": "SFML",
}

# dependency name → test framework label
TEST_FRAMEWORK_MAP: dict[str, str] = {
    # Python
    "pytest": "pytest",
    "unittest": "unittest",
    "nose": "nose",
    "nose2": "nose2",
    # Node.js
    "jest": "Jest",
    "mocha": "Mocha",
    "vitest": "Vitest",
    "@playwright/test": "Playwright",
    "cypress": "Cypress",
    "ava": "AVA",
    "tap": "tap",
    # Rust (built-in, detected from tree)
    # Go (built-in testing package)
    # Java / Kotlin
    "junit": "JUnit",
    "org.junit.jupiter:junit-jupiter": "JUnit 5",
    "org.junit.jupiter:junit-jupiter-api": "JUnit 5",
    "junit:junit": "JUnit 4",
    "org.mockito:mockito-core": "Mockito",
    "org.testng:testng": "TestNG",
    # Ruby
    "rspec": "RSpec",
    "rspec-rails": "RSpec",
    "minitest": "Minitest",
}

# Files in tree that indicate test framework
TEST_FILE_PATTERNS: dict[str, str] = {
    "jest.config": "Jest",
    "vitest.config": "Vitest",
    "cypress.config": "Cypress",
    "playwright.config": "Playwright",
    ".mocharc": "Mocha",
    "pytest.ini": "pytest",
    "setup.cfg": "pytest",  # often contains [tool:pytest]
    "conftest.py": "pytest",
}
