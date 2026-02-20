"""Image provider registry and auto-detection."""

from __future__ import annotations

import os
from collections.abc import Callable

from langlearn_types import ImageProvider, ImageProviderId

__all__ = ["PROVIDER_REGISTRY", "auto_detect_provider", "get_provider"]

ProviderFactory = Callable[..., ImageProvider]

# Factories are lazy to avoid importing SDKs unless needed.
PROVIDER_REGISTRY: dict[str, ProviderFactory] = {}


def _register_openai(**kwargs: str | None) -> ImageProvider:
    from langlearn_imagegen.providers.openai import OpenAIProvider

    model = kwargs.get("model")
    return OpenAIProvider(model=model)


def _register_pexels(**kwargs: str | None) -> ImageProvider:
    from langlearn_imagegen.providers.pexels import PexelsProvider

    return PexelsProvider()


PROVIDER_REGISTRY[ImageProviderId.openai.value] = _register_openai
PROVIDER_REGISTRY[ImageProviderId.pexels.value] = _register_pexels


def auto_detect_provider() -> str:
    """Detect provider from environment or available API keys."""
    env = os.environ.get("LANGLEARN_IMAGEGEN_PROVIDER")
    if env:
        return env.lower()
    if os.environ.get("OPENAI_API_KEY"):
        return ImageProviderId.openai.value
    if os.environ.get("PEXELS_API_KEY"):
        return ImageProviderId.pexels.value
    return ImageProviderId.openai.value


def get_provider(name: str | None = None, **kwargs: str | None) -> ImageProvider:
    """Look up a provider by name, or auto-detect."""
    resolved = name.lower() if name is not None else auto_detect_provider()
    factory = PROVIDER_REGISTRY.get(resolved)
    if factory is None:
        available = ", ".join(sorted(PROVIDER_REGISTRY))
        msg = f"Unknown provider '{resolved}'. Available: {available}"
        raise ValueError(msg)
    return factory(**kwargs)
