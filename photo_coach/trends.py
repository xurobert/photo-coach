from __future__ import annotations

from collections import Counter
from typing import Any

from .models import PhotoRecord


def _focal(exif: dict[str, Any]) -> str | None:
    for key in ("FocalLength", "FocalLengthIn35mmFilm"):
        if key in exif:
            return str(exif[key])
    return None


def _aperture(exif: dict[str, Any]) -> str | None:
    for key in ("FNumber", "ApertureValue"):
        if key in exif:
            return str(exif[key])
    return None


def _hour(exif: dict[str, Any]) -> int | None:
    for key in ("DateTimeOriginal", "DateTime"):
        val = exif.get(key)
        if isinstance(val, str) and " " in val and ":" in val:
            try:
                time_part = val.split(" ")[1]
                return int(time_part.split(":")[0])
            except Exception:
                return None
    return None


def build_trend_tips(photos: list[PhotoRecord], lang: str = "zh") -> list[str]:
    if not photos:
        return ["还没有照片数据。先扫描一个文件夹。"] if lang == "zh" else ["No photos yet. Scan a folder first."]

    focals = Counter(f for p in photos if (f := _focal(p.exif)))
    apertures = Counter(a for p in photos if (a := _aperture(p.exif)))
    hours = Counter(h for p in photos if (h := _hour(p.exif)) is not None)
    flagged = sum(1 for p in photos if p.flags)
    scores = sorted((p.score for p in photos), reverse=True)

    tips: list[str] = []
    n = len(photos)

    if focals:
        top_f, cnt = focals.most_common(1)[0]
        pct = round(100 * cnt / n)
        if lang == "zh":
            tips.append(
                f"本批约 {pct}% 照片焦段集中在 {top_f}。刻意换一个焦段拍同一题材，更容易拉开作品差异。"
            )
        else:
            tips.append(f"About {pct}% of this batch uses focal {top_f}. Try another focal length on the same subject.")
    else:
        tips.append(
            "很多文件缺少焦段 EXIF（样例图或导出时被剥离）。保留相机原始元数据，趋势建议会更准。"
            if lang == "zh"
            else "Many files lack focal-length EXIF. Keep original metadata for better trend tips."
        )

    if apertures:
        top_a, cnt = apertures.most_common(1)[0]
        if lang == "zh":
            tips.append(f"光圈多用 {top_a}。人像可试更大光圈练主体分离，风景可试 f/8–f/11 练景深控制。")
        else:
            tips.append(f"Aperture often {top_a}. For portraits try wider; for landscapes try f/8–f/11.")

    if hours:
        top_h, cnt = hours.most_common(1)[0]
        if 10 <= top_h <= 15:
            tips.append(
                f"拍摄高峰在 {top_h}:00 前后（硬光时段）。可多安排日出/日落前后，皮肤与天空层次通常更好。"
                if lang == "zh"
                else f"Peak shooting around {top_h}:00 (harsh light). Golden hour often improves skin and sky."
            )
        else:
            tips.append(
                f"你常在 {top_h}:00 左右拍摄，时段习惯稳定。可以按题材固定「黄金一小时」练习计划。"
                if lang == "zh"
                else f"You often shoot around {top_h}:00. Lock a golden-hour practice plan by subject."
            )

    if flagged:
        pct = round(100 * flagged / n)
        tips.append(
            f"约 {pct}% 照片触发模糊或曝光警告。连拍后先按清晰度筛选，再谈构图，能明显提高成片率。"
            if lang == "zh"
            else f"About {pct}% flagged blur/exposure. Cull for sharpness before composition to raise keeper rate."
        )

    if len(scores) >= 3:
        spread = scores[0] - scores[-1]
        tips.append(
            f"分数跨度约 {spread:.2f}。把最高分的 20% 单独建「可发布」文件夹，长期对比题材成功率。"
            if lang == "zh"
            else f"Score spread ~{spread:.2f}. Keep the top 20% in a publish folder to track subject success."
        )

    return tips[:5]
