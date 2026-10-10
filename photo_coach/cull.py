from __future__ import annotations

import imagehash

from .models import CullGroup, PhotoRecord


def group_near_duplicates(photos: list[PhotoRecord], max_distance: int = 6) -> list[CullGroup]:
    unused = photos[:]
    groups: list[CullGroup] = []
    gid = 0
    while unused:
        seed = unused.pop(0)
        members = [seed]
        seed_hash = imagehash.hex_to_hash(seed.phash)
        rest: list[PhotoRecord] = []
        for p in unused:
            d = seed_hash - imagehash.hex_to_hash(p.phash)
            if d <= max_distance:
                members.append(p)
            else:
                rest.append(p)
        unused = rest
        for m in members:
            m.group_id = gid
        best = max(members, key=lambda m: m.score)
        for m in members:
            m.keep = m.path == best.path or len(members) == 1
        groups.append(
            CullGroup(group_id=gid, members=members, suggested_keep=best.path)
        )
        gid += 1
    return groups
