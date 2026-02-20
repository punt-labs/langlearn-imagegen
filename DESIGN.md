# Design Decision Log

## 0001 — Initial split into tri-modal packages (SETTLED)
- Imagegen is dumb: accepts prompts and returns images without evaluation.
- Prompt refinement and evaluation live in the orchestrator.
