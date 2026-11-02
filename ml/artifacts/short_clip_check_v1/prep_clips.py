import json, subprocess, sys, shutil, numpy as np, cv2
from pathlib import Path
sys.path.insert(0,'ml/app')
import calorie_pipeline as cp
PICK={'squat':['P-yaD24bUE8','xqvCmoLULNY'],'push_up':['mECzqUIDWfU'],'bicep_curl':['cBSD6mQIPQk','6DeLZ6cbgWQ'],'lateral_raise':['pOmbQuGeHf8','geenhiHju-o'],
 'shoulder_press':['Did01dFR3Lk'],'deadlift':['5WxMW-Fu5KU'],'tricep_extension':['YM8iX9BJWjA'],'dumbbell_row':['cxtcS1zz9Vk'],'lunge':['3TM-vVWuLYE'],
 'sit_up':['pCX65Mtc_Kk'],'jumping_jack':['c4DAnQ6DtF8'],'bench_press':['O7ECGhZj_Hc']}
W=Path('/tmp/shortcheck/work'); W.mkdir(exist_ok=True); rows=[]
for cls,ids in PICK.items():
    for vid in ids:
        raw=W/f'{vid}.mp4'
        subprocess.run(['.venv/bin/yt-dlp','-q','--no-warnings','--no-playlist','-f','bv*[height<=360][ext=mp4]/bv*[height<=360]/b[height<=360]','-o',str(W/f'{vid}.%(ext)s'),f'https://www.youtube.com/watch?v={vid}'],capture_output=True)
        f=next(W.glob(f'{vid}.*'),None)
        if not f: print('download failed',vid); continue
        try:
            pose,rate=cp.extract_pose(f)
        except Exception as e:
            print('pose failed',vid,e); f.unlink(); continue
        np.save(W/f'{vid}.npy',pose)
        cap=cv2.VideoCapture(str(f)); n=int(cap.get(7)); tiles=[]
        for k in range(6):
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(n*(k+0.5)/6)); ok,fr=cap.read()
            if ok: tiles.append(cv2.resize(fr,(213,120)))
        cap.release()
        if tiles: cv2.imwrite(str(W/f'{vid}_frames.jpg'),np.hstack(tiles))
        f.unlink()  # raw video never kept
        rows.append({'cls':cls,'id':vid,'seconds':round(len(pose)/15,1),'detect':round(rate,2)}); print(cls,vid,rows[-1]['seconds'],'s detect',rows[-1]['detect'],flush=True)
json.dump(rows,open('/tmp/shortcheck/prepped.json','w'))
# one contact sheet, label strip per clip
sheets=[]
for r in rows:
    im=cv2.imread(str(W/f"{r['id']}_frames.jpg"))
    if im is None: continue
    bar=np.zeros((22,im.shape[1],3),np.uint8); cv2.putText(bar,f"{r['id']}  claimed: {r['cls']}",(4,15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)
    sheets.append(np.vstack([bar,im]))
for i in range(0,len(sheets),5): cv2.imwrite(f'/tmp/shortcheck/sheet{i//5}.jpg',np.vstack(sheets[i:i+5]))
print('done',len(rows))
