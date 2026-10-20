# Baymax

A local-first personal assistant under development, supporting
Bahasa Indonesia and English.

## Development status

Verified:
- Python environment managed with uv.
- Local Ollama connection.
- Qwen3.5 4B running on GPU.
- Basic bilingual note and timer planning.

Not integrated yet:
- Action execution through the new planner.
- Bilingual speech input and output.

The planner currently runs in dry-run mode:
it displays action plans without executing them.

## Development environment

- Ubuntu on WSL 2
- Python managed with uv
- Ollama
- Model: qwen3.5:4b

## Setup

Install uv and Ollama first, then run from the repository root:

```bash
uv sync --locked
ollama pull qwen3.5:4b
```

Ensure the Ollama server is running.

## Manual checks

Check the local model connection:

```bash
uv run python -m scripts.check_ollama
```

Run the bilingual planner:

```bash
uv run python -m scripts.check_planner
```

## Project structure

- scripts/: manual development checks.
- baymax_1.2/: original prototype, retained during migration.
- pyproject.toml: project metadata and dependencies.
- uv.lock: locked dependency resolution.

## Safety

Model-generated plans must be validated before execution.
Do not commit API keys, personal recordings, or private notes.