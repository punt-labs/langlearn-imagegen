"""Pexels image search provider."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

import httpx
from langlearn_types import ImageProviderId, ImageRequest, ImageResult

from langlearn_imagegen.utils import extension_from_url, resolve_output_path

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"


def _orientation_from_size(size: str | None) -> str | None:
    if not size or "x" not in size:
        return None
    width_str, height_str = size.lower().split("x", 1)
    if not width_str.isdigit() or not height_str.isdigit():
        return None
    width = int(width_str)
    height = int(height_str)
    if width > height:
        return "landscape"
    if height > width:
        return "portrait"
    return "square"


class PexelsProvider:
    """Implements ImageProvider using the Pexels search API."""

    def __init__(self, api_key: str | None = None) -> None:
        resolved_key = api_key or os.environ.get("PEXELS_API_KEY")
        if not resolved_key:
            raise ValueError("PEXELS_API_KEY is required for PexelsProvider.")
        self._api_key: str = resolved_key

    def generate_image(self, request: ImageRequest) -> ImageResult:
        headers = {"Authorization": self._api_key}
        params: dict[str, str | int] = {"query": request.prompt, "per_page": 1}

        if request.language:
            params["locale"] = request.language

        orientation = request.metadata.get("orientation") or _orientation_from_size(
            request.size
        )
        if orientation:
            params["orientation"] = orientation

        size = request.metadata.get("pexels_size")
        if size:
            params["size"] = size

        color = request.metadata.get("color")
        if color:
            params["color"] = color

        response = httpx.get(
            PEXELS_SEARCH_URL, headers=headers, params=params, timeout=30.0
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        photos: list[dict[str, Any]] = payload.get("photos", [])
        if not photos:
            raise RuntimeError("Pexels search returned no photos.")

        photo = photos[0]
        sources: dict[str, str] = photo.get("src", {})
        source_key = request.metadata.get("pexels_src", "original")
        image_url = sources.get(source_key) or sources.get("original")
        if not image_url:
            raise RuntimeError("Pexels photo response missing image URL.")

        image_response = httpx.get(image_url, timeout=30.0)
        image_response.raise_for_status()
        image_bytes = image_response.content

        extension = extension_from_url(image_url, default="jpg")
        output_path = resolve_output_path(
            request.prompt,
            ImageProviderId.pexels.value,
            request.metadata,
            extension,
        )
        output_path.write_bytes(image_bytes)

        metadata = dict(request.metadata)
        metadata.setdefault("pexels_id", str(photo.get("id", "")))
        metadata.setdefault("pexels_url", str(photo.get("url", "")))
        metadata.setdefault("pexels_photographer", str(photo.get("photographer", "")))
        metadata.setdefault(
            "pexels_photographer_url", str(photo.get("photographer_url", ""))
        )
        metadata.setdefault("pexels_source", source_key)

        return ImageResult(
            path=output_path,
            prompt=request.prompt,
            provider=ImageProviderId.pexels,
            revised_prompt=None,
            model=None,
            metadata=metadata,
        )

    def generate_images(self, requests: Sequence[ImageRequest]) -> list[ImageResult]:
        return [self.generate_image(request) for request in requests]
