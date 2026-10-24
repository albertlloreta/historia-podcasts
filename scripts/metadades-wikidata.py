"""Resol personatges, esdeveniments i llocs de metadades/brut/*.txt a Wikidata.

Desa metadades/wikidata-cache.json: {"pers|Nom": {qid, label, desc}, "lloc|Nom": {..., lat, lon}}.
Es pot interrompre i reprendre: només consulta els noms que no són a la caché.
"""
import glob, json, os, sys, time, urllib.parse, urllib.request

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = f'{D}/metadades/wikidata-cache.json'
API = 'https://www.wikidata.org/w/api.php'
UA = {'User-Agent': 'historia.allr.cat metadades (albert.lloreta@gmail.com)'}
COL = {'pers': 6, 'esdev': 7, 'lloc': 4}


def api(**p):
    p.update(format='json')
    url = API + '?' + urllib.parse.urlencode(p)
    for intent in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(2 + 3 * intent)
    raise RuntimeError(url)


def noms():
    out = set()
    for f in glob.glob(f'{D}/metadades/brut/*.txt'):
        for l in open(f).read().splitlines():
            c = l.split('|')
            for tipus, i in COL.items():
                for n in c[i].split(';'):
                    n = n.strip()
                    if n and n != '-':
                        out.add((tipus, n))
    return sorted(out)


def resol(tipus, nom):
    cands = []
    for lang in ('ca', 'es', 'en'):
        r = api(action='wbsearchentities', search=nom, language=lang, uselang='ca', type='item', limit=7)
        cands = [x['id'] for x in r.get('search', [])]
        if cands:
            break
    if not cands:
        return None
    ents = api(action='wbgetentities', ids='|'.join(cands), props='labels|descriptions|claims',
               languages='ca|es|en')['entities']

    def info(q):
        e = ents[q]
        lab = next((e['labels'][l]['value'] for l in ('ca', 'es', 'en') if l in e.get('labels', {})), nom)
        desc = next((e['descriptions'][l]['value'] for l in ('ca', 'es', 'en') if l in e.get('descriptions', {})), '')
        return e, {'qid': q, 'label': lab, 'desc': desc}

    def p31(e):
        return {c['mainsnak'].get('datavalue', {}).get('value', {}).get('id') for c in e.get('claims', {}).get('P31', [])}

    for q in cands:
        e, d = info(q)
        if 'Q4167410' in p31(e):  # pàgina de desambiguació
            continue
        if tipus == 'pers' and 'Q5' not in p31(e):
            continue
        if tipus == 'lloc':
            c = e.get('claims', {}).get('P625')
            if not c:
                continue
            v = c[0]['mainsnak'].get('datavalue', {}).get('value')
            if not v:
                continue
            d.update(lat=round(v['latitude'], 4), lon=round(v['longitude'], 4))
        return d
    if tipus == 'pers':  # personatges mítics o bíblics: el primer que no sigui desambiguació
        for q in cands:
            e, d = info(q)
            if 'Q4167410' not in p31(e):
                d['no_huma'] = True
                return d
    return None


cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
pendents = [(t, n) for t, n in noms() if f'{t}|{n}' not in cache]
print(len(pendents), 'pendents de', len(noms()), flush=True)
for i, (t, n) in enumerate(pendents, 1):
    try:
        cache[f'{t}|{n}'] = resol(t, n)
    except Exception as e:
        print('error', t, n, e, flush=True)
        continue
    if i % 50 == 0:
        json.dump(cache, open(CACHE, 'w'), ensure_ascii=False, indent=0)
        print(i, flush=True)
    time.sleep(0.1)
json.dump(cache, open(CACHE, 'w'), ensure_ascii=False, indent=0)
print('fet', sum(v is None for v in cache.values()), 'sense resoldre')
