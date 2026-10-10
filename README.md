# Photo Coach

Local-first photo assistant for photographers: **cull near-duplicates, score keepers, trend tips, and fuzzy search** over your library. No Lightroom subscription required.

本地优先的摄影师助手：**去重选片、质量打分、趋势建议、模糊语义检索**。第一版不做完整修图引擎。

## Why not just Lightroom / Capture One?
Those are paid workflows focused on develop/edit. Photo Coach focuses on the free, local loop many open-source tools still underserve: *keep or drop*, *why your keep rate moved*, and *find that shoot by a vague memory*.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
photo-coach demo
photo-coach scan ./fixtures --out .photo-coach/index.json
photo-coach search "红色 雨伞" --index .photo-coach/index.json
photo-coach tips --index .photo-coach/index.json
photo-coach serve --index .photo-coach/index.json
# open http://127.0.0.1:8765
```

## Features (v0.1)
- Near-duplicate grouping via perceptual hash
- Heuristic sharpness / exposure scoring (no cloud model required)
- Blur / exposure flags
- EXIF-based trend tips (focal length, aperture, time-of-day habits)
- Knowledge-base style search: keyword/CJK fallback by default; optional local embeddings via `PHOTO_COACH_EMBED=1` (+ `pip install -e '.[embed]'`)

## Optional embedding search
```bash
pip install -e '.[embed]'
export PHOTO_COACH_EMBED=1
# optional model override:
# export PHOTO_COACH_EMBED_MODEL=sentence-transformers/clip-ViT-B-32
photo-coach search "棚拍侧光人像"
```

## Not in v1
- Full RAW develop / curves / masks
- Auto delete originals (we only mark suggestions)
- Auto-posting to social networks

## Docs
See [docs/MVP.md](docs/MVP.md).

## License
MIT
