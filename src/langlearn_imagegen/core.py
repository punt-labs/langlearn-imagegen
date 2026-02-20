"""Provider-agnostic image generation orchestration."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from langlearn_imagegen.providers import get_provider

if TYPE_CHECKING:
    from langlearn_types import ImageEvaluator, ImageRequest, ImageResult

__all__ = ["ImageClient", "generate"]


class ImageClient:
    """Thin wrapper around ImageProvider with optional evaluation."""

    def __init__(
        self,
        provider_name: str | None = None,
        evaluator: ImageEvaluator | None = None,
    ) -> None:
        self._provider = get_provider(provider_name)
        self._evaluator = evaluator

    def generate(self, request: ImageRequest) -> ImageResult:
        result = self._provider.generate_image(request)
        self._maybe_evaluate(result)
        return result

    def generate_batch(self, requests: Sequence[ImageRequest]) -> list[ImageResult]:
        results = self._provider.generate_images(requests)
        if self._evaluator is not None:
            for result in results:
                self._maybe_evaluate(result)
        return results

    def _maybe_evaluate(self, result: ImageResult) -> None:
        if self._evaluator is None:
            return
        evaluation = self._evaluator.evaluate(result)
        if not evaluation.passed:
            reason = evaluation.reason or "evaluation failed"
            raise ValueError(reason)


def generate(
    request: ImageRequest, evaluator: ImageEvaluator | None = None
) -> ImageResult:
    """Generate a single image with optional evaluation."""
    provider_name = request.provider.value if request.provider else None
    client = ImageClient(provider_name=provider_name, evaluator=evaluator)
    return client.generate(request)
