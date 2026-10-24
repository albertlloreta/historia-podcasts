"""Revisa els llocs de wikidata-cache.json: el país (P17) ha de ser un dels països de l'episodi.

Si no ho és, busca un altre candidat que hi encaixi. Els que no es poden resoldre es marquen
amb 'dubte': true (es mostren igualment al mapa, però es poden revisar a mà).
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('wd', f'{D}/scripts/metadades-wikidata.py')
src = open(f'{D}/scripts/metadades-wikidata.py').read().split('cache = json.load')[0]
ns = {'__file__': f'{D}/scripts/metadades-wikidata.py'}
exec(src, ns)
api = ns['api']
CACHE = f'{D}/metadades/wikidata-cache.json'
cache = json.load(open(CACHE))

paisos = {}
for f in glob.glob(f'{D}/metadades/brut/*.txt'):
    for l in open(f).read().splitlines():
        c = l.split('|')
        if c[4] not in ('', '-'):
            paisos.setdefault(c[4], set()).update(x for x in c[2].split(';') if x not in ('', '-'))

iso = {}


def isos(qids):
    falten = [q for q in qids if q not in iso]
    for i in range(0, len(falten), 50):
        ents = api(action='wbgetentities', ids='|'.join(falten[i:i + 50]), props='claims')['entities']
        for q, e in ents.items():
            v = [c['mainsnak'].get('datavalue', {}).get('value') for c in e.get('claims', {}).get('P297', [])]
            iso[q] = v[0] if v else None
    return [iso.get(q) for q in qids]


def p17(e):
    return [c['mainsnak'].get('datavalue', {}).get('value', {}).get('id') for c in e.get('claims', {}).get('P17', [])]


canvis = dubtes = 0
for nom, ps in sorted(paisos.items()):
    k = f'lloc|{nom}'
    d = cache.get(k)
    if not ps or not d:
        continue
    e = api(action='wbgetentities', ids=d['qid'], props='claims')['entities'][d['qid']]
    if set(isos([q for q in p17(e) if q])) & ps:
        continue
    trobat = None
    for lang in ('ca', 'es', 'en'):
        cands = [x['id'] for x in api(action='wbsearchentities', search=nom, language=lang, uselang='ca',
                                      type='item', limit=15).get('search', [])]
        if not cands:
            continue
        ents = api(action='wbgetentities', ids='|'.join(cands), props='labels|descriptions|claims',
                   languages='ca|es|en')['entities']
        for q in cands:
            e = ents[q]
            c = e.get('claims', {}).get('P625')
            v = c and c[0]['mainsnak'].get('datavalue', {}).get('value')
            if v and set(isos([x for x in p17(e) if x])) & ps:
                lab = next((e['labels'][l]['value'] for l in ('ca', 'es', 'en') if l in e.get('labels', {})), nom)
                desc = next((e['descriptions'][l]['value'] for l in ('ca', 'es', 'en') if l in e.get('descriptions', {})), '')
                trobat = {'qid': q, 'label': lab, 'desc': desc, 'lat': round(v['latitude'], 4), 'lon': round(v['longitude'], 4)}
                break
        if trobat:
            break
    if trobat:
        print('canvi', nom, d['label'], '|', d['desc'][:40], '→', trobat['label'], '|', trobat['desc'][:40])
        cache[k] = trobat
        canvis += 1
    else:
        print('dubte', nom, d['label'], '|', d['desc'][:50], sorted(ps))
        d['dubte'] = True
        dubtes += 1
json.dump(cache, open(CACHE, 'w'), ensure_ascii=False, indent=0)
print('canvis', canvis, 'dubtes', dubtes)
