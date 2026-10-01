# ---- Stage 1: build the virtual environment ----
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app
ENV UV_LINK_MODE=copy
RUN pip install --no-cache-dir uv

# Install only dependencies first, so Docker caches this layer
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Now install the project itself
COPY src/ src/
RUN uv sync --frozen --no-dev --no-editable

# ---- Stage 2: small runtime image ----
FROM python:3.12-slim-bookworm AS runtime
RUN useradd --system --no-create-home --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser alembic/ alembic/
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER appuser
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]