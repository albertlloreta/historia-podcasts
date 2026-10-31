"""Baixa de Wikidata els noms alternatius de cada personatge, esdeveniment i lloc (per QID)
i desa alies.json: {"Q215646": ["Yedo", "Tòquio", ...], ...}. Ho fan servir els cercadors
(cerca.js) perquè «Tòquio» trobi Edo o «Bizanci» trobi Constantinoble.

Inclou les etiquetes i àlies en ca/es/en/fr/it i, per als llocs, els noms del lloc que
el substitueix o al qual substitueix (P1365, P1366) i dels que es diu que són el mateix (P460).
Es pot interrompre i reprendre: guarda les respostes a metadades/wikidata-alies-cache.json.
"""
import glob, json, os, time, unicodedata, urllib.parse, urllib.request

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = f'{D}/metadades/wikidata-alies-cache.json'
API = 'https://www.wikidata.org/w/api.php'
UA = {'User-Agent': 'historia.allr.cat alies (albert.lloreta@gmail.com)'}
LLENGUES = ['ca', 'es', 'en', 'fr', 'it']
VINCLES = ['P1365', 'P1366', 'P460']
MAX = 15


def norm(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn').lower()


def get(ids, props):
    q = urllib.parse.urlencode({'action': 'wbgetentities', 'ids': '|'.join(ids), 'props': props,
                                'languages': '|'.join(LLENGUES), 'format': 'json'})
    for intent in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(f'{API}?{q}', headers=UA), timeout=60) as r:
                return json.load(r).get('entities', {})
        except Exception as e:
            print('  reintent', intent, e)
            time.sleep(5 * (intent + 1))
    raise SystemExit('Wikidata no respon')


def main():
    qids, llocs = set(), set()
    for f in glob.glob(f'{D}/episodis-*.json') + glob.glob(f'{D}/sessions-*.json'):
        for e in json.load(open(f)):
            for p in (e.get('personatges') or []) + (e.get('esdeveniments') or []):
                if p.get('qid'): qids.add(p['qid'])
            if (e.get('lloc') or {}).get('qid'):
                qids.add(e['lloc']['qid']); llocs.add(e['lloc']['qid'])

    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    falten = sorted(q for q in qids if q not in cache)
    print(f'{len(qids)} QID, en falten {len(falten)}')
    for i in range(0, len(falten), 50):
        lot = falten[i:i + 50]
        for q, ent in get(lot, 'labels|aliases|claims').items():
            noms = [v['value'] for v in ent.get('labels', {}).values()]
            noms += [a['value'] for l in ent.get('aliases', {}).values() for a in l]
            vincles = [c['mainsnak']['datavalue']['value']['id'] for p in VINCLES
                       for c in ent.get('claims', {}).get(p, []) if c['mainsnak'].get('datavalue')]
            cache[q] = {'noms': noms, 'vincles': vincles}
        json.dump(cache, open(CACHE, 'w'), ensure_ascii=False)
        print(f'  {min(i + 50, len(falten))}/{len(falten)}')
        time.sleep(1)

    # Noms dels llocs vinculats (només per als llocs: Edo → Tòquio)
    vinc = sorted({v for q in llocs if q in cache for v in cache[q]['vincles']} - set(cache))
    for i in range(0, len(vinc), 50):
        for q, ent in get(vinc[i:i + 50], 'labels').items():
            cache[q] = {'noms': [v['value'] for v in ent.get('labels', {}).values()], 'vincles': []}
        time.sleep(1)
    json.dump(cache, open(CACHE, 'w'), ensure_ascii=False)

    out = {}
    for q in sorted(qids, key=lambda x: int(x[1:])):
        c = cache.get(q)
        if not c: continue
        noms = list(c['noms'])
        if q in llocs:
            for v in c['vincles']: noms += cache.get(v, {}).get('noms', [])
        vist, res = set(), []
        for n in noms:
            k = norm(n).strip()
            if not k or len(k) > 60 or k in vist: continue
            vist.add(k); res.append(n)
        if res: out[q] = res[:MAX]
    json.dump(out, open(f'{D}/alies.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f'alies.json: {len(out)} QID, {sum(map(len, out.values()))} noms')


if __name__ == '__main__':
    main()
