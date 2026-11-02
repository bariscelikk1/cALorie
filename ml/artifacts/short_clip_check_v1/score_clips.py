import json, sys, numpy as np, pandas as pd, torch, collections
sys.path.insert(0,'ml/app')
import calorie_pipeline as cp
rows=json.load(open('/tmp/shortcheck/prepped.json'))
EXCLUDE={'mECzqUIDWfU':'animated cartoon, not a real person'}
FLAG={'P-yaD24bUE8':'two people, mostly talking','cBSD6mQIPQk':'two people, demo with talking','pCX65Mtc_Kk':'two people, mostly talking'}
dev='mps' if torch.backends.mps.is_available() else 'cpu'
models=cp.load_final_model(torch.device(dev)); out=[]
for r in rows:
    if r['id'] in EXCLUDE: continue
    pose=np.load(f"/tmp/shortcheck/work/{r['id']}.npy"); tl=cp.timeline(pose,dev,models)
    dur=collections.Counter()
    for t in tl.itertuples(): dur[t.label]+=t.end_s-t.start_s
    total=sum(dur.values()); sup={k:v for k,v in dur.items() if k!='unknown'}
    top=max(sup,key=sup.get) if sup else 'unknown'
    out.append({'id':r['id'],'truth':r['cls'],'top_label':top,'clip_correct':top==r['cls'],'seconds':round(total,1),
                'share_correct':round(dur[r['cls']]/total,2),'share_unknown':round(dur['unknown']/total,2),
                'share_other_exercise':round((total-dur['unknown']-dur[r['cls']])/total,2),'note':FLAG.get(r['id'],'')})
df=pd.DataFrame(out); df.to_csv('/tmp/shortcheck/results.csv',index=False)
pd.set_option('display.width',200); print(df.to_string(index=False))
print('\nclips:',len(df),'| clip-level correct:',int(df.clip_correct.sum()),f"= {df.clip_correct.mean():.0%}")
clean=df[df.note=='']; print('without flagged clips:',len(clean),'| correct:',int(clean.clip_correct.sum()),f"= {clean.clip_correct.mean():.0%}")
print('mean time share labeled correct:',f"{df.share_correct.mean():.0%}",'| unknown:',f"{df.share_unknown.mean():.0%}")
