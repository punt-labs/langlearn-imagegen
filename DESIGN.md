# Design Decision Log

## 0001 — Initial split into tri-modal packages (SETTLED)

- Imagegen is dumb: accepts prompts and returns images without evaluation.
- Prompt refinement and evaluation live in the orchestrator.

## 0002 — Provider-first execution model (SETTLED)

- Providers implement ImageProvider and are selected by request.provider or CLI flags.
- The core ImageClient optionally accepts an ImageEvaluator but ships no built-in evaluators.
- Pexels and OpenAI are first-class providers; additional providers are additive.
