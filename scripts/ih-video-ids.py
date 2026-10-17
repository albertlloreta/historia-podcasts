#!/usr/bin/env python3
"""Afegeix `vimeo` o `youtube` (id del vídeo) a les sessions IH de vídeo sense `ivoox`, per incrustar-les al reproductor.
Llegeix l'iframe de cada pàgina de l'IH (pauses de 4 s per evitar 429).
Ús: python3 scripts/ih-video-ids.py"""
import json, re, time, urllib.request

f = 'sessions-institut-humanitats.json'
d = json.load(open(f))
todo = [x for x in d if x['format'] == 'video' and not x.get('ivoox') and not x.get('vimeo') and not x.get('youtube')]
for i, x in enumerate(todo):
    for intent in range(5):
        try:
            h = urllib.request.urlopen(urllib.request.Request(x['enllac'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode()
            m = re.search(r'player\.vimeo\.com/video/(\d+)', h)
            if m: x['vimeo'] = m.group(1)
            m = re.search(r'youtube(?:-nocookie)?\.com/embed/([\w-]{11})', h)
            if m and 'vimeo' not in x: x['youtube'] = m.group(1)
            break
        except Exception as e:
            print(x['nid'], e, flush=True); time.sleep(20 * (intent + 1))
    if i % 20 == 0:
        json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2); print(i, len(todo), flush=True)
    time.sleep(4)
json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2)
v = [x for x in d if x['format'] == 'video']
print('vimeo', sum('vimeo' in x for x in v), 'youtube', sum('youtube' in x for x in v), 'res', sum(not (x.get('ivoox') or x.get('vimeo') or x.get('youtube')) for x in v))
