from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict
from importlib import import_module
from pathlib import Path
from typing import Any, cast

import typer
from langlearn_types import (
    EvaluationResult,
    ImageEvaluator,
    ImageProviderId,
    ImageRequest,
    ImageResult,
)

from langlearn_imagegen import __version__, generate

app = typer.Typer(help="langlearn-imagegen: langlearn-imagegen CLI")

json_output_enabled = False

METADATA_OPTION = typer.Option(None, "--metadata", "-m")


def _emit(payload: Mapping[str, object], text: str) -> None:
    if json_output_enabled:
        typer.echo(json.dumps(payload))
    else:
        typer.echo(text)


def _parse_metadata(pairs: list[str] | None) -> dict[str, str]:
    metadata: dict[str, str] = {}
    if not pairs:
        return metadata
    for pair in pairs:
        if "=" not in pair:
            raise typer.BadParameter("metadata entries must be KEY=VALUE")
        key, value = pair.split("=", 1)
        metadata[key] = value
    return metadata


def _merge_metadata(
    base: dict[str, str],
    *,
    output_path: str | None = None,
    output_dir: str | None = None,
    filename: str | None = None,
    response_format: str | None = None,
    output_format: str | None = None,
    pexels_src: str | None = None,
    pexels_size: str | None = None,
    orientation: str | None = None,
    color: str | None = None,
) -> dict[str, str]:
    merged = dict(base)
    if output_path:
        merged["output_path"] = output_path
    if output_dir:
        merged["output_dir"] = output_dir
    if filename:
        merged["filename"] = filename
    if response_format:
        merged["response_format"] = response_format
    if output_format:
        merged["output_format"] = output_format
    if pexels_src:
        merged["pexels_src"] = pexels_src
    if pexels_size:
        merged["pexels_size"] = pexels_size
    if orientation:
        merged["orientation"] = orientation
    if color:
        merged["color"] = color
    return merged


def _request_payload(request: ImageRequest) -> dict[str, object]:
    payload = asdict(request)
    payload["provider"] = request.provider.value if request.provider else None
    return payload


def _result_payload(result: ImageResult) -> dict[str, object]:
    return {
        "path": str(result.path),
        "prompt": result.prompt,
        "provider": result.provider.value,
        "revised_prompt": result.revised_prompt,
        "model": result.model,
        "metadata": result.metadata,
    }


def _evaluation_payload(result: EvaluationResult) -> dict[str, object]:
    return {
        "passed": result.passed,
        "score": result.score,
        "reason": result.reason,
        "metadata": result.metadata,
    }


def _load_evaluator(path: str) -> ImageEvaluator:
    module_name, sep, attr = path.partition(":")
    if not sep:
        raise typer.BadParameter("evaluator must be in module:object format")
    module = import_module(module_name)
    target = getattr(module, attr, None)
    if target is None:
        raise typer.BadParameter(f"evaluator target not found: {path}")
    evaluator: Any = target() if isinstance(target, type) else target
    if not hasattr(evaluator, "evaluate"):
        raise typer.BadParameter("evaluator must implement evaluate(result)")
    return cast("ImageEvaluator", evaluator)


@app.callback()
def main(json_output: bool = typer.Option(False, "--json")) -> None:
    "langlearn-imagegen command group."
    global json_output_enabled
    json_output_enabled = json_output


@app.command()
def version() -> None:
    "Print version."
    _emit({"version": __version__}, __version__)


@app.command()
def doctor() -> None:
    "Check installation health."
    _emit({"status": "ok"}, "ok")


@app.command()
def install() -> None:
    "Install/configure the tool for the environment."
    payload = {"status": "pending", "message": "install not implemented"}
    _emit(payload, "install not implemented")


@app.command()
def serve() -> None:
    "Start MCP server."
    from langlearn_imagegen.server import run_server

    run_server()


