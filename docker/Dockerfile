# ============================================================
# RKGB — Development Dockerfile
# ============================================================
FROM python:3.11-slim AS base

LABEL maintainer="RKGB Team"
LABEL description="Research Knowledge Graph Builder"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy dependency manifest first for layer caching
COPY pyproject.toml ./

# Install project in editable mode with all extras
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[all]"

# Copy application source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
