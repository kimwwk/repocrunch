FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir ".[mcp]"

EXPOSE 8000

ENTRYPOINT ["python", "-m", "repocrunch.mcp_server"]