@app.command()
def generate_image(
    prompt: str,
    provider: str | None = typer.Option(None, "--provider"),
    size: str | None = typer.Option(None, "--size"),
    style: str | None = typer.Option(None, "--style"),
    language: str | None = typer.Option(None, "--language"),
    cultural_context: str | None = typer.Option(None, "--cultural-context"),
    quality: str | None = typer.Option(None, "--quality"),
    seed: int | None = typer.Option(None, "--seed"),
    output_path: str | None = typer.Option(None, "--output-path"),
    output_dir: str | None = typer.Option(None, "--output-dir"),
    filename: str | None = typer.Option(None, "--filename"),
    response_format: str | None = typer.Option(None, "--response-format"),
    output_format: str | None = typer.Option(None, "--output-format"),
    pexels_src: str | None = typer.Option(None, "--pexels-src"),
    pexels_size: str | None = typer.Option(None, "--pexels-size"),
    orientation: str | None = typer.Option(None, "--orientation"),
    color: str | None = typer.Option(None, "--color"),
    metadata: list[str] | None = METADATA_OPTION,
) -> None:
    """Generate an image and write it to disk."""
    provider_id = ImageProviderId(provider) if provider else None
    metadata_map = _parse_metadata(metadata)
    metadata_map = _merge_metadata(
        metadata_map,
        output_path=output_path,
        output_dir=output_dir,
        filename=filename,
        response_format=response_format,
        output_format=output_format,
        pexels_src=pexels_src,
        pexels_size=pexels_size,
        orientation=orientation,
        color=color,
    )
    request = ImageRequest(
        prompt=prompt,
        provider=provider_id,
        size=size,
        style=style,
        language=language,
        cultural_context=cultural_context,
        quality=quality,
        seed=seed,
        metadata=metadata_map,
    )
    result = generate(request)
    payload = _result_payload(result)
    _emit(payload, str(payload))


@app.command()
def dry_run(
    prompt: str,
    provider: str | None = typer.Option(None, "--provider"),
    size: str | None = typer.Option(None, "--size"),
    style: str | None = typer.Option(None, "--style"),
    language: str | None = typer.Option(None, "--language"),
    cultural_context: str | None = typer.Option(None, "--cultural-context"),
    quality: str | None = typer.Option(None, "--quality"),
    seed: int | None = typer.Option(None, "--seed"),
    output_path: str | None = typer.Option(None, "--output-path"),
    output_dir: str | None = typer.Option(None, "--output-dir"),
    filename: str | None = typer.Option(None, "--filename"),
    response_format: str | None = typer.Option(None, "--response-format"),
    output_format: str | None = typer.Option(None, "--output-format"),
    pexels_src: str | None = typer.Option(None, "--pexels-src"),
    pexels_size: str | None = typer.Option(None, "--pexels-size"),
    orientation: str | None = typer.Option(None, "--orientation"),
    color: str | None = typer.Option(None, "--color"),
    metadata: list[str] | None = METADATA_OPTION,
) -> None:
    """Print the ImageRequest payload without generating."""
    provider_id = ImageProviderId(provider) if provider else None
    metadata_map = _parse_metadata(metadata)
    metadata_map = _merge_metadata(
        metadata_map,
        output_path=output_path,
        output_dir=output_dir,
        filename=filename,
        response_format=response_format,
        output_format=output_format,
        pexels_src=pexels_src,
        pexels_size=pexels_size,
        orientation=orientation,
        color=color,
    )
    request = ImageRequest(
        prompt=prompt,
        provider=provider_id,
        size=size,
        style=style,
        language=language,
        cultural_context=cultural_context,
        quality=quality,
        seed=seed,
        metadata=metadata_map,
    )
    payload = _request_payload(request)
    _emit(payload, str(payload))


@app.command()
def evaluate_only(
    image_path: Path,
    prompt: str = typer.Option(..., "--prompt"),
    provider: str | None = typer.Option(None, "--provider"),
    evaluator: str = typer.Option(..., "--evaluator"),
    revised_prompt: str | None = typer.Option(None, "--revised-prompt"),
    model: str | None = typer.Option(None, "--model"),
    metadata: list[str] | None = METADATA_OPTION,
) -> None:
    """Evaluate an existing image using a custom evaluator."""
    provider_id = ImageProviderId(provider) if provider else ImageProviderId.openai
    metadata_map = _parse_metadata(metadata)
    result = ImageResult(
        path=image_path,
        prompt=prompt,
        provider=provider_id,
        revised_prompt=revised_prompt,
        model=model,
        metadata=metadata_map,
    )
    evaluator_impl = _load_evaluator(evaluator)
    evaluation = evaluator_impl.evaluate(result)
    payload = _evaluation_payload(evaluation)
    _emit(payload, str(payload))
