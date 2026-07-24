# syntax=docker/dockerfile:1

# --- Builder: resolve and install runtime dependencies into a local venv ---
FROM python:3.13-slim AS builder

ENV POETRY_VERSION=2.4.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

# Only the dependency manifests first, so the install layer is cached as long
# as dependencies don't change (source edits won't bust it).
COPY pyproject.toml poetry.lock README.md ./

# Install runtime deps only (no dev group) and skip the root package: the
# application source is copied straight onto PYTHONPATH in the final stage.
RUN poetry install --only main --no-root

# --- Runtime: slim image carrying just the venv and the application source ---
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"

WORKDIR /app

# Run as an unprivileged user.
RUN groupadd --system app && useradd --system --gid app --home-dir /app app

COPY --from=builder /app/.venv /app/.venv
COPY app/src /app/src

USER app

EXPOSE 8000

CMD ["uvicorn", "url_shortener.main:app", "--host", "0.0.0.0", "--port", "8000"]
