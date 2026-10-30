#!/usr/bin/env python3
"""Role groups for RepCount-A intake v2 (locked 2026-10-27 after the full-set gray-zone check).

Scene groups (cosine >= 0.85) are merged further for split assignment:
- gray-zone pairs >= 0.84 merge (eye-check: about 7 of 8 sampled were the same source);
- pairs confirmed by eye as the same source merge regardless of score;
- a group with any remaining 0.78-0.84 link to another group is barred from the
  sealed test (about 1 in 8 sampled pairs there was still the same source).
"""

from __future__ import annotations

import argparse
import collections
from pathlib import Path

import pandas as pd

ROLE_MERGE = 0.84
CONFIRMED_SAME_SOURCE = [  # seen by eye during review and the gray-zone check
    ("stu1_53", "stu7_53"), ("stu4_38", "stu5_40"), ("stu7_70", "stu9_66"), ("stu11_24", "stu12_21"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_groups_csv", type=Path)
    parser.add_argument("gray_zone_csv", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    scene = dict(pd.read_csv(args.scene_groups_csv)[["video_id", "scene_group"]].itertuples(index=False))
    gray = pd.read_csv(args.gray_zone_csv)
    parent = {g: g for g in set(scene.values())}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for row in gray[gray.similarity >= ROLE_MERGE].itertuples(index=False):
        parent[find(scene[row.video_a])] = find(scene[row.video_b])
    for a, b in CONFIRMED_SAME_SOURCE:
        parent[find(scene[a])] = find(scene[b])
    roots = {}
    root_of = {v: find(g) for v, g in scene.items()}
    names = {r: f"role_group_{i:04d}" for i, r in enumerate(sorted(set(root_of.values())))}
    barred = set()
    for row in gray.itertuples(index=False):
        a, b = root_of[row.video_a], root_of[row.video_b]
        if a != b:
            barred.update((a, b))
    out = pd.DataFrame([{"video_id": v, "scene_group": scene[v], "role_group": names[root_of[v]],
                         "sealed_test_eligible": root_of[v] not in barred} for v in sorted(scene)])
    out.to_csv(args.output, index=False)
    sizes = collections.Counter(out.role_group)
    print(f"{len(out)} clips -> {len(sizes)} role groups (largest {max(sizes.values())}); "
          f"sealed-test eligible clips: {int(out.sealed_test_eligible.sum())}")


if __name__ == "__main__":
    main()
