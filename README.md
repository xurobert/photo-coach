# Photo Coach

**免费本地挑图：去重选片 · 质量打分 · 趋势建议 · 模糊搜旧片**  
不用 Lightroom 订阅，也能把「拍了一堆 → 不知道留哪张 / 找不到那张」解决掉。

> 目标很朴素：先让摄影师愿意 star 并真用起来。

## 30 秒上手

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
photo-coach demo
photo-coach scan ./你的照片文件夹
photo-coach search "雨天 红伞"
photo-coach tips
photo-coach serve   # http://127.0.0.1:8765
```

仓库：https://github.com/xurobert/photo-coach

## 它解决什么
| 痛点 | Photo Coach |
|------|-------------|
| 连拍太多，不知道留哪张 | 感知哈希去重，按清晰度/曝光建议保留 |
| 记得「好像有张红伞」找不到 | 中文模糊检索（默认可不接大模型） |
| 拍了很多但没进步感 | 基于 EXIF 给可执行趋势建议 |

## 和 Lightroom / Capture One 的边界
那些是**付费修图工作流**。本项目第一版**不做**完整 RAW 显影/曲线/蒙版，专注选片、打分、建议、检索。

## Features (v0.1)
- Near-duplicate cull (pHash)
- Heuristic sharpness / exposure score（无需云端模型）
- Blur / exposure flags
- EXIF trend tips（焦段、光圈、时段习惯）
- Knowledge-base style search：默认关键词/CJK；可选 `PHOTO_COACH_EMBED=1` 本地向量

## Optional embedding search
```bash
pip install -e '.[embed]'
export PHOTO_COACH_EMBED=1
photo-coach search "棚拍侧光人像"
```

## Not in v1
- Full RAW develop / curves / masks
- Auto-delete originals（只标记建议）
- Auto-post to social networks

## Docs
See [docs/MVP.md](docs/MVP.md).

## License
MIT
