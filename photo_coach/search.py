from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from .models import PhotoRecord

# Lightweight bag-of-tokens fallback (no model required).
# Optional: sentence-transformers if installed and PHOTO_COACH_EMBED=1.


def _tokenize(text: str) -> set[str]:
    text = text.lower()
    parts = re.split(r"[\s_\-./\\]+", text)
    toks = {p for p in parts if len(p) >= 2}
    # also keep CJK bigrams
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            toks.add(ch)
    for i in range(len(text) - 1):
        a, b = text[i], text[i + 1]
        if "\u4e00" <= a <= "\u9fff" and "\u4e00" <= b <= "\u9fff":
            toks.add(a + b)
    return toks


def index_text(photo: PhotoRecord) -> str:
    bits = [photo.filename, photo.path, *photo.keywords, *photo.flags]
    bits.extend(f"{k}:{v}" for k, v in photo.exif.items())
    return " ".join(str(b) for b in bits)


def keyword_search(photos: list[PhotoRecord], query: str, top_k: int = 10) -> list[tuple[PhotoRecord, float]]:
    q = _tokenize(query)
    if not q:
        return []
    scored: list[tuple[PhotoRecord, float]] = []
    for p in photos:
        doc = _tokenize(index_text(p))
        if not doc:
            continue
        inter = len(q & doc)
        if inter == 0:
            continue
        score = inter / math.sqrt(len(q) * len(doc))
        scored.append((p, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def try_embed_search(photos: list[PhotoRecord], query: str, top_k: int = 10) -> list[tuple[PhotoRecord, float]] | None:
    """Optional local embedding search. Returns None if unavailable."""
    import os

    if os.environ.get("PHOTO_COACH_EMBED", "").strip() not in {"1", "true", "yes"}:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except Exception:
        return None

    model_name = os.environ.get("PHOTO_COACH_EMBED_MODEL", "sentence-transformers/clip-ViT-B-32")
    model = SentenceTransformer(model_name)
    texts = [index_text(p) for p in photos]
    # Text-only fallback embeddings for MVP; image+CLIP can replace later
    doc_emb = model.encode(texts, normalize_embeddings=True)
    q_emb = model.encode([query], normalize_embeddings=True)[0]
    sims = doc_emb @ q_emb
    order = np.argsort(-sims)[:top_k]
    return [(photos[int(i)], float(sims[int(i)])) for i in order]


def search_photos(photos: list[PhotoRecord], query: str, top_k: int = 10) -> tuple[str, list[tuple[PhotoRecord, float]]]:
    embedded = try_embed_search(photos, query, top_k=top_k)
    if embedded is not None:
        return "embedding", embedded
    return "keyword", keyword_search(photos, query, top_k=top_k)


def save_index(path: Path, photos: list[PhotoRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [p.to_dict() for p in photos]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_index(path: Path) -> list[PhotoRecord]:
    data: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    out: list[PhotoRecord] = []
    for d in data:
        out.append(
            PhotoRecord(
                path=d["path"],
                filename=d["filename"],
                exif=d.get("exif", {}),
                sharpness=d.get("sharpness", 0.0),
                exposure=d.get("exposure", 0.0),
                score=d.get("score", 0.0),
                flags=d.get("flags", []),
                phash=d.get("phash", ""),
                group_id=d.get("group_id"),
                keep=d.get("keep", True),
                keywords=d.get("keywords", []),
            )
        )
    return out
