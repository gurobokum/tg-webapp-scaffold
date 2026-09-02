# syntax=docker/dockerfile:1

FROM docker.io/python:3.13.3-slim-bullseye

LABEL name="GramStack" \
      maintainer="Guro Bokum <jiojiajiu@gmail.com>" \
      org.opencontainers.image.source="https://github.com/gurobokum/gramstack" \
      org.opencontainers.image.description="GramStack backend - full-stack starter for Telegram Mini Apps" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local \
    UV_COMPILE_BYTECODE=1 \
    APP_USER=gramstack \
    APP_HOME=/app

RUN useradd --create-home $APP_USER

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR $APP_HOME

COPY --chown=$APP_USER:$APP_USER uv.lock pyproject.toml ./
RUN uv sync --frozen --no-install-project --no-cache

USER $APP_USER
COPY --chown=$APP_USER:$APP_USER . .
