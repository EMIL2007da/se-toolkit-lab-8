# Multi-stage build for nanobot gateway service
# Build context is the repository root (.)

# Stage 1: Build stage with uv
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

# Copy nanobot project files (paths relative to build context .)
COPY nanobot/pyproject.toml ./nanobot/
COPY nanobot/entrypoint.py ./nanobot/
COPY nanobot/config.json ./nanobot/
COPY nanobot/workspace ./nanobot/workspace/

# Copy mcp directory
COPY mcp ./mcp/

# Copy nanobot-websocket-channel for editable installs
COPY nanobot-websocket-channel/nanobot-channel-protocol ./nanobot-websocket-channel/nanobot-channel-protocol/
COPY nanobot-websocket-channel/nanobot-webchat ./nanobot-websocket-channel/nanobot-webchat/
COPY nanobot-websocket-channel/mcp-webchat ./nanobot-websocket-channel/mcp-webchat/
COPY nanobot-websocket-channel/mcp-cron ./nanobot-websocket-channel/mcp-cron/
COPY nanobot-websocket-channel/pyproject.toml ./nanobot-websocket-channel/

WORKDIR /app/nanobot

# Create virtual environment and install dependencies
# Install in order: protocol first, then webchat, then mcp-webchat, then mcp-cron, then mcp-obs, then nanobot
# Note: We need to remove workspace source references before installing nanobot
RUN uv venv /app/.venv && \
    cd /app/nanobot-websocket-channel/nanobot-channel-protocol && \
    uv pip install --no-deps -e . && \
    cd /app/nanobot-websocket-channel/nanobot-webchat && \
    uv pip install --no-deps -e . && \
    cd /app/nanobot-websocket-channel/mcp-webchat && \
    uv pip install --no-deps -e . && \
    cd /app/nanobot-websocket-channel/mcp-cron && \
    uv pip install --no-deps -e . && \
    cd /app/mcp/mcp-lms && \
    uv pip install --no-deps -e . && \
    cd /app/mcp/mcp-obs && \
    uv pip install --no-deps -e . && \
    cd /app/nanobot && \
    # Remove workspace source reference from pyproject.toml
    sed -i '/mcp-obs.*workspace/d' pyproject.toml && \
    uv pip install --no-cache-dir .

# Stage 2: Runtime stage
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS runtime

# Accept build args for user IDs
ARG APP_UID=1000
ARG APP_GID=1000

# Create non-root user with specified UID/GID
RUN groupadd --gid "${APP_GID}" appgroup && \
    useradd --uid "${APP_UID}" --gid "${APP_GID}" --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/nanobot /app/nanobot
COPY --from=builder --chown=appuser:appgroup /app/mcp /app/mcp
COPY --from=builder --chown=appuser:appgroup /app/nanobot-websocket-channel /app/nanobot-websocket-channel

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Default command runs the entrypoint which resolves env vars and launches nanobot gateway
CMD ["python", "/app/nanobot/entrypoint.py"]
