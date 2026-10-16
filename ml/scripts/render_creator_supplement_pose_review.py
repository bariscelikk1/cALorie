"""Render supplemental creator pose sheets from archived landmarks, without raw video."""
import argparse, hashlib, io, json, shutil, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

VIDEO_ID = 'phFvFuLUFEw'
EDGES = [(0,5),(0,6),(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),
         (11,12),(11,13),(13,15),(12,14),(14,16)]

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def tile(pose, time_s, detected, center, scale):
    im=Image.new('RGB',(320,180),'white'); d=ImageDraw.Draw(im)
    if np.isfinite(pose[:,:2]).all():
        xy=[((float(p[0])-center[0])*scale+160,(float(p[1])-center[1])*scale+100) for p in pose]
        for a,b in EDGES:
            if pose[a,3]>=.35 and pose[b,3]>=.35: d.line((xy[a],xy[b]),fill='#167ac6',width=3)
        for j,(x,y) in enumerate(xy):
            if pose[j,3]>=.35: d.ellipse((x-3,y-3,x+3,y+3),fill='#df2424')
    d.rectangle((0,0,320,23),fill='#181818')
    d.text((5,5),f'{time_s:.1f}s  {time_s/60:.2f}min  '+('detected' if detected else 'interpolated'),fill='white')
    return im

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--evidence-zip',type=Path,required=True)
    ap.add_argument('--candidates',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    candidates=pd.read_csv(args.candidates)
    assert len(candidates)==4 and set(candidates.video_id)=={VIDEO_ID}
    assert set(candidates.review_status)=={'draft'}
    assert set(candidates.benchmark_ready.astype(str).str.lower())=={'false'}
    if args.output.exists(): shutil.rmtree(args.output)
    pose_root=args.output/'pose_contact_sheets';pose_root.mkdir(parents=True)
    rgb_root=args.output/'coarse_rgb_context';rgb_root.mkdir()
    with zipfile.ZipFile(args.evidence_zip) as z:
        with np.load(io.BytesIO(z.read(f'continuous_landmarks/{VIDEO_ID}.npz')),allow_pickle=False) as data:
            pose=data['landmarks'];times=data['timestamps_s'];detected=data['detected']
            assert pose.shape==(len(times),17,4)
            assert float(data['target_fps'])==15 and times[-1]>candidates.end_s.max()+5
        rgb=pd.read_csv(io.BytesIO(z.read('contact_sheet_index.csv')))
        rgb=rgb[rgb.video_id==VIDEO_ID]
        pages=set()
        for row in candidates.itertuples(index=False):
            for r in rgb.itertuples(index=False):
                if r.first_time_s<=row.end_s+5 and r.last_time_s>=row.start_s-5: pages.add(r.path)
        for path in sorted(pages): (rgb_root/Path(path).name).write_bytes(z.read(path))
    index=[]
    for row in candidates.itertuples(index=False):
        samples=np.arange(max(0,row.start_s-5),row.end_s+5,.5)
        idx=np.clip(np.searchsorted(times,samples),0,len(times)-1)
        prev=np.clip(idx-1,0,len(times)-1)
        idx=np.where(abs(times[prev]-samples)<abs(times[idx]-samples),prev,idx)
        xy=pose[idx,:,:2].reshape(-1,2);xy=xy[np.isfinite(xy).all(axis=1)]
        assert len(xy)>100
        lo,hi=np.percentile(xy,[1,99],axis=0)
        center=(lo+hi)/2
        scale=min(250/max(hi[0]-lo[0],.1),128/max(hi[1]-lo[1],.1))
        dest=pose_root/row.interval_id;dest.mkdir()
        for page in range((len(idx)+11)//12):
            start=page*12;stop=min(start+12,len(idx))
            tiles=[tile(pose[idx[i]],float(times[idx[i]]),bool(detected[idx[i]]),center,scale) for i in range(start,stop)]
            count=len(tiles)
            while len(tiles)<12: tiles.append(Image.new('RGB',(320,180),'white'))
            sheet=Image.new('RGB',(1280,540),'white')
            for j,t in enumerate(tiles): sheet.paste(t,((j%4)*320,(j//4)*180))
            output=dest/f'{page:03d}.jpg';sheet.save(output,quality=86)
            index.append(dict(interval_id=row.interval_id,candidate_class=row.canonical_class,
                              page_index=page,first_s=float(samples[start]),last_s=float(samples[stop-1]),
                              path=str(output.relative_to(args.output))))
    pd.DataFrame(index).to_csv(args.output/'pose_contact_sheet_index.csv',index=False)
    shutil.copy2(args.candidates,args.output/'supplemental_candidates_v1.csv')
    meta=dict(source_id=VIDEO_ID,source_zip_sha256=digest(args.evidence_zip),
              candidates_sha256=digest(args.candidates),sample_fps=2,source_landmark_fps=15,
              coarse_rgb_interval_s=10,labels_locked=False,training_allowed=False,
              calibration_allowed=False,threshold_selection_allowed=False,
              raw_video_included=False,model_predictions_included=False,
              warning='Pose supports motion review but cannot prove equipment or exact RGB boundaries.')
    (args.output/'run_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    (args.output/'README.md').write_text(
        '# Supplemental creator pose review\n\n'
        'These 2 FPS pose sheets come from the previously archived 15 FPS '
        'Michelle Briehler landmarks. Four 10-second RGB storyboard pages are '
        'copied as coarse visual context. No video download, pose re-extraction, '
        'or model inference was performed.\n\n'
        'The bench-press regions visibly repeat supine pressing. The seated '
        'shoulder regions show repeated arm elevation, but their precise '
        'canonical label and boundaries still need independent review. '
        'The candidate CSV remains draft; these sources are external test only.\n'
    )
    checksum_lines=[f'{digest(p)}  {p.relative_to(args.output)}' for p in sorted(args.output.rglob('*')) if p.is_file()]
    (args.output/'SHA256SUMS.txt').write_text('\n'.join(checksum_lines)+'\n')
    print('Pose pages:',len(index),'Coarse RGB pages:',len(pages),'Output:',args.output)

if __name__=='__main__':main()
