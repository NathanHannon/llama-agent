# Llama-Agent — Copilot Instructions

## Project Overview

Llama-Agent is a CLI coding assistant (like Codex CLI / Claude Code) powered by Meta's Llama models. It uses the **OpenAI Python SDK** against multiple OpenAI-compatible backends (Groq, OpenRouter, Ollama, LM Studio). The core loop: user chats → model optionally calls tools → tools execute → model summarizes.

## Architecture (4 files)

- **`main.py`** — Typer CLI entry point + Rich REPL loop. Single `start` command.
- **`agent.py`** — `LlamaAgent` class. Manages provider selection, conversation history (`self.messages`), and the tool-call → response cycle.
- **`tools.py`** — Tool implementations (`list_files`, `read_file`, `run_shell`) + `AVAILABLE_TOOLS` dict and `TOOL_DEFINITIONS` list (OpenAI function-calling JSON schema).
- **`.env`** — Runtime config: `AI_PROVIDER`, `AI_MODEL`, API keys, optional base URL overrides.

## Key Patterns

### Adding a new tool

1. Write the function in `tools.py` — must return a `str`.
2. Add it to the `AVAILABLE_TOOLS` dict (key = function name as string).
3. Add its OpenAI function-calling JSON schema to the `TOOL_DEFINITIONS` list.
4. No changes needed in `agent.py` — it discovers tools dynamically from those two exports.

### Adding a new provider

Add an `elif` branch in `LlamaAgent.__init__` (in `agent.py`). All providers use the `OpenAI` client with a custom `base_url`. Local providers (Ollama, LM Studio) use a dummy API key string. Update `.env` comments to document the new option.

### Tool-call flow (current limitation)

`LlamaAgent.chat()` handles **one round** of tool calls then makes a final completion. It does NOT loop, so multi-step tool chains (read → edit → verify) require multiple user turns today. This is a known area for improvement.

## Conventions

- **All LLM communication** goes through the `openai` Python package — never call provider-specific SDKs.
- **Tool functions** return plain strings (including errors as `"Error: ..."`); the model interprets the output.
- **CLI output** uses Rich markdown rendering (`console.print(Markdown(response))`).
- **No async** — everything is synchronous. The OpenAI client is sync.
- **Config via `.env`** loaded by `python-dotenv` at import time in `agent.py`.

## Running

```bash
python -m venv venv && venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py start
```

## Planned Improvements

- Multi-step tool loop (agent keeps calling tools until done)
- Write/edit file tools
- Shell command safety confirmations
- Streaming responses
- `prompt_toolkit` integration for input history and multiline editing
- Grep/search tool for codebase exploration
