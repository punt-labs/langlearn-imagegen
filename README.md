# langlearn-imagegen

Image generation backends for language learning assets.

## Status (2026-02-21)

- Providers implemented: OpenAI image API and Pexels search.
- Optional evaluator can reject results, but no built-in evaluators ship yet.
- Two-stage generation and cultural-context query rewriting are not implemented yet.

## Roadmap

See ROADMAP.md.

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

Example:

```bash
langlearn-imagegen generate --prompt "a small bakery" --provider openai
langlearn-imagegen generate --prompt "Paris cafe" --provider pexels --pexels-size medium
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
