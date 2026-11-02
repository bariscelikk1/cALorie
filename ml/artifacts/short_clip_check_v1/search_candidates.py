import csv, json, subprocess, sys
R='ml/data/long_video_round2_v1/'
bad_ch=set(); bad_names=set(); bad_vid=set()
for r in csv.DictReader(open(R+'exclusions.csv')):
    if r['channel_id']: bad_ch.add(r['channel_id'])
    if r['creator']: bad_names.add(r['creator'].strip().lower())
    if r['video_id']: bad_vid.add(r['video_id'])
for r in csv.DictReader(open(R+'candidates.csv')):
    if r['role'] in ('train','test'): bad_ch.add(r['channel_id']); bad_names.add(r['channel'].strip().lower())
Q={'squat':'bodyweight squat proper form demonstration','push_up':'push up proper form demonstration','bicep_curl':'dumbbell bicep curl form demonstration',
   'lateral_raise':'dumbbell lateral raise form demonstration','shoulder_press':'dumbbell shoulder press form demonstration',
   'deadlift':'romanian deadlift dumbbell form demonstration','tricep_extension':'dumbbell overhead tricep extension form demonstration',
   'dumbbell_row':'single arm dumbbell row form demonstration','lunge':'dumbbell lunge form demonstration','sit_up':'sit up proper form demonstration',
   'pull_up':'pull up proper form demonstration','jumping_jack':'jumping jacks demonstration','bench_press':'dumbbell bench press form demonstration'}
out=[]; seen=set()
for cls,q in Q.items():
    p=subprocess.run(['.venv/bin/yt-dlp','--flat-playlist','--no-warnings','-J',f'ytsearch25:{q}'],capture_output=True,text=True)
    for e in json.loads(p.stdout).get('entries',[]):
        d=e.get('duration') or 0; ch=e.get('channel_id') or ''
        if not (20<=d<=75) or e['id'] in bad_vid or ch in bad_ch or (e.get('channel') or '').strip().lower() in bad_names or ch in seen or not ch: continue
        out.append({'cls':cls,'id':e['id'],'dur':d,'channel':e.get('channel'),'channel_id':ch,'title':e.get('title')}); seen.add(ch)
        if sum(o['cls']==cls for o in out)>=3: break
json.dump(out,open('/tmp/shortcheck/cands.json','w'),indent=1)
for o in out: print(o['cls'],o['id'],int(o['dur']),o['channel'][:22],'|',o['title'][:50])
