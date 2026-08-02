FROM python:3.12-slim

# System deps + Node.js 22 LTS + GitHub CLI (run as root for installs)
RUN apt-get update && apt-get install -y git curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
        tee /usr/share/keyrings/githubcli-archive-keyring.gpg > /dev/null && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
        tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
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
