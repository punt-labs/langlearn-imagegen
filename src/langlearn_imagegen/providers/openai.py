"""OpenAI image generation provider."""

from __future__ import annotations

import base64
from collections.abc import Sequence
from typing import Any

import httpx
from langlearn_types import ImageProviderId, ImageRequest, ImageResult
from openai import OpenAI

from langlearn_imagegen.utils import extension_from_url, resolve_output_path


class OpenAIProvider:
    """Implements ImageProvider using the OpenAI Image API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self._client: Any = OpenAI(api_key=api_key)
        self._model = model or "gpt-image-1.5"

    @property
    def model(self) -> str:
        return self._model

    def generate_image(self, request: ImageRequest) -> ImageResult:
        params: dict[str, object] = {"model": self._model, "prompt": request.prompt}
        if request.size:
            params["size"] = request.size
        if request.quality:
            params["quality"] = request.quality

        response_format = request.metadata.get("response_format", "b64_json")
        params["response_format"] = response_format

        result: Any = self._client.images.generate(**params)
        data: Any | None = result.data[0] if result.data else None
        if data is None:
            raise RuntimeError("OpenAI image generation returned no data.")

        image_bytes: bytes
        extension: str
        if response_format == "url":
            image_url = getattr(data, "url", None)
            if not image_url:
                raise RuntimeError("OpenAI image response missing image URL.")
            extension = extension_from_url(image_url, default="png")
            image_response = httpx.get(image_url, timeout=30.0)
            image_response.raise_for_status()
            image_bytes = image_response.content
        else:
            b64_payload = getattr(data, "b64_json", None)
            if not b64_payload:
                raise RuntimeError("OpenAI image response missing base64 payload.")
            image_bytes = base64.b64decode(b64_payload)
            extension = request.metadata.get("output_format", "png")

        output_path = resolve_output_path(
            request.prompt,
            ImageProviderId.openai.value,
            request.metadata,
            extension,
        )
        output_path.write_bytes(image_bytes)

        metadata = dict(request.metadata)
        metadata.setdefault("response_format", response_format)

        return ImageResult(
            path=output_path,
            prompt=request.prompt,
            provider=ImageProviderId.openai,
            revised_prompt=getattr(data, "revised_prompt", None),
            model=self._model,
            metadata=metadata,
        )

    def generate_images(self, requests: Sequence[ImageRequest]) -> list[ImageResult]:
        return [self.generate_image(request) for request in requests]
