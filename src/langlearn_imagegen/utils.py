from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path


def resolve_output_path(
    prompt: str,
    provider: str,
    metadata: Mapping[str, str],
    extension: str,
) -> Path:
    """Resolve an output path for a generated image."""
    output_path = metadata.get("output_path")
    if output_path:
        path = Path(output_path)
    else:
        output_dir = Path(metadata.get("output_dir", "."))
        filename = metadata.get("filename")
        if filename is None:
            digest = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:12]
            filename = f"{provider}_{digest}.{extension}"
        path = output_dir / filename

    if not path.suffix:
        path = path.with_suffix(f".{extension}")

    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def extension_from_url(url: str, default: str = "jpg") -> str:
    """Infer a filename extension from a URL."""
    suffix = Path(url.split("?", 1)[0]).suffix
    if suffix.startswith("."):
        return suffix[1:]
    return default
