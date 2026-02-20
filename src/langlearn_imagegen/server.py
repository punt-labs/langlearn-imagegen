from __future__ import annotations

from langlearn_types import ImageProviderId, ImageRequest
from mcp.server.fastmcp import FastMCP

from langlearn_imagegen import __version__, generate
from langlearn_imagegen.providers import PROVIDER_REGISTRY

mcp = FastMCP("langlearn-imagegen")
mcp._mcp_server.version = __version__  # pyright: ignore[reportPrivateUsage]


@mcp.tool()
def ping() -> str:
    "Health check tool."
    return "ok"


@mcp.tool()
def health() -> dict[str, str]:
    """Report basic service health."""
    return {"status": "ok", "version": __version__}


@mcp.tool()
def list_providers() -> list[str]:
    """List available image providers."""
    return sorted(PROVIDER_REGISTRY)


@mcp.tool()
def generate_image(
    prompt: str,
    provider: str | None = None,
    size: str | None = None,
    style: str | None = None,
    language: str | None = None,
    cultural_context: str | None = None,
    quality: str | None = None,
    seed: int | None = None,
    output_path: str | None = None,
    output_dir: str | None = None,
    filename: str | None = None,
    response_format: str | None = None,
    output_format: str | None = None,
    pexels_src: str | None = None,
    pexels_size: str | None = None,
    orientation: str | None = None,
    color: str | None = None,
    metadata: dict[str, str] | None = None,
) -> dict[str, object]:
    """Generate an image via the configured provider."""
    resolved_provider = ImageProviderId(provider) if provider else None

    merged_metadata = dict(metadata or {})
    if output_path:
        merged_metadata["output_path"] = output_path
    if output_dir:
        merged_metadata["output_dir"] = output_dir
    if filename:
        merged_metadata["filename"] = filename
    if response_format:
        merged_metadata["response_format"] = response_format
    if output_format:
        merged_metadata["output_format"] = output_format
    if pexels_src:
        merged_metadata["pexels_src"] = pexels_src
    if pexels_size:
        merged_metadata["pexels_size"] = pexels_size
    if orientation:
        merged_metadata["orientation"] = orientation
    if color:
        merged_metadata["color"] = color

    request = ImageRequest(
        prompt=prompt,
        provider=resolved_provider,
        size=size,
        style=style,
        language=language,
        cultural_context=cultural_context,
        quality=quality,
        seed=seed,
        metadata=merged_metadata,
    )
    result = generate(request)
    return {
        "path": str(result.path),
        "prompt": result.prompt,
        "provider": result.provider.value,
        "revised_prompt": result.revised_prompt,
        "model": result.model,
        "metadata": result.metadata,
    }


def run_server() -> None:
    "Run the MCP server."
    mcp.run()
