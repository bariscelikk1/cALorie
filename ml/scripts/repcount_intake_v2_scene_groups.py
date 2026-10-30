#!/usr/bin/env python3
"""Scene-based source groups for RepCount-A intake v2 (locked 2026-10-25)."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torchvision
from torchvision.io import read_image


MERGE_THRESHOLD = 0.85  # known v1 duplicates: 0.929 and 0.987; closest distinct pilot pair: 0.794
GRAY_ZONE = (0.78, 0.90)  # pairs here need a visual check in the full intake
THUMBNAILS_PER_CLIP = 3


def embed(scene_dirs: list[Path]) -> tuple[list[str], np.ndarray]:
    """Frozen ImageNet ResNet-50; each clip is the normalized mean of its 3 thumbnail embeddings."""
    weights = torchvision.models.ResNet50_Weights.IMAGENET1K_V2
    model = torchvision.models.resnet50(weights=weights)
    model.fc = torch.nn.Identity()
    model.eval()
    prep = weights.transforms()
    folder = {path.name.rsplit("_", 1)[0]: d for d in scene_dirs for path in d.glob("*.jpg")}
    ids = sorted(folder)
    vectors = []
    with torch.no_grad():
        for video_id in ids:
            images = torch.stack([prep(read_image(str(folder[video_id] / f"{video_id}_{i}.jpg"))) for i in range(THUMBNAILS_PER_CLIP)])
            e = model(images)
            e = e / e.norm(dim=1, keepdim=True)
            mean = e.mean(0)
            vectors.append((mean / mean.norm()).numpy())
    return ids, np.stack(vectors)


def groups(ids: list[str], vectors: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    similarity = vectors @ vectors.T
    parent = list(range(len(ids)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    pairs = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            s = float(similarity[i, j])
            if s >= MERGE_THRESHOLD:
                parent[find(i)] = find(j)
            if GRAY_ZONE[0] <= s < GRAY_ZONE[1]:
                pairs.append({"video_a": ids[i], "video_b": ids[j], "similarity": round(s, 4)})
    roots = {}
    assignment = []
    for i, video_id in enumerate(ids):
        root = find(i)
        roots.setdefault(root, f"scene_{len(roots):04d}")
        assignment.append({"video_id": video_id, "scene_group": roots[root]})
    return pd.DataFrame(assignment), pd.DataFrame(pairs, columns=["video_a", "video_b", "similarity"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("groups_csv", type=Path)
    parser.add_argument("gray_zone_csv", type=Path)
    parser.add_argument("scene_dirs", type=Path, nargs="+", help="report/scene directories of thumbnails")
    args = parser.parse_args()
    ids, vectors = embed(args.scene_dirs)
    assignment, gray = groups(ids, vectors)
    assignment.to_csv(args.groups_csv, index=False)
    gray.sort_values("similarity", ascending=False).to_csv(args.gray_zone_csv, index=False)
    sizes = assignment.scene_group.value_counts()
    print(f"{len(ids)} clips -> {len(sizes)} groups; multi-clip groups: {int((sizes > 1).sum())}; gray-zone pairs: {len(gray)}")


if __name__ == "__main__":
    main()
