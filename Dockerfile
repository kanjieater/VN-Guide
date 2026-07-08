FROM python:3.12-slim

# System deps + Node.js 22 LTS
RUN apt-get update && apt-get install -y git curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Claude Code CLI for automated guide generation
RUN npm install -g @anthropic-ai/claude-code

ENV PYTHONUNBUFFERED=1
# Prevent Claude CLI from checking for updates in the container
ENV CLAUDE_CODE_DISABLE_TELEMETRY=1

WORKDIR /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
