"""Run Notebook 29F pose cell locally against preserved 360p source videos.

Requires mediapipe==0.10.35, OpenCV, pandas, numpy, and ffmpeg on PATH.
Raw videos stay outside Git; the output ZIP contains only landmarks, overlays,
quality metadata, and pinned draft locators. Never treat it as training data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def run(args: list[str], timeout: int = 300) -> tuple[int, str]:
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=timeout, check=False)
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired as exc:
        return 124, str(exc)


def info(path: Path) -> dict[str, float] | None:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return None
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    cap.release()
    if fps <= 0 or frames <= 0:
        return None
    return {'duration_s': frames / fps, 'height': height, 'fps': fps}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video-root', required=True, type=Path)
    parser.add_argument('--output-root', required=True, type=Path)
    parser.add_argument('--work-root', required=True, type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    triage_path = repo / 'ml/data/source_balance_v1/dense_visual_first_pass.csv'
    candidate_path = repo / 'ml/data/source_balance_v1/candidates.csv'
    assert sha256(triage_path) == '6a9fccdb444edec48287d713832aee8c87a524a693696d0796d5f7b2e9fa71bd'
    triage = pd.read_csv(triage_path).fillna('')
    assert (triage.review_status == 'draft').all() and (~triage.training_allowed).all()
    selected = triage[triage.first_pass_status.isin(['pose_review', 'second_review'])]
    rows = []
    for row in selected.itertuples(index=False):
        for number, pair in enumerate(row.approx_candidate_windows_s.split('|'), 1):
            start, end = map(float, pair.split('-'))
            assert float(row.source_start_s) <= start < end <= float(row.source_end_s)
            rows.append({'window_id': f'{row.review_id}_{number:02d}', 'review_id': row.review_id,
                         'video_id': row.video_id, 'target_hypothesis': row.target_hypothesis,
                         'start_s': start, 'end_s': end,
                         'first_pass_status': row.first_pass_status})
    windows = pd.DataFrame(rows)
    assert len(windows) == 17 and windows.window_id.is_unique
    source_paths = {}
    source_status = []
    video_hashes = []
    for video_id in sorted(set(windows.video_id)):
        path = args.video_root / f'{video_id}.mp4'
        probe = info(path) if path.exists() else None
        record = {'video_id': video_id, 'status': 'ready' if probe and probe['height'] == 360 else 'unavailable',
                  'error': '' if probe and probe['height'] == 360 else 'Missing or invalid local 360p video'}
        if record['status'] == 'ready':
            source_paths[video_id] = path
            video_hashes.append({'video_id': video_id, 'sha256': sha256(path),
                                 'bytes': path.stat().st_size, 'fps': probe['fps'],
                                 'duration_s': probe['duration_s']})
        source_status.append(record)
    if args.output_root.exists():
        shutil.rmtree(args.output_root)
    for folder in (args.output_root, args.output_root / 'continuous_landmarks',
                   args.output_root / 'pose_contact_sheets', args.work_root,
                   args.work_root / 'pose_segments'):
        folder.mkdir(parents=True, exist_ok=True)
    namespace = {'WORK': args.work_root, 'OUTPUT': args.output_root, 'windows': windows,
                 'source_paths': source_paths, 'source_status': source_status,
                 'run': run, 'info': info, 'sha256': sha256, 'cv2': cv2, 'mp': mp,
                 'np': np, 'pd': pd, 'Path': Path, 'urllib': __import__('urllib'),
                 'display': lambda frame: print(frame.to_string(index=False))}
    import urllib.request
    namespace['urllib'] = urllib
    notebook = json.loads((repo / 'ml/notebooks/29f_colab_audit_source_balance_pose_candidates.ipynb').read_text())
    pose_cell = ''.join(notebook['cells'][4]['source'])
    exec(compile(pose_cell, '29f_pose_cell', 'exec'), namespace)
    quality = namespace['quality']
    shutil.copy2(triage_path, args.output_root / triage_path.name)
    shutil.copy2(candidate_path, args.output_root / candidate_path.name)
    windows.to_csv(args.output_root / 'candidate_windows.csv', index=False)
    pd.DataFrame(video_hashes).to_csv(args.output_root / 'local_source_sha256.csv', index=False)
    metadata = {'notebook': '29f_colab_audit_source_balance_pose_candidates.ipynb',
                'execution': 'local_cpu_fallback', 'runtime': 'CPU',
                'pinned_triage_sha256': sha256(triage_path), 'target_fps': 15,
                'window_count': len(windows), 'pose_ready': int((quality.status == 'pose_ready').sum()),
                'training_allowed': False, 'review_status': 'draft',
                'raw_video_exported': False}
    (args.output_root / 'run_metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    checks = []
    for path in sorted(p for p in args.output_root.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt'):
        checks.append(f'{sha256(path)}  {path.relative_to(args.output_root)}')
    (args.output_root / 'SHA256SUMS.txt').write_text('\n'.join(checks) + '\n')
    assert not list(args.output_root.rglob('*.mp4'))
    archive = shutil.make_archive(str(args.output_root), 'zip', args.output_root)
    print('Created', archive, 'sha256', sha256(Path(archive)))


if __name__ == '__main__':
    main()
