# langlearn-imagegen

Image generation backends for language learning assets.

## Install

```bash
uv tool install punt-langlearn-imagegen
```

## CLI

```bash
langlearn-imagegen --help
langlearn-imagegen --json version
langlearn-imagegen doctor
langlearn-imagegen serve
```

## MCP

```bash
langlearn-imagegen install
langlearn-imagegen serve
```

## Development

```bash
uv sync --all-extras
uv run ruff check .
uv run ruff format --check .
uv run mypy src/ tests/
uv run pyright src/ tests/
uv run pytest
```
