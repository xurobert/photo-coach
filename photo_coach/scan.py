from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ExifTags
import imagehash
import numpy as np

from .models import PhotoRecord

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff"}


def iter_images(root: Path) -> Iterable[Path]:
    root = root.resolve()
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            yield p


def _exif_dict(im: Image.Image) -> dict:
    out: dict = {}
    raw = im.getexif()
    if not raw:
        return out
    for k, v in raw.items():
        name = ExifTags.TAGS.get(k, str(k))
        try:
            out[name] = v if isinstance(v, (int, float, str)) else str(v)
        except Exception:
            continue
    return out


def _sharpness(gray: np.ndarray) -> float:
    # Laplacian variance proxy
    g = gray.astype(np.float64)
    lap = (
        -4 * g[1:-1, 1:-1]
        + g[:-2, 1:-1]
        + g[2:, 1:-1]
        + g[1:-1, :-2]
        + g[1:-1, 2:]
    )
    return float(lap.var())


def _exposure(gray: np.ndarray) -> float:
    mean = float(gray.mean()) / 255.0
    # 0.5 ideal; score peaks near mid
    return 1.0 - abs(mean - 0.5) * 2.0


def analyze_image(path: Path) -> PhotoRecord:
    with Image.open(path) as im:
        im = im.convert("RGB")
        exif = _exif_dict(im)
        ph = str(imagehash.phash(im))
        arr = np.asarray(im.convert("L"))
        sharp = _sharpness(arr)
        expo = _exposure(arr)
        # Normalize sharpness roughly into 0..1 using log scale
        sharp_n = float(np.tanh(sharp / 500.0))
        score = round(0.65 * sharp_n + 0.35 * max(0.0, expo), 4)
        flags: list[str] = []
        if sharp_n < 0.15:
            flags.append("blurry")
        if expo < 0.25:
            mean = float(arr.mean()) / 255.0
            flags.append("underexposed" if mean < 0.5 else "overexposed")
        stem = path.stem
        keywords = [stem, stem.replace("_", " "), path.parent.name]
        for ch in stem:
            if "一" <= ch <= "鿿":
                keywords.append(ch)
        for i in range(len(stem) - 1):
            a, b = stem[i], stem[i + 1]
            if "一" <= a <= "鿿" and "一" <= b <= "鿿":
                keywords.append(a + b)
        for key in ("Make", "Model", "DateTime", "DateTimeOriginal"):
            if key in exif:
                keywords.append(str(exif[key]))
        return PhotoRecord(
            path=str(path.resolve()),
            filename=path.name,
            exif=exif,
            sharpness=round(sharp_n, 4),
            exposure=round(float(expo), 4),
            score=score,
            flags=flags,
            phash=ph,
            keywords=keywords,
        )


def scan_folder(root: Path) -> list[PhotoRecord]:
    return [analyze_image(p) for p in iter_images(root)]
