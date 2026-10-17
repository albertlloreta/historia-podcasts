#!/usr/bin/env python3
"""Afegeix el camp `ivoox` (id d'episodi iVoox) per reproduir l'àudio des del web.
- Portes de Troia: del feed iVoox complet, per número d'episodi.
- Institut d'Humanitats (format àudio): de l'iframe player_ej_ID de cada pàgina (pauses per evitar 429).
Ús: python3 scripts/ivoox-ids.py [pdt] [ih]"""
import json, re, sys, time, urllib.request, xml.etree.ElementTree as ET

UA = {'User-Agent': 'Mozilla/5.0'}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()

def pdt():
    root = ET.fromstring(get('https://feeds.ivoox.com/feed_fg_f186177_filtro_1.xml'))
    ids = {}
    for it in root.iter('item'):
        n = re.match(r'^(\d+)\s*[-–.]', (it.findtext('title') or '').strip())
        e = it.find('enclosure')
        if n and e is not None:
            ids.setdefault(int(n.group(1)), re.search(r'_mf_(\d+)_', e.get('url')).group(1))
    f = 'episodis-portes-de-troia.json'
    d = json.load(open(f))
    for x in d:
        if x['num'] in ids: x['ivoox'] = ids[x['num']]
    json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2)
    print('PdT:', sum('ivoox' in x for x in d), '/', len(d))

def ih():
    f = 'sessions-institut-humanitats.json'
    d = json.load(open(f))
    todo = [x for x in d if x['format'] == 'audio' and 'ivoox' not in x]
    for i, x in enumerate(todo):
        for intent in range(3):
            try:
                m = re.search(rb'ivoox\.com/player_e[a-z]_(\d+)', get(x['enllac']))
                if m: x['ivoox'] = m.group(1).decode()
                break
            except Exception as e:
                time.sleep(15)
        if i % 20 == 0:
            json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2); print(i, len(todo), flush=True)
        time.sleep(4)
    json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2)
    print('IH:', sum('ivoox' in x for x in d if x['format'] == 'audio'), '/', sum(x['format'] == 'audio' for x in d))

args = sys.argv[1:] or ['pdt', 'ih']
if 'pdt' in args: pdt()
if 'ih' in args: ih()
