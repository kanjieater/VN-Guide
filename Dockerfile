FROM python:3.12-slim

# System deps + Node.js 22 LTS (run as root for installs)
RUN apt-get update && apt-get install -y git curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Claude Code CLI for automated guide generation
RUN npm install -g @anthropic-ai/claude-code

ENV PYTHONUNBUFFERED=1
ENV CLAUDE_CODE_DISABLE_TELEMETRY=1

# Non-root user matching host ke (uid 1000) so Claude CLI and file writes work
RUN useradd -m -u 1000 -s /bin/bash guide && \
    mkdir -p /home/guide/.claude && \
    chown guide:guide /home/guide/.claude

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER guide
WORKDIR /home/guide
CMD ["/entrypoint.sh"]
