# ==============================================================================
# FuXi-S2S Model Service Dockerfile
# ==============================================================================
# GPU-enabled service for running FuXi-S2S model inference
# Port: 8002
# ==============================================================================

FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu22.04 AS base

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-venv \
    python3-pip \
    python3.10-dev \
    libhdf5-dev \
    libnetcdf-dev \
    libgeos-dev \
    libproj-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.10 /usr/bin/python \
    && ln -sf /usr/bin/python3.10 /usr/bin/python3

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ------------------------------------------------------------------------------
# Builder stage
# ------------------------------------------------------------------------------
FROM base AS builder

WORKDIR /build

COPY requirements.txt ./requirements.txt

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies (includes PyTorch CUDA wheels via extra index)
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cu117 \
    -r requirements.txt

# Ensure the server runtime is always available even if it is missing from the local requirements file.
RUN pip install --no-cache-dir "uvicorn[standard]>=0.27.0"

# ------------------------------------------------------------------------------
# Runtime stage
# ------------------------------------------------------------------------------
FROM base AS runtime

WORKDIR /app/ml_weather

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Add /app to PYTHONPATH so "from ml_weather.X import Y" works
ENV PYTHONPATH="/app"

# Copy application code
COPY . /app/ml_weather/

# Create directories
RUN mkdir -p /app/data/realtime /app/data/sample /app/output /app/model

# Copy entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Environment variables
ENV PORT=8002
ENV MODEL_PATH=/app/model/fuxi_s2s.onnx
ENV DATA_DIR=/app/data
ENV OUTPUT_DIR=/app/output
ENV DEVICE=cuda

# GPU settings
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["serve"]
