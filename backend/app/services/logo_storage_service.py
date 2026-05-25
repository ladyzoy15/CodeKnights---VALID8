from __future__ import annotations

import io
import re
import uuid
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings

_NEUTRAL_THRESHOLD = 30
_EXTREME_LUM_MIN = 60
_EXTREME_LUM_MAX = 720


def extract_dominant_colors_from_bytes(image_bytes: bytes, is_svg: bool = False) -> Tuple[str | None, str | None]:
    if is_svg:
        return None, None

    try:
        with Image.open(io.BytesIO(image_bytes)).convert("RGB") as img:
            img = img.resize((100, 100))
            pal = img.quantize(colors=6).convert("RGB")
    except Exception:
        return None, None

    colors = pal.getcolors(maxcolors=1000)
    if not colors:
        return None, None

    colors.sort(key=lambda x: x[0], reverse=True)

    def _is_neutral(r: int, g: int, b: int) -> bool:
        return max(abs(r - g), abs(g - b), abs(b - r)) < _NEUTRAL_THRESHOLD

    def _is_extreme(r: int, g: int, b: int) -> bool:
        return (r + g + b) < _EXTREME_LUM_MIN or (r + g + b) > _EXTREME_LUM_MAX

    dominant: list[str] = []
    for _count, pixel in colors:
        r, g, b = pixel
        if _is_neutral(r, g, b) or _is_extreme(r, g, b):
            continue
        hex_colour = f"#{r:02x}{g:02x}{b:02x}"
        if hex_colour not in dominant:
            dominant.append(hex_colour)
        if len(dominant) >= 2:
            break

    if not dominant:
        for _count, pixel in colors[:3]:
            r, g, b = pixel
            hex_colour = f"#{r:02x}{g:02x}{b:02x}"
            if hex_colour not in dominant:
                dominant.append(hex_colour)
            if len(dominant) >= 2:
                break

    primary = dominant[0] if len(dominant) > 0 else None
    secondary = dominant[1] if len(dominant) > 1 else None
    return primary, secondary


ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


def _validate_svg_content(content: bytes) -> None:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SVG encoding.",
        ) from exc

    lowered = text.lower()
    if "<svg" not in lowered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SVG content.",
        )

    if "<script" in lowered or "javascript:" in lowered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SVG scripts are not allowed.",
        )


def _validate_raster_content(content: bytes) -> None:
    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file.",
        ) from exc


def _safe_extension(filename: str) -> str:
    cleaned_name = filename.strip()
    extension = Path(cleaned_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported logo file type. Allowed: PNG, JPG, JPEG, WebP, SVG.",
        )
    return extension


async def store_school_logo(upload: UploadFile) -> str:
    content = await upload.read()
    filename = (upload.filename or "").strip()
    return store_school_logo_bytes(content, filename)


def store_school_logo_bytes(
    content: bytes,
    filename: str,
    content_type: str | None = None,
) -> str:
    settings = get_settings()

    if not filename:
        raise HTTPException(status_code=400, detail="Logo file name is required.")

    extension = _safe_extension(filename)

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded logo file is empty.")

    max_size_bytes = settings.school_logo_max_file_size_mb * 1024 * 1024
    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Logo file exceeds {settings.school_logo_max_file_size_mb} MB limit.",
        )

    if extension == ".svg":
        _validate_svg_content(content)
    else:
        _validate_raster_content(content)

    storage_dir = Path(settings.school_logo_storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)

    generated_name = f"{uuid.uuid4().hex}{extension}"
    target_path = storage_dir / generated_name
    target_path.write_bytes(content)

    public_prefix = settings.school_logo_public_prefix.rstrip("/")
    return f"{public_prefix}/{generated_name}"


def delete_managed_school_logo(logo_url: str | None) -> None:
    if not logo_url:
        return

    settings = get_settings()
    prefix = settings.school_logo_public_prefix.rstrip("/")
    if not logo_url.startswith(prefix):
        return

    parsed = urlparse(logo_url)
    candidate = Path(parsed.path).name
    if not re.fullmatch(r"[a-f0-9]{32}\.(png|jpg|jpeg|webp|svg)", candidate):
        return

    storage_dir = Path(settings.school_logo_storage_dir).resolve()
    target_path = (storage_dir / candidate).resolve()
    if storage_dir not in target_path.parents:
        return

    if target_path.exists():
        target_path.unlink()
