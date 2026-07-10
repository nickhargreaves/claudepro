FROM python:3.11-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

COPY app/ ./app/
RUN uv sync --no-dev

EXPOSE 8080

# "::" (not "0.0.0.0") — Fly's public edge reaches this fine either way, but
# Fly's private 6PN network (used by the frontend's nginx reverse proxy) is
# IPv6-only, and Linux's IPv6 wildcard also accepts IPv4-mapped connections
# by default, so this is the one binding that satisfies both.
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "::", "--port", "8080"]
