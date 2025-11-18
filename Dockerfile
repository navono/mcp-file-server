FROM python:3.13-slim

# Set proxy arguments
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ENV HTTP_PROXY=$HTTP_PROXY \
    HTTPS_PROXY=$HTTPS_PROXY \
    http_proxy=$HTTP_PROXY \
    https_proxy=$HTTPS_PROXY \
    NO_PROXY=$NO_PROXY \
    no_proxy=$NO_PROXY

WORKDIR /app

# Install system dependencies required by uv
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv (Rust-based Python package/dependency manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure uv-installed binaries are on PATH (default install location)
ENV PATH="/root/.local/bin:${PATH}"

# Copy project metadata and lock file for dependency resolution
COPY pyproject.toml uv.lock /app/

# Install Python dependencies into the system environment using uv
RUN uv sync

# Copy application code
COPY server.py /app/
COPY streaming_server.py /app/

# Create a directory to mount the local files
RUN mkdir /data

# Command to run the stdio-based MCP server by default
CMD ["uv", "run", "python", "server.py"]