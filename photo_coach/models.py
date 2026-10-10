from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class PhotoRecord:
    path: str
    filename: str
    exif: dict[str, Any] = field(default_factory=dict)
    sharpness: float = 0.0
    exposure: float = 0.0
    score: float = 0.0
    flags: list[str] = field(default_factory=list)
    phash: str = ""
    group_id: int | None = None
    keep: bool = True
    keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CullGroup:
    group_id: int
    members: list[PhotoRecord]
    suggested_keep: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "group_id": self.group_id,
            "suggested_keep": self.suggested_keep,
            "members": [m.to_dict() for m in self.members],
        }
