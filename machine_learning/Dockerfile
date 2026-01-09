# Machine Learning Service Dockerfile
# ARICE Project - ML Models for Rice Farming

# =============================================================================
# Base Image
# =============================================================================
FROM python:3.13-slim-bookworm AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Dependencies Stage
# =============================================================================
FROM base AS dependencies

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# =============================================================================
# Development Stage
# =============================================================================
FROM dependencies AS development

# Install development dependencies
RUN pip install \
    jupyter \
    ipykernel \
    black \
    isort \
    flake8 \
    mypy \
    pytest \
    pytest-asyncio \
    pytest-cov

# Copy application code
COPY . .

# Create directories for models
RUN mkdir -p /app/trained_models/recommendation \
             /app/trained_models/weather \
             /app/trained_models/soil

# Expose ports
EXPOSE 8001
EXPOSE 8888

# Default command for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# =============================================================================
# Production Stage
# =============================================================================
FROM dependencies AS production

# Create non-root user for security
RUN groupadd -r mlservice && useradd -r -g mlservice mlservice

# Copy only necessary application code
COPY app/ /app/app/
COPY trained_models/ /app/trained_models/

# Set ownership
RUN chown -R mlservice:mlservice /app

# Switch to non-root user
USER mlservice

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Production command with optimized settings
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8001", \
     "--workers", "4", \
     "--loop", "uvloop", \
     "--http", "httptools"]

# =============================================================================
# Training Stage (for model training jobs)
# =============================================================================
FROM dependencies AS training

# Copy all code including scripts and notebooks
COPY . .

# Create directories
RUN mkdir -p /app/trained_models/recommendation \
             /app/trained_models/weather \
             /app/trained_models/soil \
             /app/data/raw \
             /app/data/processed

# Default command for training
CMD ["python", "scripts/train_all.py", "--data-source", "database"]
