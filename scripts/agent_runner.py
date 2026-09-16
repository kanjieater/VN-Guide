"""Provider selection for the guide pipeline; Claude subscriptions stay on Claude CLI."""
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path


def provider() -> str:
    value = os.environ.get("GUIDE_PROVIDER", "claude").strip().lower()
    if value not in {"claude", "openrouter"}:
        raise ValueError("GUIDE_PROVIDER must be claude or openrouter")
    return value


def model_for(role: str) -> str:
    return (os.environ.get(f"GUIDE_{role}_MODEL") or os.environ.get("GUIDE_MODEL")
            or ("stealth/union-alpha" if provider() == "openrouter" else "claude-sonnet-5"))


def credentials_available() -> bool:
    if provider() == "openrouter":
        return bool(os.environ.get("OPENROUTER_API_KEY"))
    return bool(os.environ.get("ANTHROPIC_API_KEY")) or (
        Path.home() / ".claude" / ".credentials.json").exists()


def _write_openrouter_model_config(agent_dir: str, model: str) -> None:
    """Declare Union Alpha in the private config, without changing other models.

    The pinned Pi catalog predates this model. Explicit metadata and an output
    budget prevent OpenRouter from reserving almost the entire context as output.
    Other OpenRouter models retain their own catalog limits and pricing.
    """
    if model != "stealth/union-alpha":
        return
    max_tokens = int(os.environ.get("GUIDE_OPENROUTER_MAX_TOKENS", "16384"))
    if not 1 <= max_tokens <= 65536:
        raise ValueError("GUIDE_OPENROUTER_MAX_TOKENS must be between 1 and 65536")
    config = {
        "providers": {
            "openrouter": {
                "baseUrl": "https://openrouter.ai/api/v1",
                "api": "openai-completions",
                "apiKey": "$OPENROUTER_API_KEY",
                "models": [{
                    "id": model,
                    "name": model,
                    "input": ["text"],
                    "contextWindow": 262144,
                    "maxTokens": max_tokens,
                    "reasoning": False,
                    "compat": {"maxTokensField": "max_tokens"},
                    "samplingParams": {"max_tokens": max_tokens},
                }],
            },
        },
    }
    (Path(agent_dir) / "models.json").write_text(json.dumps(config), encoding="utf-8")


def run_openrouter(prompt: str, model: str, max_turns: int, cwd: Path,
                   timeout: int) -> bool:
    """Run a fresh, tool-capable Pi session with an explicit OpenRouter model.

    Do not load personal extensions/settings/credentials. OPENROUTER_API_KEY is
    required. Generation resumes from completed files, never a Claude session.
    JSON events let us enforce the turn cap and reject provider errors even if
    the CLI exits zero. Author/review calls never share model context.
    """
    import tempfile

    if not os.environ.get("OPENROUTER_API_KEY"):
        print("[agent] OPENROUTER_API_KEY is required", file=sys.stderr, flush=True)
        return False
    cmd = ["pi", "--print", "--mode", "json", "--provider", "openrouter",
           "--model", model, "--no-session", "--no-extensions", "--no-skills",
           "--no-prompt-templates", "--no-themes", "--no-approve",
           "--tools", "read,write,edit,bash,grep,find,ls"]
    prompt = ("Use the provided filesystem tools and bash (curl or Python urllib) to fetch "
              "web sources. You do not have Claude WebSearch/WebFetch tools. Read and follow "
              "the repository CLAUDE.md and the role instructions requested below. "
              "Do not commit, push, or launch other agents; the pipeline owns orchestration.\n\n"
              + prompt)
    print(f"[agent] provider=openrouter model={model} max_turns={max_turns} timeout={timeout}s",
          flush=True)
    # A private agent directory prevents host plugins, credentials and default
    # models from overriding this explicitly configured unattended run.
    with tempfile.TemporaryDirectory(prefix="vn-guide-pi-") as agent_dir:
        _write_openrouter_model_config(agent_dir, model)
        env = dict(os.environ, PI_CODING_AGENT_DIR=agent_dir, PI_SKIP_VERSION_CHECK="1",
                   PI_TELEMETRY="0")
        # Pass the prompt through a file instead of argv (large research prompts).
        prompt_file = Path(agent_dir) / "task.md"
        prompt_file.write_text(prompt, encoding="utf-8")
        cmd.append("@" + str(prompt_file))
        try:
            proc = subprocess.Popen(cmd, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, text=True, start_new_session=True)
        except FileNotFoundError:
            print("[agent] pi CLI not found; install @earendil-works/pi-coding-agent",
                  file=sys.stderr, flush=True)
            return False
        events: queue.Queue = queue.Queue()

        def read_output():
            try:
                for line in proc.stdout:
                    events.put(line)
            finally:
                events.put(None)

        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()
        deadline = time.monotonic() + timeout
        turns = 0
        completed = False
        failed = False
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("agent timeout")
                try:
                    line = events.get(timeout=remaining)
                except queue.Empty:
                    raise TimeoutError("agent timeout")
                if line is None:
                    break
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    print(line.rstrip(), flush=True)
                    continue
                kind = event.get("type")
                if kind == "turn_start":
                    turns += 1
                    if turns > max_turns:
                        raise TimeoutError(f"agent exceeded {max_turns} turns")
                elif kind == "message_update":
                    delta = event.get("assistantMessageEvent", {})
                    if delta.get("type") == "text_delta":
                        print(delta.get("delta", ""), end="", flush=True)
                elif kind == "tool_execution_start":
                    print(f"\n[agent] tool: {event.get('toolName')}", flush=True)
                elif kind == "message_end":
                    message = event.get("message", {})
                    if message.get("role") == "assistant":
                        # Pi retries transient provider errors internally. Judge the
                        # final assistant result, not an error it later recovered from.
                        failed = message.get("stopReason") in {"error", "aborted"}
                        if failed:
                            print(f"\n[agent] {message.get('errorMessage', 'Provider error')}",
                                  file=sys.stderr, flush=True)
                elif kind == "agent_end":
                    completed = True
            code = proc.wait(timeout=max(0.01, deadline - time.monotonic()))
            return code == 0 and completed and not failed
        except (TimeoutError, subprocess.TimeoutExpired) as exc:
            print(f"\n[agent] {exc}", file=sys.stderr, flush=True)
            return False
        finally:
            # Pi tracks detached bash tool groups and kills them on SIGTERM.
            # SIGKILL first would bypass that cleanup and leave tools writing.
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            reader.join(timeout=5)
            proc.stdout.close()
